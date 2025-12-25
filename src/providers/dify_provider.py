# src/providers/dify_provider.py
"""
Dify API Provider
支持 Dify 平台的 Chat API
"""
import time
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import ChatProvider


class DifyProvider(ChatProvider):
    """Dify API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._init_session()
        # 存储每个用户的 Dify conversation_id
        self.conversation_ids: Dict[str, str] = {}

    def _init_session(self) -> None:
        """初始化 HTTP Session 并配置重试策略"""
        self.session = requests.Session()
        max_retries = self.http_config.get('max_retries', 3)
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_chat_endpoint(self) -> str:
        """
        获取 Dify Chat API 端点

        Returns:
            完整的 chat-messages API URL
        """
        base_url = self.get_api_url().rstrip('/')
        # 如果 URL 已经包含 chat-messages，直接返回
        if base_url.endswith('/chat-messages'):
            return base_url
        # 如果 URL 以 /v1 结尾，追加 /chat-messages
        if base_url.endswith('/v1'):
            return f"{base_url}/chat-messages"
        # 否则追加完整路径
        return f"{base_url}/v1/chat-messages"

    def _get_conversation_id(self, user_id: str) -> Optional[str]:
        """获取用户的 conversation_id"""
        return self.conversation_ids.get(user_id)

    def _set_conversation_id(self, user_id: str, conversation_id: str) -> None:
        """设置用户的 conversation_id"""
        self.conversation_ids[user_id] = conversation_id

    def _clear_conversation_id(self, user_id: str) -> None:
        """清除用户的 conversation_id（用于开始新对话）"""
        if user_id in self.conversation_ids:
            del self.conversation_ids[user_id]

    def send_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Any] = None
    ) -> Optional[str]:
        """
        发送消息到 Dify API 并获取响应

        Args:
            user_id: 用户唯一标识
            message: 用户发送的消息内容
            context: Conversation 对象（Dify 使用服务端会话管理，此参数用于兼容）

        Returns:
            AI 的响应文本，如果失败则返回 None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.get_api_key()}",
                "Content-Type": "application/json"
            }

            # 构建 Dify API 请求体
            json_data: Dict[str, Any] = {
                "inputs": {},
                "query": message,
                "response_mode": "blocking",
                "user": user_id
            }

            # 如果有现有会话，添加 conversation_id
            conversation_id = self._get_conversation_id(user_id)
            if conversation_id:
                json_data["conversation_id"] = conversation_id

            response = self.session.post(
                self._get_chat_endpoint(),
                headers=headers,
                json=json_data,
                timeout=self.get_timeout()
            )
            response.raise_for_status()

            result = response.json()

            # 保存返回的 conversation_id，用于后续对话
            if 'conversation_id' in result:
                self._set_conversation_id(user_id, result['conversation_id'])

            # Dify 响应中的 answer 字段包含 AI 回复
            return result.get('answer', '')

        except requests.exceptions.RequestException as e:
            print(f"[DifyProvider] Request failed: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            print(f"[DifyProvider] Response parsing failed: {str(e)}")
            return None
        except Exception as e:
            print(f"[DifyProvider] Unexpected error: {str(e)}")
            return None

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 Dify API 连接

        Returns:
            测试结果字典
        """
        print("🧪 Testing Dify API connection...")

        headers = {
            "Authorization": f"Bearer {self.get_api_key()}",
            "Content-Type": "application/json"
        }

        test_data = {
            "inputs": {},
            "query": "Please reply 'API test successful' to confirm the connection is working.",
            "response_mode": "blocking",
            "user": "test_user"
        }

        try:
            endpoint = self._get_chat_endpoint()
            print(f"   📡 API URL: {endpoint}")
            print(f"   💬 Test message: {test_data['query']}")

            start_time = time.time()

            response = requests.post(
                endpoint,
                headers=headers,
                json=test_data,
                timeout=self.get_timeout()
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if 'answer' in result:
                    ai_response = result['answer'].strip()

                    print(f"   ✅ API response successful (time: {response_time:.2f}s)")
                    print(f"   🤖 AI reply: {ai_response}")

                    # Dify 返回的 metadata
                    if 'metadata' in result:
                        print(f"   📊 Metadata: {result['metadata']}")

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "response": ai_response,
                        "response_time": response_time,
                        "conversation_id": result.get('conversation_id', ''),
                        "message_id": result.get('message_id', '')
                    }
                else:
                    print("   ❌ API response format error: missing answer field")
                    return {
                        "success": False,
                        "provider": self.provider_name,
                        "error": "Invalid response format",
                        "details": result
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except Exception:
                    error_msg += f": {response.text}"

                print(f"   ❌ API request failed: {error_msg}")
                return {
                    "success": False,
                    "provider": self.provider_name,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            print(f"   ❌ API request timeout (>{self.get_timeout()}s)")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to API server")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Connection failed"
            }
        except Exception as e:
            print(f"   ❌ API test exception: {str(e)}")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": str(e)
            }

    def clear_user_conversation(self, user_id: str) -> None:
        """
        清除用户的会话（开始新对话时使用）

        Args:
            user_id: 用户唯一标识
        """
        self._clear_conversation_id(user_id)
        print(f"[DifyProvider] Cleared conversation for user: {user_id}")
