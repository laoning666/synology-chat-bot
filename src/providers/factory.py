# src/providers/factory.py
"""
Provider 工厂类
根据配置创建对应的 Chat Provider 实例
"""
from typing import Dict, Any

from .base import ChatProvider
from .openai_provider import OpenAIProvider
from .dify_provider import DifyProvider


class ProviderFactory:
    """Provider 工厂类"""

    # 支持的 Provider 类型映射
    PROVIDER_MAP: Dict[str, type] = {
        'openai': OpenAIProvider,
        'dify': DifyProvider,
    }

    @classmethod
    def create(cls, config: Dict[str, Any]) -> ChatProvider:
        """
        根据配置创建 Provider 实例

        Args:
            config: 完整的应用配置字典

        Returns:
            ChatProvider 实例

        Raises:
            ValueError: 当指定的 provider 类型不支持时
        """
        chat_config = config.get('CHAT_API', {})
        provider_type = chat_config.get('type', 'openai').lower()

        if provider_type not in cls.PROVIDER_MAP:
            supported = ', '.join(cls.PROVIDER_MAP.keys())
            raise ValueError(
                f"Unsupported provider type: '{provider_type}'. "
                f"Supported types: {supported}"
            )

        provider_class = cls.PROVIDER_MAP[provider_type]
        print(f"📦 Creating {provider_class.__name__} instance...")
        return provider_class(config)

    @classmethod
    def get_supported_types(cls) -> list:
        """
        获取支持的 Provider 类型列表

        Returns:
            支持的类型名称列表
        """
        return list(cls.PROVIDER_MAP.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        注册新的 Provider 类型（用于扩展）

        Args:
            name: Provider 类型名称
            provider_class: Provider 类（必须继承自 ChatProvider）

        Raises:
            TypeError: 当 provider_class 不是 ChatProvider 的子类时
        """
        if not issubclass(provider_class, ChatProvider):
            raise TypeError(
                f"{provider_class.__name__} must be a subclass of ChatProvider"
            )
        cls.PROVIDER_MAP[name.lower()] = provider_class
        print(f"📦 Registered new provider type: {name}")
