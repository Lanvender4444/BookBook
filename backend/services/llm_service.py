import json
import httpx
from config import (
    LLM_PROVIDER, LLM_MODEL,
    ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY,
    ZHIPU_API_KEY, QWEN_API_KEY, GEMINI_API_KEY, KIMI_API_KEY,
    OPENAI_BASE_URL, DEEPSEEK_BASE_URL, ZHIPU_BASE_URL,
    QWEN_BASE_URL, KIMI_BASE_URL
)

class BaseLLMService:
    async def generate(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        raise NotImplementedError
    
    def generate_sync(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        """同步版本，用于后台线程"""
        raise NotImplementedError

class AnthropicService(BaseLLMService):
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    async def generate(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    
    def generate_sync(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

class OpenAICompatibleService(BaseLLMService):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def generate(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def generate_sync(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]

class GeminiService(BaseLLMService):
    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    async def generate(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        from google.genai import types
        full_prompt = f"[System]: {system_prompt}\n\n[User]: {user_message}"
        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens)
        )
        return response.text
    
    def generate_sync(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        from google.genai import types
        full_prompt = f"[System]: {system_prompt}\n\n[User]: {user_message}"
        response = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens)
        )
        return response.text

def get_llm_service() -> BaseLLMService:
    services = {
        "anthropic": lambda: AnthropicService(),
        "openai": lambda: OpenAICompatibleService(OPENAI_API_KEY, OPENAI_BASE_URL),
        "deepseek": lambda: OpenAICompatibleService(DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL),
        "zhipu": lambda: OpenAICompatibleService(ZHIPU_API_KEY, ZHIPU_BASE_URL),
        "qwen": lambda: OpenAICompatibleService(QWEN_API_KEY, QWEN_BASE_URL),
        "kimi": lambda: OpenAICompatibleService(KIMI_API_KEY, KIMI_BASE_URL),
        "gemini": lambda: GeminiService(),
    }
    
    if LLM_PROVIDER not in services:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
    
    return services[LLM_PROVIDER]()

llm_service = get_llm_service()

def generate_outline_sync(prompt: str, requirements: dict) -> dict:
    """同步版本的大纲生成"""
    system_prompt = """你是一个专业的电子书大纲生成器。根据用户需求和生成要求，生成结构化的JSON格式大纲。
    
返回格式（必须严格遵循JSON格式，不要包含其他文字）：
{
    "title": "书籍标题",
    "description": "书籍简介",
    "chapters": [
        {"title": "章节标题", "summary": "章节概要"}
    ]
}"""
    
    user_message = f"""用户需求：{prompt}

生成要求：
- 难易度：{requirements.get('difficulty', '中等')}
- 目标字数：{requirements.get('word_count', '5000')}字
- 章节数量：{requirements.get('chapter_count', '5-8')}
- 风格：{requirements.get('style', '科普向')}

请生成详细的大纲，只返回JSON格式内容。"""
    
    content = llm_service.generate_sync(system_prompt, user_message)
    
    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse outline JSON: {content[:200]}...")

def generate_chapter_sync(outline: dict, chapter: dict, chapter_index: int) -> str:
    """同步版本的章节生成"""
    system_prompt = f"""你是一个专业的电子书内容写手。正在为《{outline['title']}》撰写第{chapter_index + 1}章。
书籍简介：{outline['description']}

要求：
- 内容详实，逻辑清晰
- 语言流畅，符合目标读者水平
- 字数控制在合理范围内"""

    user_message = f"""章节标题：{chapter['title']}
章节概要：{chapter['summary']}

请撰写完整的章节内容。"""

    content = llm_service.generate_sync(system_prompt, user_message)
    return content

async def generate_outline(prompt: str, requirements: dict) -> dict:
    system_prompt = """你是一个专业的电子书大纲生成器。根据用户需求和生成要求，生成结构化的JSON格式大纲。
    
返回格式（必须严格遵循JSON格式，不要包含其他文字）：
{
    "title": "书籍标题",
    "description": "书籍简介",
    "chapters": [
        {"title": "章节标题", "summary": "章节概要"}
    ]
}"""
    
    user_message = f"""用户需求：{prompt}

生成要求：
- 难易度：{requirements.get('difficulty', '中等')}
- 目标字数：{requirements.get('word_count', '5000')}字
- 章节数量：{requirements.get('chapter_count', '5-8')}
- 风格：{requirements.get('style', '科普向')}

请生成详细的大纲，只返回JSON格式内容。"""
    
    content = await llm_service.generate(system_prompt, user_message)
    
    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse outline JSON: {content[:200]}...")

async def generate_chapter(outline: dict, chapter: dict, chapter_index: int) -> str:
    system_prompt = f"""你是一个专业的电子书内容写手。正在为《{outline['title']}》撰写第{chapter_index + 1}章。
书籍简介：{outline['description']}

要求：
- 内容详实，逻辑清晰
- 语言流畅，符合目标读者水平
- 字数控制在合理范围内"""

    user_message = f"""章节标题：{chapter['title']}
章节概要：{chapter['summary']}

请撰写完整的章节内容。"""

    content = await llm_service.generate(system_prompt, user_message)
    return content
