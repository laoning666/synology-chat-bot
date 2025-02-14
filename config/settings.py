# settings.py
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

from typing import Dict, Any
def get_env_int(key: str, default: int) -> int:
    """获取整数类型的环境变量"""
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default

def get_env_float(key: str, default: float) -> float:
    """获取浮点数类型的环境变量"""
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default

def get_env_bool(key: str, default: bool) -> bool:
    """获取布尔类型的环境变量"""
    return str(os.getenv(key, default)).lower() in ('true', '1', 'yes')

# ChatGPT API Configuration
CHAT_API: Dict[str, Any] = {
    'url': os.getenv('CHAT_API_URL', ''),
    'api_key': os.getenv('CHAT_API_KEY', ''),
    'model': os.getenv('CHAT_API_MODEL', ''),
    'temperature': get_env_float('CHAT_API_TEMPERATURE', 0.7),
    'max_tokens': get_env_int('CHAT_API_MAX_TOKENS', 4096),
    'system_prompt': os.getenv('CHAT_API_SYSTEM_PROMPT', '你是一个智能助手，可以帮助用户解答问题。')
}

# Synology Chat Configuration
SYNOLOGY: Dict[str, str] = {
    'incoming_webhook_url': os.getenv('SYNOLOGY_INCOMING_WEBHOOK_URL', ''),
    'outgoing_webhook_token': os.getenv('SYNOLOGY_OUTGOING_WEBHOOK_TOKEN', ''),
}

# Server Configuration
SERVER: Dict[str, Any] = {
    'host': os.getenv('SERVER_HOST', '0.0.0.0'),
    'port': get_env_int('SERVER_PORT', 8008),
    'debug': get_env_bool('SERVER_DEBUG', False)
}

# Conversation Settings
CONVERSATION: Dict[str, Any] = {
    'max_history': get_env_int('CONVERSATION_MAX_HISTORY', 10),
    'timeout': get_env_int('CONVERSATION_TIMEOUT', 1800),
    'typing_text': os.getenv('CONVERSATION_TYPING_TEXT', '...')
}

# HTTP Client Settings
HTTP: Dict[str, int] = {
    'timeout': get_env_int('HTTP_TIMEOUT', 30),
    'max_retries': get_env_int('HTTP_MAX_RETRIES', 3)
}