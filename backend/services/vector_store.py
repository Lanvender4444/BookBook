"""Milvus 向量存储后端。

替代原先「SQLite BLOB + 纯 Python 暴力余弦」的向量检索：
- 向量、主键、source_id 存进 Milvus，相似检索交给 Milvus 索引；
- 默认使用 **Milvus Lite**（嵌入式、本地单文件，无需独立服务；仅 Linux/macOS 官方支持）；
- 通过 `config.MILVUS_URI` 可指向 Milvus 服务（如 http://localhost:19530），用于 Windows / 共享部署。

对外只暴露 4 个函数：available / upsert / search / delete_by_source。
任何不可用情况（未装 pymilvus、连接失败、维度冲突）都安全返回，调用方（rag_service）据此
自动回落到 SQLite 暴力检索 / BM25，保证功能不中断。

集合 schema：
    id        INT64        主键（= KnowledgeChunk.id）
    source_id VARCHAR(64)  归属知识源，用于检索范围过滤
    vector    FLOAT_VECTOR 维度由首个写入向量决定；维度变化会重建集合（需重新索引）
索引：AUTOINDEX + COSINE。
"""

import json
import threading
import time

from config import MILVUS_URI

COLLECTION = "knowledge_vectors"

# 连接重试间隔：Milvus 容器自动拉起需要时间，连接失败后每隔一段时间重试一次，
# 这样 Milvus 就绪后下一次检索/索引就能自动接上，而不是整会话卡在降级。
_RETRY_INTERVAL = 15.0

_client = None
_last_try = 0.0
_lock = threading.Lock()


def _get_client():
    """惰性单例 + 限频重试。已连上则直接复用；未连上则每 _RETRY_INTERVAL 秒重试一次。"""
    global _client, _last_try
    if _client is not None:
        return _client
    now = time.time()
    if now - _last_try < _RETRY_INTERVAL:
        return None
    with _lock:
        if _client is not None:
            return _client
        if time.time() - _last_try < _RETRY_INTERVAL:
            return None
        _last_try = time.time()
        try:
            from pymilvus import MilvusClient

            _client = MilvusClient(MILVUS_URI)
            print(f"[Milvus] connected: {MILVUS_URI}")
        except Exception as e:
            print(f"[Milvus] unavailable (will retry in {int(_RETRY_INTERVAL)}s), fallback for now: {e}")
            _client = None
        return _client


def available() -> bool:
    return _get_client() is not None


def _current_dim(client):
    """返回当前集合的向量维度；集合不存在返回 None。"""
    try:
        if not client.has_collection(COLLECTION):
            return None
        for f in client.describe_collection(COLLECTION)["fields"]:
            if f["name"] == "vector":
                return f.get("params", {}).get("dim")
    except Exception:
        return None
    return None


def _ensure_collection(client, dim: int) -> bool:
    """确保集合存在且维度匹配；维度变化则重建（会清空旧向量，需重新索引）。"""
    cur = _current_dim(client)
    if cur == dim:
        return True
    try:
        from pymilvus import MilvusClient, DataType

        if cur is not None and cur != dim:
            print(f"[Milvus] embedding dim changed {cur} -> {dim}, recreating collection")
            client.drop_collection(COLLECTION)

        schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("source_id", DataType.VARCHAR, max_length=64)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=dim)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector", index_type="AUTOINDEX", metric_type="COSINE"
        )
        client.create_collection(COLLECTION, schema=schema, index_params=index_params)
        return True
    except Exception as e:
        print(f"[Milvus] ensure_collection failed: {e}")
        return False


def upsert(rows: list[dict]) -> bool:
    """写入/更新向量。rows = [{'id': int, 'source_id': str, 'vector': list[float]}]。"""
    if not rows:
        return True
    client = _get_client()
    if client is None:
        return False
    dim = len(rows[0]["vector"])
    if not _ensure_collection(client, dim):
        return False
    try:
        client.upsert(COLLECTION, rows)
        return True
    except Exception:
        # 个别版本无 upsert：退回 delete + insert
        try:
            client.delete(COLLECTION, ids=[r["id"] for r in rows])
            client.insert(COLLECTION, rows)
            return True
        except Exception as e:
            print(f"[Milvus] upsert failed: {e}")
            return False


def delete_by_source(source_id: str) -> None:
    """删除某知识源的全部向量（重建索引前先清旧）。"""
    client = _get_client()
    if client is None:
        return
    try:
        if client.has_collection(COLLECTION):
            client.delete(COLLECTION, filter=f'source_id == "{source_id}"')
    except Exception as e:
        print(f"[Milvus] delete_by_source failed: {e}")


def search(query_vec: list[float], source_ids: list[str], top_k: int = 5) -> list[tuple[int, float]]:
    """在指定 source 范围内向量检索，返回 [(chunk_id, similarity), ...]（best-first）。
    不可用 / 无集合 / 无命中返回 []。
    """
    client = _get_client()
    if client is None or not source_ids:
        return []
    try:
        if not client.has_collection(COLLECTION):
            return []
        flt = f"source_id in {json.dumps(source_ids)}"
        res = client.search(
            COLLECTION,
            data=[query_vec],
            limit=top_k,
            filter=flt,
            output_fields=["source_id"],
        )
        hits = res[0] if res else []
        # Milvus Lite 的 COSINE 返回 distance = 1 - cos（越小越相似），统一转成相似度
        return [(h["id"], 1.0 - float(h["distance"])) for h in hits]
    except Exception as e:
        print(f"[Milvus] search failed: {e}")
        return []
