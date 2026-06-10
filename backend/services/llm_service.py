import json
import httpx
from database import SessionLocal
from models import ProviderConfig, ActiveModel
from config import PROVIDERS


def _decrypt_api_key(encrypted: str) -> str:
    if not encrypted:
        return ""
    import base64

    FERNET_KEY = b"bkbk_ebook_api_key_encryption_key_2026!!"
    try:
        key_bytes = FERNET_KEY
        data_bytes = base64.b64decode(encrypted)
        decrypted = bytearray(len(data_bytes))
        for i, b in enumerate(data_bytes):
            decrypted[i] = b ^ key_bytes[i % len(key_bytes)]
        return decrypted.decode("utf-8")
    except Exception:
        return ""


class BaseLLMService:
    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        raise NotImplementedError

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        raise NotImplementedError


class AnthropicService(BaseLLMService):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text


class OpenAICompatibleService(BaseLLMService):
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]


class GeminiService(BaseLLMService):
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        from google.genai import types

        full_prompt = f"[System]: {system_prompt}\n\n[User]: {user_message}"
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        return response.text

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        from google.genai import types

        full_prompt = f"[System]: {system_prompt}\n\n[User]: {user_message}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        return response.text


def get_llm_service(provider_id: str = None, model_name: str = None) -> BaseLLMService:
    db = SessionLocal()
    try:
        if provider_id and model_name:
            config = (
                db.query(ProviderConfig)
                .filter(ProviderConfig.provider_id == provider_id)
                .first()
            )
            if not config:
                raise ValueError(f"Provider '{provider_id}' not configured")
            api_key = _decrypt_api_key(config.api_key)
            base_url = config.base_url or PROVIDERS.get(provider_id, {}).get(
                "default_base_url", ""
            )
            return _create_service(provider_id, api_key, base_url, model_name)

        active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()
        if active:
            config = (
                db.query(ProviderConfig)
                .filter(ProviderConfig.provider_id == active.provider_id)
                .first()
            )
            if config:
                api_key = _decrypt_api_key(config.api_key)
                base_url = config.base_url or PROVIDERS.get(active.provider_id, {}).get(
                    "default_base_url", ""
                )
                return _create_service(
                    active.provider_id, api_key, base_url, active.model_name
                )

        from config import (
            LLM_PROVIDER,
            LLM_MODEL,
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

        services = {
            "anthropic": lambda: AnthropicService(ANTHROPIC_API_KEY, LLM_MODEL),
            "openai": lambda: OpenAICompatibleService(
                OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL
            ),
            "deepseek": lambda: OpenAICompatibleService(
                DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
            ),
            "zhipu": lambda: OpenAICompatibleService(
                ZHIPU_API_KEY, ZHIPU_BASE_URL, LLM_MODEL
            ),
            "qwen": lambda: OpenAICompatibleService(
                QWEN_API_KEY, QWEN_BASE_URL, LLM_MODEL
            ),
            "kimi": lambda: OpenAICompatibleService(
                KIMI_API_KEY, KIMI_BASE_URL, LLM_MODEL
            ),
            "gemini": lambda: GeminiService(GEMINI_API_KEY, LLM_MODEL),
        }

        if LLM_PROVIDER not in services:
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

        return services[LLM_PROVIDER]()
    finally:
        db.close()


def _create_service(
    provider_id: str, api_key: str, base_url: str, model_name: str
) -> BaseLLMService:
    provider_def = PROVIDERS.get(provider_id)
    if not provider_def:
        raise ValueError(f"Unknown provider: {provider_id}")

    api_type = provider_def["api_type"]

    if api_type == "anthropic":
        return AnthropicService(api_key=api_key, model=model_name)
    elif api_type == "gemini":
        return GeminiService(api_key=api_key, model=model_name)
    else:
        return OpenAICompatibleService(
            api_key=api_key, base_url=base_url, model=model_name
        )


def get_active_provider_info() -> dict:
    db = SessionLocal()
    try:
        active = db.query(ActiveModel).order_by(ActiveModel.id.desc()).first()
        if not active:
            return None

        config = (
            db.query(ProviderConfig)
            .filter(ProviderConfig.provider_id == active.provider_id)
            .first()
        )
        provider_def = PROVIDERS.get(active.provider_id)

        return {
            "provider_id": active.provider_id,
            "provider_name": provider_def["name"]
            if provider_def
            else active.provider_id,
            "model_name": active.model_name,
            "api_type": provider_def["api_type"]
            if provider_def
            else "openai_compatible",
            "is_configured": config is not None,
        }
    finally:
        db.close()


LANGUAGE_NAMES = {
    "zh-CN": "简体中文",
    "zh-TW": "繁体中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "español",
    "fr": "français",
    "de": "Deutsch",
    "it": "italiano",
    "pt-BR": "português (Brasil)",
    "ru": "русский",
    "ar": "العربية",
    "hi": "हिन्दी",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Indonesia",
    "ms": "Melayu",
    "tr": "Türkçe",
    "pl": "polski",
    "nl": "Nederlands",
    "sv": "svenska",
    "da": "dansk",
    "fi": "suomi",
    "nb": "norsk bokmål",
    "cs": "čeština",
    "sk": "slovenčina",
    "hu": "magyar",
    "ro": "română",
    "bg": "български",
    "uk": "українська",
    "el": "Ελληνικά",
    "he": "עברית",
    "bn": "বাংলা",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "ml": "മലയാളം",
    "kn": "ಕನ್ನಡ",
    "ca": "català",
    "hr": "hrvatski",
    "sl": "slovenščina",
    "et": "eesti",
    "lv": "latviešu",
    "lt": "lietuvių",
    "fil": "Filipino",
    "sw": "Kiswahili",
    "af": "Afrikaans",
}


def _get_language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "简体中文")


def generate_outline_sync(
    prompt: str, requirements: dict, provider_id: str = None, model_name: str = None
) -> dict:
    service = get_llm_service(provider_id, model_name)

    lang_code = requirements.get("language", "zh-CN")
    lang_name = _get_language_name(lang_code)

    system_prompt = f"""你是一个专业的电子书大纲生成器。根据用户需求和生成要求，生成结构化的JSON格式大纲。

重要：书籍内容必须使用 {lang_name} 撰写，所有标题和描述都必须是 {lang_name}。

返回格式（必须严格遵循JSON格式，不要包含其他文字）：
{{
    "title": "书籍标题（{lang_name}）",
    "description": "书籍简介（{lang_name}）",
    "chapters": [
        {{"title": "章节标题（{lang_name}）", "summary": "章节概要（{lang_name}）"}}
    ]
}}"""

    user_message = f"""用户需求：{prompt}

生成要求：
- 难易度：{requirements.get("difficulty", "中等")}
- 目标字数：{requirements.get("word_count", "5000")}字
- 章节数量：{requirements.get("chapter_count", "5-8")}
- 风格：{requirements.get("style", "科普向")}
- 语言：{lang_name}

请生成详细的大纲，只返回JSON格式内容。"""

    content = service.generate_sync(system_prompt, user_message)

    try:
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse outline JSON: {content[:200]}...")


def generate_chapter_sync(
    outline: dict,
    chapter: dict,
    chapter_index: int,
    provider_id: str = None,
    model_name: str = None,
) -> str:
    service = get_llm_service(provider_id, model_name)

    system_prompt = f"""你是一个专业的电子书内容写手。正在为《{outline["title"]}》撰写第{chapter_index + 1}章。
书籍简介：{outline["description"]}

要求：
- 内容详实，逻辑清晰
- 语言流畅，符合目标读者水平
- 字数控制在合理范围内
- 保持与书籍标题相同的语言"""

    user_message = f"""章节标题：{chapter["title"]}
章节概要：{chapter["summary"]}

请撰写完整的章节内容。"""

    content = service.generate_sync(system_prompt, user_message)
    return content


async def generate_outline(
    prompt: str, requirements: dict, provider_id: str = None, model_name: str = None
) -> dict:
    service = get_llm_service(provider_id, model_name)

    lang_code = requirements.get("language", "zh-CN")
    lang_name = _get_language_name(lang_code)

    system_prompt = f"""你是一个专业的电子书大纲生成器。根据用户需求和生成要求，生成结构化的JSON格式大纲。

重要：书籍内容必须使用 {lang_name} 撰写，所有标题和描述都必须是 {lang_name}。

返回格式（必须严格遵循JSON格式，不要包含其他文字）：
{{
    "title": "书籍标题（{lang_name}）",
    "description": "书籍简介（{lang_name}）",
    "chapters": [
        {{"title": "章节标题（{lang_name}）", "summary": "章节概要（{lang_name}）"}}
    ]
}}"""

    user_message = f"""用户需求：{prompt}

生成要求：
- 难易度：{requirements.get("difficulty", "中等")}
- 目标字数：{requirements.get("word_count", "5000")}字
- 章节数量：{requirements.get("chapter_count", "5-8")}
- 风格：{requirements.get("style", "科普向")}
- 语言：{lang_name}

请生成详细的大纲，只返回JSON格式内容。"""

    content = await service.generate(system_prompt, user_message)

    try:
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse outline JSON: {content[:200]}...")


async def generate_chapter(
    outline: dict,
    chapter: dict,
    chapter_index: int,
    provider_id: str = None,
    model_name: str = None,
) -> str:
    service = get_llm_service(provider_id, model_name)

    system_prompt = f"""你是一个专业的电子书内容写手。正在为《{outline["title"]}》撰写第{chapter_index + 1}章。
书籍简介：{outline["description"]}

要求：
- 内容详实，逻辑清晰
- 语言流畅，符合目标读者水平
- 字数控制在合理范围内
- 保持与书籍标题相同的语言"""

    user_message = f"""章节标题：{chapter["title"]}
章节概要：{chapter["summary"]}

请撰写完整的章节内容。"""

    content = await service.generate(system_prompt, user_message)
    return content
