import json
import re
import time
import asyncio
import httpx
from database import SessionLocal
from models import ProviderConfig, ActiveModel
from config import PROVIDERS

LLM_TIMEOUT = httpx.Timeout(600.0, connect=30.0)
LLM_RETRIES = 3
LLM_RETRY_BACKOFF = 2.0


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
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except Exception as e:
            raise ValueError(f"Anthropic API error: {e}")

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except Exception as e:
            raise ValueError(f"Anthropic API error: {e}")


class OpenAICompatibleService(BaseLLMService):
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _handle_response(self, result: dict, response_status_code: int) -> str:
        if "error" in result:
            err = result["error"]
            err_msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            raise ValueError(f"API error ({response_status_code}): {err_msg}")
        if "choices" not in result:
            raise ValueError(f"API 响应格式异常 (status={response_status_code}): {json.dumps(result, ensure_ascii=False)[:500]}")
        content = result["choices"][0]["message"]["content"]
        if not content:
            finish_reason = result["choices"][0].get("finish_reason", "")
            raise ValueError(f"API 返回空内容 (finish_reason={finish_reason})")
        return content

    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        last_error = None
        for attempt in range(LLM_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
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
                    return self._handle_response(result, response.status_code)
            except (httpx.TimeoutException, httpx.RemoteProtocolError, httpx.ConnectError) as e:
                last_error = e
                if attempt < LLM_RETRIES - 1:
                    await asyncio.sleep(LLM_RETRY_BACKOFF * (2 ** attempt))
        raise ValueError(f"LLM API 请求失败（重试 {LLM_RETRIES} 次后）: {last_error}")

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        last_error = None
        for attempt in range(LLM_RETRIES):
            try:
                with httpx.Client(timeout=LLM_TIMEOUT) as client:
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
                    return self._handle_response(result, response.status_code)
            except (httpx.TimeoutException, httpx.RemoteProtocolError, httpx.ConnectError) as e:
                last_error = e
                if attempt < LLM_RETRIES - 1:
                    time.sleep(LLM_RETRY_BACKOFF * (2 ** attempt))
        raise ValueError(f"LLM API 请求失败（重试 {LLM_RETRIES} 次后）: {last_error}")


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
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(max_output_tokens=max_tokens),
            )
            return response.text
        except Exception as e:
            raise ValueError(f"Gemini API error: {e}")

    def generate_sync(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        from google.genai import types

        full_prompt = f"[System]: {system_prompt}\n\n[User]: {user_message}"
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(max_output_tokens=max_tokens),
            )
            return response.text
        except Exception as e:
            raise ValueError(f"Gemini API error: {e}")


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
  "zh-CN": "中文（简体）",
  "zh-TW": "中文（繁體）",
  "ja": "日本語",
  "ko": "한국어",
  "en": "English",
  "en-US": "English (United States)",
  "en-GB": "English (United Kingdom)",
  "es": "español",
  "es-419": "español (Latinoamérica)",
  "es-MX": "español (México)",
  "fr": "français",
  "fr-CA": "français (Canada)",
  "ar": "العربية",
  "ar-EG": "العربية المصرية",
  "ru": "русский",
  "id": "Bahasa Indonesia",
  "hi": "हिन्दी",
  "pt": "português",
  "pt-BR": "português (Brasil)",
  "pt-PT": "português (Portugal)",
  "de": "Deutsch",
  "de-DE": "Deutsch (Deutschland)",
  "af": "Afrikaans",
  "sq": "shqip",
  "am": "አማርኛ",
  "ti": "ትግርኛ",
  "hy": "հայերեն",
  "az": "azərbaycan",
  "az-Latn": "Azərbaycan (latın)",
  "az-Cyrl": "Азәрбајҹан дили",
  "eu": "euskara",
  "be": "беларуская",
  "bn": "বাংলা",
  "as": "অসমীয়া",
  "bs": "bosanski",
  "bg": "български",
  "ca": "català",
  "ceb": "Cebuano",
  "hr": "hrvatski",
  "cs": "čeština",
  "cy": "Cymraeg",
  "da": "dansk",
  "nl": "Nederlands",
  "et": "eesti",
  "fi": "suomi",
  "gl": "galego",
  "ka": "ქართული",
  "el": "Ελληνικά",
  "gu": "ગુજરાતી",
  "ht": "créole haïtien",
  "ha": "Hausa",
  "he": "עברית",
  "kok": "कोंकणी",
  "mai": "मैथिली",
  "mr": "मराठी",
  "ne": "नेपाली",
  "doi": "डोगरी",
  "hu": "magyar",
  "is": "íslenska",
  "ig": "Igbo",
  "jv": "Basa Jawa",
  "su": "Basa Sunda",
  "ga": "Gaeilge",
  "it": "italiano",
  "kn": "ಕನ್ನಡ",
  "kk": "қазақ тілі",
  "km": "ភាសាខ្មែរ",
  "rw": "Kinyarwanda",
  "ks": "کٲشُر",
  "ky": "кыргызча",
  "ku": "Kurdî",
  "ckb": "کوردی",
  "lo": "ລາວ",
  "la": "Latina",
  "lv": "latviešu",
  "lt": "lietuvių",
  "ln": "Lingála",
  "mk": "македонски",
  "mg": "Malagasy",
  "ms": "Melayu",
  "ml": "മലയാളം",
  "mt": "Malti",
  "mn": "Монгол хэл",
  "my": "မြန်မာ",
  "mni": "মৈতৈলোন্",
  "nb": "Norsk Bokmål",
  "nn": "Norsk Nynorsk",
  "no": "Norsk",
  "ny": "Chichewa",
  "or": "ଓଡ଼ିଆ",
  "ps": "پښتو",
  "fa": "فارسی",
  "fil": "Wikang Filipino",
  "pl": "polski",
  "pa": "ਪੰਜਾਬੀ",
  "ro": "română",
  "tt": "татарча",
  "ba": "башҡортса",
  "cv": "чӑваш",
  "ce": "нохчийн мотт",
  "av": "магӀарул мацӀ",
  "sah": "саха тыла",
  "tyv": "тыва дыл",
  "sr": "српски",
  "sr-Latn": "srpski (latinica)",
  "sd": "سنڌي",
  "si": "සිංහල",
  "sk": "slovenčina",
  "sl": "slovenščina",
  "so": "Soomaali",
  "st": "Sesotho",
  "tn": "Setswana",
  "sw": "Kiswahili",
  "sv": "svenska",
  "tg": "тоҷикӣ",
  "ta": "தமிழ்",
  "te": "తెలుగు",
  "th": "ไทย",
  "tk": "Türkmen",
  "tr": "Türkçe",
  "ug": "ئۇيغۇرچە",
  "uk": "українська",
  "ur": "اردو",
  "uz": "oʻzbek",
  "uz-Cyrl": "Ўзбек",
  "vi": "Tiếng Việt",
  "xh": "isiXhosa",
  "yo": "Yorùbá",
  "zu": "isiZulu",
}


def _get_language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "简体中文")


def _language_rule(lang_name: str) -> str:
    return f"""【语言铁律 / LANGUAGE RULE】
本书的写作语言是：{lang_name}。
1. 从书名、章节标题到每一句正文，全部必须使用 {lang_name}，任何情况下都不得混入其他语言的句子或段落。
2. 即使下方的参考资料、风格样本或续写原文使用了其他语言，你也必须将其中的信息用 {lang_name} 重新表达。
3. 唯一例外：如果本书是语言教学/学习类书籍，允许出现"所教授的目标语言"的例句和词汇，但所有讲解、说明文字仍必须使用 {lang_name}，形成 {lang_name} + 目标语言的对照。
4. 代码、数学公式、专有名词（人名、品牌等）可保留原文。
违反语言铁律是最严重的错误。"""


def _compose_context(card_context: str, extra_requirements: str) -> str:
    """组装写作卡上下文（RAG 检索结果 + 额外需求），拼入 system prompt。"""
    parts = []
    if card_context:
        parts.append(
            "# 写作卡参考材料\n"
            "以下材料按用途分类。「写作指导」约束写法，「风格参考」需模仿其文风（不要照抄内容），"
            "「资料库」提供事实依据（优先采用），「续写原文」是必须自然衔接续写的原文上下文。\n\n"
            + card_context
        )
    if extra_requirements:
        parts.append(f"# 额外需求（必须满足）\n{extra_requirements}")
    return "\n\n".join(parts)


def _build_outline_prompts(
    prompt: str,
    requirements: dict,
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
) -> tuple[str, str]:
    lang_code = requirements.get("language", "zh-CN")
    lang_name = _get_language_name(lang_code)

    continuation_note = (
        "\n注意：本书是【续写】任务，大纲必须从「续写原文」结尾处自然延续其情节、人物与设定，不要重新开始故事。"
        if has_continuation
        else ""
    )
    context = _compose_context(card_context, extra_requirements)

    system_prompt = f"""你是一个专业的电子书大纲生成器。根据用户需求和生成要求，生成结构化的JSON格式大纲。

{_language_rule(lang_name)}
{continuation_note}
{context}

返回格式（必须严格遵循JSON格式，不要包含其他文字）：
{{
    "title": "书籍标题（{lang_name}）",
    "description": "书籍简介（{lang_name}）",
    "tags": ["3到6个内容分类标签（{lang_name}，每个2-6字，如题材/领域/受众）"],
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

    return system_prompt, user_message


def _build_chapter_prompts(
    outline: dict,
    chapter: dict,
    chapter_index: int,
    language: str = "zh-CN",
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
    enable_rich: bool = False,
    stub_note: str = "",
) -> tuple[str, str]:
    lang_name = _get_language_name(language)
    total_chapters = len(outline.get("chapters", []))

    continuation_note = (
        "\n注意：本书是【续写】任务，内容必须延续「续写原文」的情节、人物、设定与文风。"
        if has_continuation
        else ""
    )
    context = _compose_context(card_context, extra_requirements)

    rich_block = ""
    if enable_rich:
        from services.content_tools import content_tools_prompt
        rich_block = "\n\n" + content_tools_prompt()
    if stub_note:
        rich_block += "\n\n" + stub_note

    system_prompt = f"""你是一个专业的电子书内容写手。正在为《{outline["title"]}》撰写第{chapter_index + 1}章（共{total_chapters}章）。
书籍简介：{outline["description"]}

{_language_rule(lang_name)}
{continuation_note}
{context}

你必须使用以下 Markdown 标题层级来组织章节内容：
- ### 三级标题：用于章节内的主要小节（必须有）
- #### 四级标题：用于小节内的细分（可选）

严禁使用一级标题(#)和二级标题(##)，因为它们已被书名和章名占用。
每个章节必须至少包含一个 ### 三级标题。

示例格式：
### 1.1 小节标题
正文内容...

#### 1.1.1 细分标题
正文内容...

### 1.2 小节标题
正文内容...{rich_block}"""

    user_message = f"""章节标题：{chapter["title"]}
章节概要：{chapter["summary"]}

请用 {lang_name} 撰写完整的章节内容，使用 ### 和 #### 组织内容结构。"""

    return system_prompt, user_message


def _parse_outline_json(content: str) -> dict:
    try:
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse outline JSON: {content[:200]}...")


def _clean_chapter_markdown(content: str) -> str:
    content = re.sub(r'^#{1,2}\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^(#{5,6})\s+', lambda m: '####' + m.group(0)[len(m.group(1)):], content, flags=re.MULTILINE)
    return content


def generate_outline_sync(
    prompt: str,
    requirements: dict,
    provider_id: str = None,
    model_name: str = None,
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
) -> dict:
    service = get_llm_service(provider_id, model_name)
    system_prompt, user_message = _build_outline_prompts(
        prompt, requirements, card_context, extra_requirements, has_continuation
    )
    content = service.generate_sync(system_prompt, user_message)
    return _parse_outline_json(content)


def _postprocess_chapter(content: str, enable_rich: bool) -> str:
    content = _clean_chapter_markdown(content)
    if enable_rich:
        from services.content_tools import apply_content_tools
        content = apply_content_tools(content)
    return content


def generate_chapter_sync(
    outline: dict,
    chapter: dict,
    chapter_index: int,
    provider_id: str = None,
    model_name: str = None,
    language: str = "zh-CN",
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
    enable_rich: bool = False,
    stub_note: str = "",
    post_process: bool = True,
) -> str:
    service = get_llm_service(provider_id, model_name)
    system_prompt, user_message = _build_chapter_prompts(
        outline, chapter, chapter_index, language, card_context, extra_requirements, has_continuation, enable_rich, stub_note
    )
    content = service.generate_sync(system_prompt, user_message)
    if not post_process:
        # 仅做标题清洗，content_tools 留给调用方在 stub 处理后再执行
        return _clean_chapter_markdown(content)
    return _postprocess_chapter(content, enable_rich)


async def generate_outline(
    prompt: str,
    requirements: dict,
    provider_id: str = None,
    model_name: str = None,
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
) -> dict:
    service = get_llm_service(provider_id, model_name)
    system_prompt, user_message = _build_outline_prompts(
        prompt, requirements, card_context, extra_requirements, has_continuation
    )
    content = await service.generate(system_prompt, user_message)
    return _parse_outline_json(content)


async def generate_chapter(
    outline: dict,
    chapter: dict,
    chapter_index: int,
    provider_id: str = None,
    model_name: str = None,
    language: str = "zh-CN",
    card_context: str = "",
    extra_requirements: str = "",
    has_continuation: bool = False,
    enable_rich: bool = False,
) -> str:
    service = get_llm_service(provider_id, model_name)
    system_prompt, user_message = _build_chapter_prompts(
        outline, chapter, chapter_index, language, card_context, extra_requirements, has_continuation, enable_rich
    )
    content = await service.generate(system_prompt, user_message)
    return _postprocess_chapter(content, enable_rich)
