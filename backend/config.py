import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")

# Base URLs (for OpenAI-compatible APIs)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")

# P2P Settings
P2P_ENABLED = os.getenv("P2P_ENABLED", "true").lower() == "true"
P2P_BROADCAST_PORT = int(os.getenv("P2P_BROADCAST_PORT", "47832"))
P2P_BOOK_PORT = int(os.getenv("P2P_BOOK_PORT", "47833"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ebooks.db")
