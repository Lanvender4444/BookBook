"""LanceDB 向量库后端（替代 Milvus）。

为什么用 LanceDB：
- **嵌入式、单目录文件**，无需独立服务进程（不像 Milvus 要起容器）；
- **全平台 pip wheel**（Windows / macOS / Linux），PyInstaller 友好；
- **原生同时支持向量检索 + 全文 BM25（Tantivy）+ 内置混合重排（RRF）**——
  正好把「BM25 与 vector」都交给同一个专门的向量库完成，不必再手写。

一张表 `chunks`：
    id        int64   主键（= KnowledgeChunk.id，用于映射回 SQLite 取元数据）
    source_id string  归属知识源（检索范围过滤）
    text      string  原文（建 FTS / BM25 索引）
    vector    float32[dim]  向量（建向量索引）；dim 由首批写入决定，变化则重建表

对外暴露：available / upsert / delete_by_source / hybrid_search / fts_search / search。
任何不可用（未装 lancedb、版本 API 不符、建索引失败）都安全返回空/False，
调用方（rag_service）据此回落到「纯 Python BM25 + 暴力余弦 + RRF」，功能不中断。
"""

import threading

TABLE = "chunks"

_db = None
_lock = threading.RLock()
_dim = None  # 当前表的向量维度


def _conn():
    global _db
    if _db is not None:
        return _db
    with _lock:
        if _db is not None:
            return _db
        try:
            import lancedb
            from utils import get_app_data_dir

            path = str(get_app_data_dir() / "lancedb")
            _db = lancedb.connect(path)
            print(f"[LanceDB] connected: {path}")
        except Exception as e:
            print(f"[LanceDB] unavailable, fallback to pure-python: {e}")
            _db = None
        return _db


def available() -> bool:
    return _conn() is not None


def _schema(dim: int):
    import pyarrow as pa

    return pa.schema([
        pa.field("id", pa.int64()),
        pa.field("source_id", pa.string()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), dim)),
    ])


def _ensure_table(dim: int):
    """确保表存在且维度匹配；维度变化则重建（清空旧向量，需重新索引全部知识源）。"""
    global _dim
    db = _conn()
    if db is None:
        return None
    try:
        names = db.table_names()
        if TABLE in names:
            tbl = db.open_table(TABLE)
            cur = _vector_dim(tbl)
            if cur is not None and cur != dim:
                print(f"[LanceDB] embedding dim {cur} -> {dim}, recreating table")
                db.drop_table(TABLE)
                tbl = db.create_table(TABLE, schema=_schema(dim))
            _dim = dim
            return tbl
        tbl = db.create_table(TABLE, schema=_schema(dim))
        _dim = dim
        return tbl
    except Exception as e:
        print(f"[LanceDB] ensure_table failed: {e}")
        return None


def _vector_dim(tbl):
    try:
        f = tbl.schema.field("vector")
        return f.type.list_size  # fixed_size_list 的维度
    except Exception:
        return None


def _rebuild_fts(tbl):
    """（重）建全文/BM25 索引。CJK 用 ngram 分词以提升中文召回；失败回退默认分词。"""
    try:
        tbl.create_fts_index("text", replace=True, use_tantivy=False, tokenizer_name="ngram")
    except Exception:
        try:
            tbl.create_fts_index("text", replace=True)
        except Exception as e:
            print(f"[LanceDB] create_fts_index failed: {e}")


def upsert(rows: list[dict]) -> bool:
    """写入/更新分块。rows = [{'id': int, 'source_id': str, 'text': str, 'vector': list[float]}]。"""
    if not rows:
        return True
    dim = len(rows[0]["vector"])
    with _lock:
        tbl = _ensure_table(dim)
        if tbl is None:
            return False
        try:
            ids = [int(r["id"]) for r in rows]
            # 先删同 id（实现 upsert 语义），再插
            tbl.delete(f"id IN ({','.join(map(str, ids))})")
            tbl.add([
                {"id": int(r["id"]), "source_id": str(r["source_id"]),
                 "text": r.get("text", ""), "vector": list(r["vector"])}
                for r in rows
            ])
            _rebuild_fts(tbl)
            return True
        except Exception as e:
            print(f"[LanceDB] upsert failed: {e}")
            return False


def delete_by_source(source_id: str) -> None:
    db = _conn()
    if db is None:
        return
    try:
        if TABLE in db.table_names():
            tbl = db.open_table(TABLE)
            tbl.delete(f"source_id = '{source_id}'")
            _rebuild_fts(tbl)
    except Exception as e:
        print(f"[LanceDB] delete_by_source failed: {e}")


def _src_filter(source_ids: list[str]) -> str:
    quoted = ", ".join("'" + s.replace("'", "''") + "'" for s in source_ids)
    return f"source_id IN ({quoted})"


def _open():
    db = _conn()
    if db is None:
        return None
    try:
        if TABLE not in db.table_names():
            return None
        return db.open_table(TABLE)
    except Exception:
        return None


def _score_of(row) -> float:
    for k in ("_relevance_score", "_score", "_distance"):
        if k in row and row[k] is not None:
            v = float(row[k])
            return (1.0 - v) if k == "_distance" else v  # 距离越小越相似 → 转相似度
    return 0.0


def hybrid_search(query_text: str, query_vec: list[float], source_ids: list[str],
                  top_k: int = 5) -> list[tuple[int, float]]:
    """混合检索：BM25(全文) + 向量，LanceDB 内置 RRF 重排。返回 [(chunk_id, score)] best-first。"""
    tbl = _open()
    if tbl is None or not source_ids:
        return []
    try:
        from lancedb.rerankers import RRFReranker
        reranker = RRFReranker()
    except Exception:
        reranker = None
    try:
        q = tbl.search(query_type="hybrid").text(query_text).vector(query_vec)
        try:
            q = q.where(_src_filter(source_ids), prefilter=True)
        except TypeError:
            q = q.where(_src_filter(source_ids))
        if reranker is not None:
            q = q.rerank(reranker)
        rows = q.limit(top_k).to_list()
        return [(int(r["id"]), _score_of(r)) for r in rows]
    except Exception as e:
        print(f"[LanceDB] hybrid_search failed: {e}")
        # 退化：纯向量
        return search(query_vec, source_ids, top_k)


def fts_search(query_text: str, source_ids: list[str], top_k: int = 5) -> list[tuple[int, float]]:
    """纯全文 BM25 检索（无 embedding 能力时用）。返回 [(chunk_id, score)]。"""
    tbl = _open()
    if tbl is None or not source_ids or not query_text.strip():
        return []
    try:
        q = tbl.search(query_text, query_type="fts")
        try:
            q = q.where(_src_filter(source_ids), prefilter=True)
        except TypeError:
            q = q.where(_src_filter(source_ids))
        rows = q.limit(top_k).to_list()
        return [(int(r["id"]), _score_of(r)) for r in rows]
    except Exception as e:
        print(f"[LanceDB] fts_search failed: {e}")
        return []


def search(query_vec: list[float], source_ids: list[str], top_k: int = 5) -> list[tuple[int, float]]:
    """纯向量检索（兼容旧调用）。返回 [(chunk_id, similarity)]。"""
    tbl = _open()
    if tbl is None or not source_ids:
        return []
    try:
        q = tbl.search(query_vec)
        try:
            q = q.where(_src_filter(source_ids), prefilter=True)
        except TypeError:
            q = q.where(_src_filter(source_ids))
        rows = q.metric("cosine").limit(top_k).to_list()
        return [(int(r["id"]), _score_of(r)) for r in rows]
    except Exception as e:
        print(f"[LanceDB] search failed: {e}")
        return []
