import hashlib
import uuid
import getmac

def generate_user_id() -> str:
    mac = getmac.get_mac_address() or "00:00:00:00:00:00"
    machine_id = str(uuid.getnode())
    raw = f"{mac}-{machine_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
