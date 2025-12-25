# src/utils/logger.py
"""
日志工具模块
提供统一的日志配置和格式化
"""
import os
import sys
import logging
from typing import Optional
from config.settings import ENVIRONMENT, is_development


def setup_logger(
    name: str = "synology_chatbot",
    level: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别（DEBUG, INFO, WARNING, ERROR）

    Returns:
        配置好的 Logger 实例
    """
    # 从环境变量获取日志级别，默认根据环境决定
    if level is None:
        level = os.getenv('LOG_LEVEL', 'DEBUG' if is_development() else 'INFO')

    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 日志格式
    if is_development():
        # 开发环境：更详细的格式
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        # 生产环境：简洁格式
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 全局日志实例
logger = setup_logger()


def log_request(method: str, url: str, **kwargs) -> None:
    """记录 HTTP 请求"""
    logger.debug(f"📤 {method} {url}")
    if kwargs.get('headers'):
        # 隐藏敏感信息
        safe_headers = {k: '***' if 'auth' in k.lower() or 'key' in k.lower() else v
                        for k, v in kwargs['headers'].items()}
        logger.debug(f"   Headers: {safe_headers}")


def log_response(status_code: int, response_time: float, **kwargs) -> None:
    """记录 HTTP 响应"""
    status_emoji = "✅" if 200 <= status_code < 300 else "❌"
    logger.debug(f"📥 {status_emoji} Status: {status_code} ({response_time:.2f}s)")


def log_error(error_type: str, message: str, **kwargs) -> None:
    """记录错误信息"""
    logger.error(f"❌ [{error_type}] {message}")
    if kwargs.get('details'):
        logger.error(f"   Details: {kwargs['details']}")
    if kwargs.get('suggestion'):
        logger.info(f"💡 Suggestion: {kwargs['suggestion']}")


def log_info(message: str, **kwargs) -> None:
    """记录一般信息"""
    logger.info(message)


def log_debug(message: str, **kwargs) -> None:
    """记录调试信息"""
    logger.debug(message)


def log_warning(message: str, **kwargs) -> None:
    """记录警告信息"""
    logger.warning(f"⚠️  {message}")
