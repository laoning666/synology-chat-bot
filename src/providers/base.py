# src/providers/base.py
"""
Chat Provider 抽象基类
定义所有 Chat API Provider 必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ChatProvider(ABC):
    """Chat API Provider 抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Provider

        Args:
            config: 完整的应用配置字典，包含 CHAT_API, HTTP 等配置
        """
        self.config = config
        self.chat_config = config.get('CHAT_API', {})
        self.http_config = config.get('HTTP', {})

    @abstractmethod
    def send_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Any] = None
    ) -> Optional[str]:
        """
        发送消息并获取 AI 响应

        Args:
            user_id: 用户唯一标识
            message: 用户发送的消息内容
            context: 上下文对象（如 Conversation 实例）

        Returns:
            AI 的响应文本，如果失败则返回 None
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        测试 API 连接是否正常

        Returns:
            包含测试结果的字典:
            - success: bool - 是否成功
            - response: str - 成功时的响应内容
            - error: str - 失败时的错误信息
            - response_time: float - 响应时间（秒）
            - 其他 provider 特定的信息
        """
        pass

    @property
    def provider_name(self) -> str:
        """返回 Provider 名称"""
        return self.__class__.__name__

    def get_api_url(self) -> str:
        """获取 API URL"""
        return self.chat_config.get('url', '')

    def get_api_key(self) -> str:
        """获取 API Key"""
        return self.chat_config.get('api_key', '')

    def get_timeout(self) -> int:
        """获取 HTTP 超时时间"""
        return self.http_config.get('timeout', 30)
