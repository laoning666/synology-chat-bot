# src/providers/openai_provider.py
"""
OpenAI 兼容 API Provider
支持所有兼容 OpenAI Chat Completions API 格式的服务
"""
import time
import requests
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import ChatProvider


class OpenAIProvider(ChatProvider):
    """OpenAI 兼容 API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._init_session()

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

    def _build_messages(self, context: Optional[Any]) -> List[Dict[str, str]]:
        """
        构建 OpenAI 格式的消息列表

        Args:
            context: Conversation 对象或其他上下文

        Returns:
            消息列表
        """
        system_prompt = self.chat_config.get('system_prompt', '')

        # 如果 context 是 Conversation 对象，使用其方法获取上下文
        if context and hasattr(context, 'get_context'):
            return context.get_context(system_prompt)

        # 否则返回只包含系统提示的列表
        if system_prompt:
            return [{"role": "system", "content": system_prompt}]
        return []

    def send_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Any] = None
    ) -> Optional[str]:
        """
        发送消息到 OpenAI 兼容 API 并获取响应

        Args:
            user_id: 用户唯一标识
            message: 用户发送的消息内容
            context: Conversation 对象

        Returns:
            AI 的响应文本，如果失败则返回 None
        """
        try:
            messages = self._build_messages(context)

            headers = {
                "Authorization": f"Bearer {self.get_api_key()}",
                "Content-Type": "application/json"
            }

            json_data = {
                "model": self.chat_config.get('model', ''),
                "messages": messages,
                "temperature": self.chat_config.get('temperature', 0.7),
                "max_tokens": self.chat_config.get('max_tokens', 4096)
            }

            response = self.session.post(
                self.get_api_url(),
                headers=headers,
                json=json_data,
                timeout=self.get_timeout()
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"[OpenAIProvider] Request failed: {str(e)}")
            return None
        except (KeyError, IndexError) as e:
            print(f"[OpenAIProvider] Response parsing failed: {str(e)}")
            return None
        except Exception as e:
            print(f"[OpenAIProvider] Unexpected error: {str(e)}")
            return None

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 OpenAI API 连接

        Returns:
            测试结果字典
        """
        print("🧪 Testing OpenAI-compatible API connection...")

        test_messages = [
            {
                "role": "system",
                "content": "You are a test assistant, please reply briefly."
            },
            {
                "role": "user",
                "content": "Please reply 'API test successful' to confirm the connection is working."
            }
        ]

        request_data = {
            "model": self.chat_config.get('model', ''),
            "messages": test_messages,
            "temperature": 0.1,
            "max_tokens": 50
        }

        headers = {
            "Authorization": f"Bearer {self.get_api_key()}",
            "Content-Type": "application/json"
        }

        try:
            print(f"   📡 API URL: {self.get_api_url()}")
            print(f"   🤖 Model: {self.chat_config.get('model', '')}")
            print(f"   💬 Test message: {test_messages[-1]['content']}")

            start_time = time.time()

            response = requests.post(
                self.get_api_url(),
                headers=headers,
                json=request_data,
                timeout=self.get_timeout()
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content'].strip()

                    print(f"   ✅ API response successful (time: {response_time:.2f}s)")
                    print(f"   🤖 AI reply: {ai_response}")

                    if 'usage' in result:
                        print(f"   📊 Token usage: {result['usage']}")

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "response": ai_response,
                        "response_time": response_time,
                        "usage": result.get('usage', {}),
                        "model": result.get('model', self.chat_config.get('model', ''))
                    }
                else:
                    print("   ❌ API response format error: missing choices field")
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
