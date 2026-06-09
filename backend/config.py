import os
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 书籍保存路径
BOOKS_DIR = os.getenv("BOOKS_DIR", str(Path.home() / "BookBook"))

def ensure_books_dir():
    """确保书籍保存目录存在"""
    Path(BOOKS_DIR).mkdir(parents=True, exist_ok=True)

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
P2P_PORT = int(os.getenv("P2P_PORT", "47833"))
P2P_MAGIC = "EBOOK_P2P"
P2P_APP_ID = "com.bookbook.ebookgenerator"
P2P_VERSION = "1"
P2P_SHARE_TOKEN_EXPIRE = int(os.getenv("P2P_SHARE_TOKEN_EXPIRE", "86400"))

# STUN Servers for NAT traversal
P2P_STUN_SERVERS = [
    "stun.l.google.com:19302",
    "stun1.l.google.com:19302",
    "stun2.l.google.com:19302",
]


def get_local_ip() -> str:
    """获取本机局域网 IP 地址"""
    import socket
    try:
        # 通过连接外部地址来获取本机 IP
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
    """获取所有可用的 IP 地址（局域网 + 公网）"""
    import socket
    ips = []
    try:
        # 首选 IP（通过外网连接获取）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        ips.append(ip)
    except Exception:
        pass

    # 获取所有网络接口的 IP
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
    """通过 STUN 服务器获取公网 IP 地址（用于 NAT 穿透）"""
    import socket
    import struct
    import random

    stun_servers = P2P_STUN_SERVERS

    for server_addr in stun_servers:
        try:
            host, port = server_addr.split(':')
            port = int(port)

            # 创建 STUN Binding Request
            # STUN Message Type: Binding Request (0x0001)
            # Message Cookie: 0x2112A442
            # 12 bytes header + 8 bytes Change Request attribute
            tid = random.getrandbits(96).to_bytes(12, 'big')
            msg = struct.pack('>HH', 0x0001, 0x0000) + struct.pack('>I', 0x2112A442) + tid

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.sendto(msg, (host, port))
            data, _ = sock.recvfrom(1024)
            sock.close()

            if len(data) < 20:
                continue

            # 解析 STUN Response
            msg_type = struct.unpack('>H', data[0:2])[0]
            msg_len = struct.unpack('>H', data[2:4])[0]
            cookie = struct.unpack('>I', data[4:8])[0]

            if cookie != 0x2112A442:
                continue
            if msg_type & 0x0110 != 0x0100:  # not a success response
                continue

            # 解析 attributes
            attrs = data[20:]
            idx = 0
            while idx < len(attrs):
                if idx + 4 > len(attrs):
                    break
                attr_type = struct.unpack('>H', attrs[idx:idx+2])[0]
                attr_len = struct.unpack('>H', attrs[idx+2:idx+4])[0]
                padding = (4 - (attr_len % 4)) % 4
                attr_value = attrs[idx+4:idx+4+attr_len]

                if attr_type == 0x0001 or attr_type == 0x0020:  # MAPPED-ADDRESS or XOR-MAPPED-ADDRESS
                    if attr_type == 0x0001 and attr_len >= 8:
                        # MAPPED-ADDRESS: family(2) + port(2) + ip(4)
                        family = struct.unpack('>H', attr_value[0:2])[0]
                        if family == 0x01:  # IPv4
                            ip_bytes = attr_value[4:8]
                            ip = '.'.join(str(b) for b in ip_bytes)
                            return ip
                    elif attr_type == 0x0020 and attr_len >= 8:
                        # XOR-MAPPED-ADDRESS
                        family = struct.unpack('>H', attr_value[0:2])[0]
                        if family == 0x01:
                            xport = struct.unpack('>H', attr_value[2:4])[0]
                            xip = struct.unpack('>I', attr_value[4:8])[0]
                            ip = struct.unpack('>I', data[4:8])[0]  # cookie
                            ip = ip ^ xip
                            ip = '.'.join(str((ip >> (8 * i)) & 0xFF) for i in [3, 2, 1, 0])
                            return ip

                idx += 4 + attr_len + padding

        except Exception:
            continue

    return None

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ebooks.db")
