import os
import json
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 加载根目录配置
_project_root = Path(__file__).parent.parent
_config_path = _project_root / "config.json"
if _config_path.exists():
    with open(_config_path, "r", encoding="utf-8") as f:
        _app_config = json.load(f)
else:
    _app_config = {}

BOOKS_DIR = os.getenv("BOOKS_DIR", str(Path.home() / "BookBook"))


def ensure_books_dir():
    Path(BOOKS_DIR).mkdir(parents=True, exist_ok=True)


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_INTL_API_KEY = os.getenv("QWEN_INTL_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
SILICONFLOW_INTL_API_KEY = os.getenv("SILICONFLOW_INTL_API_KEY", "")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
QWEN_INTL_BASE_URL = os.getenv(
    "QWEN_INTL_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
MOONSHOT_BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
SILICONFLOW_INTL_BASE_URL = os.getenv(
    "SILICONFLOW_INTL_BASE_URL", "https://api.siliconflow.com/v1"
)

P2P_ENABLED = os.getenv("P2P_ENABLED", "true").lower() == "true"
P2P_PORT = int(os.getenv("P2P_PORT", str(_app_config.get("p2p_port", 47833))))
P2P_MAGIC = "EBOOK_P2P"
P2P_APP_ID = "com.bookbook.ebookgenerator"
P2P_VERSION = "1"
P2P_SHARE_TOKEN_EXPIRE = int(os.getenv("P2P_SHARE_TOKEN_EXPIRE", "86400"))

P2P_STUN_SERVERS = [
    "stun.l.google.com:19302",
    "stun1.l.google.com:19302",
    "stun2.l.google.com:19302",
]


PROVIDERS = {
    "anthropic": {
        "name": "Anthropic",
        "api_type": "anthropic",
        "default_base_url": "https://api.anthropic.com",
        "default_models": [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3.5-sonnet-20241022",
            "claude-3.5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ],
        "website": "https://console.anthropic.com/",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "name": "OpenAI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.openai.com/v1",
        "default_models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1",
            "o1-mini",
            "o3-mini",
        ],
        "website": "https://platform.openai.com/api-keys",
        "env_key": "OPENAI_API_KEY",
    },
    "deepseek": {
        "name": "DeepSeek",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.deepseek.com",
        "default_models": [
            "deepseek-chat",
            "deepseek-reasoner",
        ],
        "website": "https://platform.deepseek.com/",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "gemini": {
        "name": "Google Gemini",
        "api_type": "gemini",
        "default_base_url": "https://generativelanguage.googleapis.com",
        "default_models": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
        "website": "https://aistudio.google.com/apikey",
        "env_key": "GEMINI_API_KEY",
    },
    "zhipu": {
        "name": "Zhipu",
        "api_type": "openai_compatible",
        "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_models": [
            "glm-4-plus",
            "glm-4",
            "glm-4-flash",
            "glm-4-long",
        ],
        "website": "https://open.bigmodel.cn/",
        "env_key": "ZHIPU_API_KEY",
    },
    "qwen": {
        "name": "Qwen CN",
        "api_type": "openai_compatible",
        "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_models": [
            "qwen-max",
            "qwen-plus",
            "qwen-turbo",
            "qwen-long",
        ],
        "website": "https://dashscope.console.aliyun.com/",
        "env_key": "QWEN_API_KEY",
    },
    "qwen_intl": {
        "name": "Qwen International",
        "api_type": "openai_compatible",
        "default_base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "default_models": [
            "qwen-max",
            "qwen-plus",
            "qwen-turbo",
            "qwen-long",
        ],
        "website": "https://dashscope-intl.console.aliyun.com/",
        "env_key": "QWEN_INTL_API_KEY",
    },
    "kimi": {
        "name": "Moonshot CN",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.moonshot.cn/v1",
        "default_models": [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
        ],
        "website": "https://platform.moonshot.cn/",
        "env_key": "KIMI_API_KEY",
    },
    "moonshot": {
        "name": "Moonshot International",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.moonshot.ai/v1",
        "default_models": [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
        ],
        "website": "https://platform.kimi.com/",
        "env_key": "MOONSHOT_API_KEY",
    },
    "openrouter": {
        "name": "OpenRouter",
        "api_type": "openai_compatible",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_models": [
            "anthropic/claude-sonnet-4-20250514",
            "openai/gpt-4o",
            "google/gemini-2.5-pro-preview",
            "deepseek/deepseek-chat",
            "meta-llama/llama-3.1-405b-instruct",
        ],
        "website": "https://openrouter.ai/settings/keys",
    },
    "xai": {
        "name": "xAI (Grok)",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.x.ai/v1",
        "default_models": [
            "grok-3",
            "grok-3-mini",
            "grok-2",
        ],
        "website": "https://console.x.ai/",
    },
    "groq": {
        "name": "Groq",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.groq.com/openai/v1",
        "default_models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        "website": "https://console.groq.com/",
    },
    "together": {
        "name": "Together AI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.together.xyz/v1",
        "default_models": [
            "meta-llama/Llama-3-70b-chat-hf",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "togethercomputer/RedPajama-INCITE-7B-Chat",
        ],
        "website": "https://api.together.xyz/",
    },
    "fireworks": {
        "name": "Fireworks AI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.fireworks.ai/inference/v1",
        "default_models": [
            "accounts/fireworks/models/llama-v3p1-70b-instruct",
            "accounts/fireworks/models/mixtral-8x7b-instruct",
        ],
        "website": "https://app.fireworks.ai/",
    },
    "cerebras": {
        "name": "Cerebras",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.cerebras.ai/v1",
        "default_models": [
            "llama-3.3-70b",
            "llama-3.1-8b",
        ],
        "website": "https://inference.cerebras.ai/",
    },
    "deepinfra": {
        "name": "Deep Infra",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.deepinfra.com/v1/openai",
        "default_models": [
            "meta-llama/Llama-3.3-70B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "mixtralai/Mixtral-8x7B-Instruct-v0.1",
        ],
        "website": "https://deepinfra.com/",
    },
    "huggingface": {
        "name": "Hugging Face",
        "api_type": "openai_compatible",
        "default_base_url": "https://api-inference.huggingface.co/v1",
        "default_models": [
            "meta-llama/Llama-3.3-70B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
        ],
        "website": "https://huggingface.co/settings/tokens",
    },
    "nvidia": {
        "name": "NVIDIA (NIM)",
        "api_type": "openai_compatible",
        "default_base_url": "https://integrate.api.nvidia.com/v1",
        "default_models": [
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.1-405b-instruct",
        ],
        "website": "https://build.nvidia.com/",
    },
    "cloudflare": {
        "name": "Cloudflare Workers AI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1",
        "default_models": [
            "@cf/meta/llama-3.1-8b-instruct",
            "@cf/mistral/mistral-7b-instruct-v0.1",
        ],
        "website": "https://dash.cloudflare.com/",
    },
    "minimax": {
        "name": "MiniMax",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.minimax.chat/v1",
        "default_models": [
            "MiniMax-Text-01",
            "abab6.5s-chat",
        ],
        "website": "https://platform.minimax.io/",
    },
    "ollama": {
        "name": "Ollama (本地)",
        "api_type": "openai_compatible",
        "default_base_url": "http://localhost:11434/v1",
        "default_models": [
            "llama3.1",
            "qwen2.5",
            "mistral",
            "codellama",
        ],
        "website": "https://ollama.com/",
    },
    "azure_openai": {
        "name": "Azure OpenAI",
        "api_type": "openai_compatible",
        "default_base_url": "https://{RESOURCE_NAME}.openai.azure.com/openai",
        "default_models": [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-35-turbo",
        ],
        "website": "https://portal.azure.com/",
    },
    "mistral": {
        "name": "Mistral AI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.mistral.ai/v1",
        "default_models": [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mistral-nemo",
        ],
        "website": "https://console.mistral.ai/",
    },
    "perplexity": {
        "name": "Perplexity",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.perplexity.ai",
        "default_models": [
            "sonar",
            "sonar-pro",
            "sonar-reasoning",
        ],
        "website": "https://www.perplexity.ai/settings/api",
    },
    "cohere": {
        "name": "Cohere",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.cohere.ai/v2",
        "default_models": [
            "command-r-plus",
            "command-r",
        ],
        "website": "https://dashboard.cohere.com/api-keys",
    },
    "sambanova": {
        "name": "SambaNova",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.sambanova.ai/v1",
        "default_models": [
            "Meta-Llama-3.3-70B-Instruct",
            "Qwen2.5-72B-Instruct",
        ],
        "website": "https://cloud.sambanova.ai/",
    },
    "siliconflow": {
        "name": "SiliconFlow CN",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_models": [
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-V3",
            "meta-llama/Llama-3.3-70B-Instruct",
        ],
        "website": "https://cloud.siliconflow.cn/",
    },
    "siliconflow_intl": {
        "name": "SiliconFlow International",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.siliconflow.com/v1",
        "default_models": [
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-V3",
            "meta-llama/Llama-3.3-70B-Instruct",
        ],
        "website": "https://siliconflow.com/",
        "env_key": "SILICONFLOW_INTL_API_KEY",
    },
    "baichuan": {
        "name": "Baichuan",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.baichuan-api.com/v1",
        "default_models": [
            "Baichuan4",
            "Baichuan3-Turbo",
        ],
        "website": "https://platform.baichuan-ai.com/",
    },
    "volcengine": {
        "name": "Volcengine",
        "api_type": "openai_compatible",
        "default_base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_models": [
            "doubao-1.5-pro-32k",
            "doubao-1.5-lite-32k",
        ],
        "website": "https://console.volcengine.com/ark",
    },
    "yi": {
        "name": "Yi",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.lingyiwanwu.com/v1",
        "default_models": [
            "yi-large",
            "yi-medium",
            "yi-spark",
        ],
        "website": "https://platform.lingyiwanwu.com/",
    },
    "dify": {
        "name": "Dify",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.dify.ai/v1",
        "default_models": [
            "dify",
        ],
        "website": "https://cloud.dify.ai/",
    },
    "lmstudio": {
        "name": "LM Studio (本地)",
        "api_type": "openai_compatible",
        "default_base_url": "http://localhost:1234/v1",
        "default_models": [],
        "website": "https://lmstudio.ai/",
    },
    "venice": {
        "name": "Venice AI",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.venice.ai/api/v1",
        "default_models": [
            "llama-3.3-70b",
            "qwen-2.5-72b",
        ],
        "website": "https://venice.ai/",
    },
    "nebius": {
        "name": "Nebius",
        "api_type": "openai_compatible",
        "default_base_url": "https://api.studio.nebius.ai/v1",
        "default_models": [
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
        ],
        "website": "https://nebius.ai/",
    },
    "custom": {
        "name": "自定义 (Custom)",
        "api_type": "openai_compatible",
        "default_base_url": "",
        "default_models": [],
        "website": "",
    },
}

PROVIDER_CATEGORIES = [
    {
        "id": "major",
        "name": "主流服务商",
        "providers": ["anthropic", "openai", "deepseek", "gemini", "mistral"],
    },
    {
        "id": "chinese_domestic",
        "name": "国内服务商·国内源",
        "providers": [
            "zhipu",
            "qwen",
            "kimi",
            "volcengine",
            "siliconflow",
        ],
    },
    {
        "id": "chinese_international",
        "name": "国内服务商·国际源",
        "providers": [
            "baichuan",
            "yi",
            "moonshot",
            "qwen_intl",
            "siliconflow_intl",
        ],
    },
    {
        "id": "gateway",
        "name": "聚合网关",
        "providers": ["openrouter", "azure_openai", "dify"],
    },
    {
        "id": "fast_inference",
        "name": "快速推理",
        "providers": [
            "groq",
            "cerebras",
            "together",
            "fireworks",
            "deepinfra",
            "sambanova",
        ],
    },
    {
        "id": "specialized",
        "name": "专业平台",
        "providers": [
            "xai",
            "perplexity",
            "cohere",
            "nvidia",
            "minimax",
            "huggingface",
        ],
    },
    {
        "id": "local",
        "name": "本地部署",
        "providers": ["ollama", "lmstudio"],
    },
    {
        "id": "other",
        "name": "更多",
        "providers": ["cloudflare", "venice", "nebius", "custom"],
    },
]


def get_local_ip() -> str:
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def get_all_ips() -> list:
    import socket

    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        ips.append(ip)
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        for addr in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = addr[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass

    if not ips:
        ips.append("127.0.0.1")

    return ips


def get_public_ip_via_stun() -> str:
    import socket
    import struct
    import random

    stun_servers = P2P_STUN_SERVERS

    for server_addr in stun_servers:
        try:
            host, port = server_addr.split(":")
            port = int(port)

            tid = random.getrandbits(96).to_bytes(12, "big")
            msg = (
                struct.pack(">HH", 0x0001, 0x0000) + struct.pack(">I", 0x2112A442) + tid
            )

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.sendto(msg, (host, port))
            data, _ = sock.recvfrom(1024)
            sock.close()

            if len(data) < 20:
                continue

            msg_type = struct.unpack(">H", data[0:2])[0]
            msg_len = struct.unpack(">H", data[2:4])[0]
            cookie = struct.unpack(">I", data[4:8])[0]

            if cookie != 0x2112A442:
                continue
            if msg_type & 0x0110 != 0x0100:
                continue

            attrs = data[20:]
            idx = 0
            while idx < len(attrs):
                if idx + 4 > len(attrs):
                    break
                attr_type = struct.unpack(">H", attrs[idx : idx + 2])[0]
                attr_len = struct.unpack(">H", attrs[idx + 2 : idx + 4])[0]
                padding = (4 - (attr_len % 4)) % 4
                attr_value = attrs[idx + 4 : idx + 4 + attr_len]

                if attr_type == 0x0001 or attr_type == 0x0020:
                    if attr_type == 0x0001 and attr_len >= 8:
                        family = struct.unpack(">H", attr_value[0:2])[0]
                        if family == 0x01:
                            ip_bytes = attr_value[4:8]
                            ip = ".".join(str(b) for b in ip_bytes)
                            return ip
                    elif attr_type == 0x0020 and attr_len >= 8:
                        family = struct.unpack(">H", attr_value[0:2])[0]
                        if family == 0x01:
                            xip = struct.unpack(">I", attr_value[4:8])[0]
                            ip = struct.unpack(">I", data[4:8])[0]
                            ip = ip ^ xip
                            ip = ".".join(
                                str((ip >> (8 * i)) & 0xFF) for i in [3, 2, 1, 0]
                            )
                            return ip

                idx += 4 + attr_len + padding

        except Exception:
            continue

    return None


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ebooks.db")
