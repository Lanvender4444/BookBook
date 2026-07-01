"""应用设置（web 搜索 provider / API key 等）。

API key 用与 provider 相同的轻量异或方案加密存储，避免明文落库。
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.agent_tools import get_setting, set_setting, web_search_configured

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _mask(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 6:
        return "*" * len(key)
    return key[:3] + "*" * (len(key) - 6) + key[-3:]


@router.get("/search")
def get_search_config():
    provider = get_setting("search_provider", "")
    key = get_setting("search_api_key", "")
    return {
        "provider": provider,
        "has_key": bool(key),
        "key_masked": _mask(key),
        "configured": web_search_configured(),
        "supported": ["tavily", "serper", "brave"],
    }


class SearchConfigRequest(BaseModel):
    provider: str = ""
    api_key: str | None = None  # None = 不修改；"" = 清空


@router.post("/search")
def update_search_config(req: SearchConfigRequest):
    set_setting("search_provider", (req.provider or "").lower().strip())
    if req.api_key is not None:
        set_setting("search_api_key", req.api_key.strip())
    return get_search_config()


# ---------------------------------------------------------------- Cross-encoder 精排配置

@router.get("/rerank")
def get_rerank_config():
    from services import reranker

    provider = get_setting("rerank_provider", "")
    key = get_setting("rerank_api_key", "")
    return {
        "provider": provider,
        "model": get_setting("rerank_model", ""),
        "has_key": bool(key),
        "key_masked": _mask(key),
        "configured": reranker.available(),
        "supported": ["jina", "cohere", "siliconflow", "voyage", "local"],
    }


class RerankConfigRequest(BaseModel):
    provider: str = ""          # jina/cohere/siliconflow/voyage/local/""
    api_key: str | None = None  # None = 不修改；"" = 清空
    model: str | None = None    # None = 不修改；"" = 用默认多语言模型


@router.post("/rerank")
def update_rerank_config(req: RerankConfigRequest):
    set_setting("rerank_provider", (req.provider or "").lower().strip())
    if req.api_key is not None:
        set_setting("rerank_api_key", req.api_key.strip())
    if req.model is not None:
        set_setting("rerank_model", req.model.strip())
    return get_rerank_config()
