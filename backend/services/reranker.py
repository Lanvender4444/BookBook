"""Cross-encoder 精排（rerank 第三级）。

检索链路：召回（BM25 + 向量）→ RRF 融合 → **本模块 cross-encoder 精排**。
cross-encoder 把 (query, chunk) 拼在一起联合编码打分（比双塔向量更准，但更慢），
所以只对 RRF 融合后的少量候选做精排。

两档实现（本地优先级低，避免强依赖 torch）：
  A. **rerank API**（默认推荐）：Jina / Cohere / SiliconFlow / Voyage 的 rerank 接口，
     本质就是托管的 cross-encoder，多语言（含中文），只需 httpx，无本地大模型。
  B. **本地 cross-encoder**：装了 sentence-transformers 时用本地模型（如 bge-reranker）。
  C. 都没配 → available()=False，检索层直接用 RRF 结果，不做精排。

配置存 AppSetting（复用 agent_tools 的 get_setting/set_setting）：
  rerank_provider ∈ {jina, cohere, siliconflow, voyage, local, ""}
  rerank_api_key
  rerank_model（留空用各家默认多语言模型）
"""

import httpx

from services.agent_tools import get_setting

RERANK_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

# 各 provider 的默认多语言 rerank 模型
_DEFAULT_MODEL = {
    "jina": "jina-reranker-v2-base-multilingual",
    "cohere": "rerank-multilingual-v3.0",
    "siliconflow": "BAAI/bge-reranker-v2-m3",
    "voyage": "rerank-2",
    "local": "BAAI/bge-reranker-base",
}

_ENDPOINT = {
    "jina": "https://api.jina.ai/v1/rerank",
    "cohere": "https://api.cohere.com/v1/rerank",
    "siliconflow": "https://api.siliconflow.cn/v1/rerank",
    "voyage": "https://api.voyageai.com/v1/rerank",
}


def _provider() -> str:
    return (get_setting("rerank_provider", "") or "").lower().strip()


def _model(provider: str) -> str:
    return get_setting("rerank_model", "") or _DEFAULT_MODEL.get(provider, "")


def available() -> bool:
    p = _provider()
    if not p:
        return False
    if p == "local":
        try:
            import sentence_transformers  # noqa: F401
            return True
        except Exception:
            return False
    return bool(get_setting("rerank_api_key", ""))


# ---------------------------------------------------------------- 打分

def _scores_api(provider: str, query: str, docs: list[str]) -> list[float]:
    """调 rerank API，返回与 docs 顺序对齐的分数列表。"""
    api_key = get_setting("rerank_api_key", "")
    model = _model(provider)
    url = _ENDPOINT[provider]
    payload = {"model": model, "query": query, "documents": docs, "top_n": len(docs)}
    with httpx.Client(timeout=RERANK_TIMEOUT) as c:
        resp = c.post(url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload)
        resp.raise_for_status()
        data = resp.json()
    # 兼容 Cohere/Jina/SiliconFlow 的 "results" 与 Voyage 的 "data"
    items = data.get("results") or data.get("data") or []
    scores = [0.0] * len(docs)
    for it in items:
        idx = it.get("index")
        sc = it.get("relevance_score", it.get("score", 0.0))
        if isinstance(idx, int) and 0 <= idx < len(docs):
            scores[idx] = float(sc)
    return scores


_local_model = None


def _scores_local(query: str, docs: list[str]) -> list[float]:
    global _local_model
    from sentence_transformers import CrossEncoder

    if _local_model is None:
        _local_model = CrossEncoder(_model("local"))
    pairs = [(query, d) for d in docs]
    return [float(s) for s in _local_model.predict(pairs)]


# ---------------------------------------------------------------- 精排入口

def rerank(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    """对候选做 cross-encoder 精排，返回重排后的前 top_k。

    candidates: retrieve 产出的结果字典列表，每项含 "text"。
    失败 / 不可用时原样返回前 top_k（不影响主流程）。
    """
    if not candidates:
        return []
    if not available():
        return candidates[:top_k]

    provider = _provider()
    docs = [c.get("text", "") for c in candidates]
    try:
        if provider == "local":
            scores = _scores_local(query, docs)
        else:
            scores = _scores_api(provider, query, docs)
    except Exception as e:
        print(f"[rerank] cross-encoder failed, keep RRF order: {e}")
        return candidates[:top_k]

    order = sorted(range(len(candidates)), key=lambda i: scores[i], reverse=True)[:top_k]
    out = []
    for i in order:
        c = dict(candidates[i])
        c["rerank_score"] = round(scores[i], 6)
        c["match"] = (c.get("match", "") + "+ce").lstrip("+")
        out.append(c)
    return out
