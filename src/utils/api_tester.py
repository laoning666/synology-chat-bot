# src/utils/api_tester.py
"""
API测试器 / API Tester
使用 Provider 抽象层进行 API 连接测试
"""
from typing import Dict, Any
from ..providers.factory import ProviderFactory


class APITester:
    """API测试器 / API Tester"""

    def __init__(self, config: Dict[str, Any]):
        """初始化API测试器 / Initialize API tester"""
        self.config = config
        self.chat_config = config.get('CHAT_API', {})
        self.http_config = config.get('HTTP', {})
        # 创建 Provider 实例
        self.provider = ProviderFactory.create(config)

    def test_chat_api(self) -> Dict[str, Any]:
        """
        测试聊天API是否能正常对话 / Test if chat API can handle conversation normally

        使用 Provider 的 test_connection 方法进行测试，
        支持 OpenAI 和 Dify 等多种 API 类型。
        """
        print(f"🧪 Testing {self.chat_config.get('type', 'openai').upper()} API connection...")
        return self.provider.test_connection()

