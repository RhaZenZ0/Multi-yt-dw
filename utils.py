import re
import psutil

def sanitize_filename(name: str, replacement: str = "_") -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', replacement, name)
    sanitized = sanitized.strip()
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def get_cpu_percent():
    return psutil.cpu_percent(interval=None)
  
