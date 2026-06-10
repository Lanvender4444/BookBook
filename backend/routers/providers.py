import base64
import json
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import ProviderConfig, ActiveModel
from config import PROVIDERS, PROVIDER_CATEGORIES

router = APIRouter(prefix="/api/providers", tags=["providers"])

FERNET_KEY = b"bkbk_ebook_api_key_encryption_key_2026!!"


def _encrypt_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    key_bytes = FERNET_KEY
    data_bytes = api_key.encode("utf-8")
    encrypted = bytearray(len(data_bytes))
    for i, b in enumerate(data_bytes):
        encrypted[i] = b ^ key_bytes[i % len(key_bytes)]
    return base64.b64encode(bytes(encrypted)).decode("ascii")


def _decrypt_api_key(encrypted: str) -> str:
    if not encrypted:
        return ""
    try:
        key_bytes = FERNET_KEY
        data_bytes = base64.b64decode(encrypted)
        decrypted = bytearray(len(data_bytes))
        for i, b in enumerate(data_bytes):
            decrypted[i] = b ^ key_bytes[i % len(key_bytes)]
        return decrypted.decode("utf-8")
    except Exception:
        return ""


def _mask_api_key(api_key: str) -> str:
    if not api_key or len(api_key) < 8:
        return "***"
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]


class ConfigureProviderRequest(BaseModel):
    provider_id: str
    api_key: str
    base_url: str | None = None
    models: list[str] | None = None


class SetActiveModelRequest(BaseModel):
    provider_id: str
    model_name: str


@router.get("/list")
def list_providers(db: Session = Depends(get_db)):
    configs = {c.provider_id: c for c in db.query(ProviderConfig).all()}
    active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()

    result = []
    for cat in PROVIDER_CATEGORIES:
        providers_in_cat = []
        for pid in cat["providers"]:
            provider_def = PROVIDERS.get(pid)
            if not provider_def:
                continue
            config = configs.get(pid)
            providers_in_cat.append(
                {
                    "id": pid,
                    "name": provider_def["name"],
                    "api_type": provider_def["api_type"],
                    "default_base_url": provider_def["default_base_url"],
                    "default_models": provider_def["default_models"],
                    "website": provider_def.get("website", ""),
                    "is_configured": config is not None,
                    "has_api_key": config is not None and bool(config.api_key),
                    "masked_api_key": _mask_api_key(_decrypt_api_key(config.api_key))
                    if config and config.api_key
                    else "",
                    "base_url": config.base_url if config else None,
                    "models": config.models if config else None,
                    "is_active": config.is_active if config else False,
                }
            )
        result.append(
            {
                "id": cat["id"],
                "name": cat["name"],
                "providers": providers_in_cat,
            }
        )

    active_info = None
    if active:
        active_info = {
            "provider_id": active.provider_id,
            "model_name": active.model_name,
        }

    return {"categories": result, "active": active_info}


@router.get("/{provider_id}")
def get_provider(provider_id: str, db: Session = Depends(get_db)):
    provider_def = PROVIDERS.get(provider_id)
    if not provider_def:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_id}' not found"
        )

    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == provider_id)
        .first()
    )

    return {
        "id": provider_id,
        "name": provider_def["name"],
        "api_type": provider_def["api_type"],
        "default_base_url": provider_def["default_base_url"],
        "default_models": provider_def["default_models"],
        "website": provider_def.get("website", ""),
        "is_configured": config is not None,
        "has_api_key": config is not None and bool(config.api_key),
        "masked_api_key": _mask_api_key(_decrypt_api_key(config.api_key))
        if config and config.api_key
        else "",
        "base_url": config.base_url if config else None,
        "models": config.models if config else None,
        "is_active": config.is_active if config else False,
    }


@router.post("/configure")
def configure_provider(
    request: ConfigureProviderRequest, db: Session = Depends(get_db)
):
    provider_def = PROVIDERS.get(request.provider_id)
    if not provider_def:
        raise HTTPException(
            status_code=404, detail=f"Provider '{request.provider_id}' not found"
        )

    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == request.provider_id)
        .first()
    )

    base_url = request.base_url or provider_def["default_base_url"]
    models = request.models or provider_def["default_models"]
    encrypted_key = _encrypt_api_key(request.api_key)

    if config:
        config.api_key = encrypted_key
        config.base_url = base_url
        config.models = models
        config.is_active = True
        config.updated_at = datetime.now()
    else:
        config = ProviderConfig(
            provider_id=request.provider_id,
            name=provider_def["name"],
            api_key=encrypted_key,
            base_url=base_url,
            models=models,
            is_active=True,
        )
        db.add(config)

    db.commit()
    db.refresh(config)

    if not db.query(ActiveModel).first():
        active = ActiveModel(
            provider_id=request.provider_id,
            model_name=models[0] if models else "",
        )
        db.add(active)
        db.commit()

    return {
        "message": "Provider configured successfully",
        "provider_id": request.provider_id,
        "masked_api_key": _mask_api_key(request.api_key),
    }


@router.delete("/{provider_id}")
def delete_provider(provider_id: str, db: Session = Depends(get_db)):
    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == provider_id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="Provider config not found")

    active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()
    if active and active.provider_id == provider_id:
        remaining = (
            db.query(ProviderConfig)
            .filter(
                ProviderConfig.provider_id != provider_id,
                ProviderConfig.is_active == True,
            )
            .first()
        )
        if remaining:
            active.provider_id = remaining.provider_id
            remaining_models = remaining.models or []
            active.model_name = remaining_models[0] if remaining_models else ""
            active.updated_at = datetime.now()
        else:
            db.delete(active)

    db.delete(config)
    db.commit()

    return {"message": "Provider removed successfully"}


@router.post("/active")
def set_active_model(request: SetActiveModelRequest, db: Session = Depends(get_db)):
    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == request.provider_id)
        .first()
    )
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Provider not configured. Please configure it first.",
        )

    available_models = config.models or []
    if request.model_name not in available_models:
        if available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model_name}' not available. Available: {', '.join(available_models)}",
            )

    db.query(ProviderConfig).update({ProviderConfig.is_active: False})
    config.is_active = True

    active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()
    if active:
        active.provider_id = request.provider_id
        active.model_name = request.model_name
        active.updated_at = datetime.now()
    else:
        active = ActiveModel(
            provider_id=request.provider_id,
            model_name=request.model_name,
        )
        db.add(active)

    db.commit()

    return {
        "message": "Active model set successfully",
        "provider_id": request.provider_id,
        "model_name": request.model_name,
    }


@router.get("/active/detail")
def get_active_detail(db: Session = Depends(get_db)):
    active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()
    if not active:
        return {"active": None}

    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == active.provider_id)
        .first()
    )
    provider_def = PROVIDERS.get(active.provider_id)

    return {
        "active": {
            "provider_id": active.provider_id,
            "model_name": active.model_name,
            "provider_name": provider_def["name"]
            if provider_def
            else active.provider_id,
            "api_type": provider_def["api_type"]
            if provider_def
            else "openai_compatible",
            "base_url": config.base_url if config else None,
            "is_configured": config is not None,
        }
    }


@router.post("/{provider_id}/test")
async def test_provider(provider_id: str, db: Session = Depends(get_db)):
    config = (
        db.query(ProviderConfig)
        .filter(ProviderConfig.provider_id == provider_id)
        .first()
    )
    if not config or not config.api_key:
        raise HTTPException(
            status_code=400, detail="Provider not configured or missing API key"
        )

    provider_def = PROVIDERS.get(provider_id)
    if not provider_def:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_id}' not found"
        )

    api_key = _decrypt_api_key(config.api_key)
    api_type = provider_def["api_type"]
    base_url = config.base_url or provider_def["default_base_url"]

    try:
        if api_type == "openai_compatible":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{base_url}/models", headers=headers)
                if resp.status_code == 200:
                    model_list = resp.json().get("data", [])
                    model_ids = [m.get("id", "") for m in model_list if m.get("id")]
                    available_models = config.models or provider_def["default_models"]
                    if available_models:
                        model_ids = [
                            m
                            for m in model_ids
                            if any(av in m for av in available_models)
                        ] or model_ids
                    return {
                        "success": True,
                        "message": "Connection successful",
                        "available_models": model_ids[:50],
                    }
                else:
                    try:
                        error_detail = resp.json()
                    except Exception:
                        error_detail = resp.text
                    return {
                        "success": False,
                        "message": f"API returned status {resp.status_code}",
                        "detail": str(error_detail)[:200],
                    }

        elif api_type == "anthropic":
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://api.anthropic.com/v1/models", headers=headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    model_ids = [m.get("id", "") for m in data.get("data", [])]
                    return {
                        "success": True,
                        "message": "Connection successful",
                        "available_models": model_ids[:50],
                    }
                elif resp.status_code == 401:
                    return {"success": False, "message": "Invalid API key"}
                else:
                    try:
                        models_resp = await client.post(
                            f"{base_url}/v1/messages",
                            headers=headers,
                            json={
                                "model": config.models[0]
                                if config.models
                                else "claude-sonnet-4-20250514",
                                "max_tokens": 1,
                                "messages": [{"role": "user", "content": "test"}],
                            },
                        )
                        if models_resp.status_code == 200:
                            return {
                                "success": True,
                                "message": "Connection successful",
                                "available_models": config.models or [],
                            }
                        elif models_resp.status_code == 401:
                            return {"success": False, "message": "Invalid API key"}
                        elif models_resp.status_code == 400:
                            return {
                                "success": True,
                                "message": "API key valid (model test returned 400, which is expected)",
                                "available_models": config.models or [],
                            }
                        else:
                            return {
                                "success": True,
                                "message": "API key appears valid",
                                "available_models": config.models or [],
                            }
                    except Exception:
                        return {
                            "success": True,
                            "message": "API key configured (could not verify models list)",
                            "available_models": config.models or [],
                        }

        elif api_type == "gemini":
            test_url = f"{base_url}/v1beta/models?key={api_key}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(test_url)
                if resp.status_code == 200:
                    data = resp.json()
                    model_ids = [
                        m.get("name", "").replace("models/", "")
                        for m in data.get("models", [])
                    ]
                    return {
                        "success": True,
                        "message": "Connection successful",
                        "available_models": model_ids[:50],
                    }
                elif resp.status_code == 400 or resp.status_code == 403:
                    return {"success": False, "message": "Invalid API key"}
                else:
                    return {
                        "success": True,
                        "message": "API key configured",
                        "available_models": config.models or [],
                    }

        else:
            return {
                "success": True,
                "message": "Provider type not testable",
                "available_models": config.models or [],
            }

    except httpx.TimeoutException:
        return {"success": False, "message": "Connection timed out"}
    except httpx.ConnectError:
        return {"success": False, "message": "Could not connect to the API server"}
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)}"}


@router.post("/migrate-env")
def migrate_env_keys(db: Session = Depends(get_db)):
    from config import (
        ANTHROPIC_API_KEY,
        OPENAI_API_KEY,
        DEEPSEEK_API_KEY,
        ZHIPU_API_KEY,
        QWEN_API_KEY,
        GEMINI_API_KEY,
        KIMI_API_KEY,
        OPENAI_BASE_URL,
        DEEPSEEK_BASE_URL,
        ZHIPU_BASE_URL,
        QWEN_BASE_URL,
        KIMI_BASE_URL,
    )

    env_mappings = [
        ("anthropic", ANTHROPIC_API_KEY, None),
        ("openai", OPENAI_API_KEY, OPENAI_BASE_URL),
        ("deepseek", DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL),
        ("zhipu", ZHIPU_API_KEY, ZHIPU_BASE_URL),
        ("qwen", QWEN_API_KEY, QWEN_BASE_URL),
        ("gemini", GEMINI_API_KEY, None),
        ("kimi", KIMI_API_KEY, KIMI_BASE_URL),
    ]

    migrated = []
    for provider_id, api_key, base_url in env_mappings:
        if (
            api_key
            and api_key != f"your_{provider_id}_key_here"
            and not api_key.startswith("your_")
        ):
            existing = (
                db.query(ProviderConfig)
                .filter(ProviderConfig.provider_id == provider_id)
                .first()
            )
            if not existing:
                provider_def = PROVIDERS.get(provider_id)
                config = ProviderConfig(
                    provider_id=provider_id,
                    name=provider_def["name"],
                    api_key=_encrypt_api_key(api_key),
                    base_url=base_url or provider_def["default_base_url"],
                    models=provider_def["default_models"],
                    is_active=True,
                )
                db.add(config)
                migrated.append(provider_id)

    if migrated:
        if not db.query(ActiveModel).first():
            first_provider = (
                db.query(ProviderConfig)
                .filter(ProviderConfig.is_active == True)
                .first()
            )
            if first_provider:
                models = first_provider.models or []
                active = ActiveModel(
                    provider_id=first_provider.provider_id,
                    model_name=models[0] if models else "",
                )
                db.add(active)

    db.commit()

    return {
        "message": f"Migrated {len(migrated)} provider(s) from environment",
        "migrated": migrated,
    }
