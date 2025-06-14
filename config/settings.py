# settings.py
import os
from dotenv import load_dotenv
from typing import Dict, Any

# 获取环境类型
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# 根据环境加载配置文件
if ENVIRONMENT == 'development':
    if os.path.exists('.env.dev'):
        load_dotenv('.env.dev')
    else:
        load_dotenv('.env')
elif ENVIRONMENT == 'testing':
    load_dotenv('.env.test')
else:
    load_dotenv()

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

# Chat API Configuration
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

def get_server_config() -> Dict[str, Any]:
    """获取服务器配置"""
    return {
        'host': '0.0.0.0',
        'port': 8108,
        'debug': ENVIRONMENT == 'development'
    }

def is_development() -> bool:
    """判断是否为开发环境"""
    return ENVIRONMENT == 'development'

def is_production() -> bool:
    """判断是否为生产环境"""
    return ENVIRONMENT == 'production'