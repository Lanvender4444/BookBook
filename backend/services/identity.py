import hashlib
import uuid
import getmac
import json
import platform
from pathlib import Path

# 用户信息文件路径
USER_INFO_FILE = Path.home() / ".ebook-generator" / "user.json"

def get_mac_address() -> str:
    """获取 MAC 地址"""
    mac = getmac.get_mac_address()
    if not mac or mac == "00:00:00:00:00:00":
        # 备用方案：使用 uuid 获取网络信息
        mac = hex(uuid.getnode())
    return mac

def load_user_info() -> dict:
    """加载用户信息"""
    USER_INFO_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if USER_INFO_FILE.exists():
        try:
            with open(USER_INFO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    
    # 初始化用户编号
    return {"user_number": 1}

def save_user_info(info: dict):
    """保存用户信息"""
    USER_INFO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

def set_user_number(number: int):
    """设置用户编号"""
    info = load_user_info()
    info["user_number"] = number
    save_user_info(info)

def generate_user_id() -> str:
    """
    生成唯一用户 ID
    使用完整 36 位 UUID，持久化保存，每次调用返回同一 ID
    """
    info = load_user_info()
    if "user_id" not in info:
        info["user_id"] = str(uuid.uuid4())
        save_user_info(info)
    return info["user_id"]

def get_user_id() -> str:
    """获取用户 ID（确保用户信息文件存在）"""
    return generate_user_id()

def get_machine_info() -> dict:
    """获取机器信息（用于调试和展示）"""
    return {
        "mac_address": get_mac_address(),
        "user_number": load_user_info().get("user_number", 1),
        "user_id": generate_user_id(),
        "platform": platform.system(),
        "hostname": platform.node()
    }
