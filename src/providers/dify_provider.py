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
from ..utils.logger import logger, log_request, log_response, log_error


class DifyProvider(ChatProvider):
    """Dify API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._init_session()
        # 存储每个用户的 Dify conversation_id
        self.conversation_ids: Dict[str, str] = {}
        logger.debug("DifyProvider initialized")

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
        logger.debug(f"HTTP session initialized with max_retries={max_retries}")

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
        logger.debug(f"[User:{user_id}] Set conversation_id: {conversation_id[:8]}...")

    def _clear_conversation_id(self, user_id: str) -> None:
        """清除用户的 conversation_id（用于开始新对话）"""
        if user_id in self.conversation_ids:
            del self.conversation_ids[user_id]
            logger.debug(f"[User:{user_id}] Cleared conversation_id")

    def _get_http_error_suggestion(self, status_code: int) -> str:
        """根据 HTTP 状态码返回建议"""
        suggestions = {
            400: "Check request format, 'query' field is required",
            401: "Check CHAT_API_KEY is a valid Dify app API key (starts with 'app-')",
            403: "API key may lack permissions for this Dify app",
            404: "Check CHAT_API_URL points to a valid Dify instance",
            429: "Rate limit exceeded, wait and retry",
            500: "Dify server error, check Dify logs",
            502: "Dify gateway error, try again later",
            503: "Dify service unavailable, try again later",
        }
        return suggestions.get(status_code, "Check Dify API configuration")

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
        logger.info(f"[User:{user_id}] Sending message to Dify API...")
        start_time = time.time()

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
                logger.debug(f"[User:{user_id}] Continuing conversation: {conversation_id[:8]}...")
            else:
                logger.debug(f"[User:{user_id}] Starting new conversation")

            endpoint = self._get_chat_endpoint()
            log_request("POST", endpoint, headers=headers)

            response = self.session.post(
                endpoint,
                headers=headers,
                json=json_data,
                timeout=self.get_timeout()
            )

            response_time = time.time() - start_time
            log_response(response.status_code, response_time)

            response.raise_for_status()

            result = response.json()

            # 保存返回的 conversation_id，用于后续对话
            if 'conversation_id' in result:
                self._set_conversation_id(user_id, result['conversation_id'])

            ai_response = result.get('answer', '')
            logger.info(f"[User:{user_id}] Response received in {response_time:.2f}s "
                       f"(message_id: {result.get('message_id', 'N/A')[:8]}...)")

            return ai_response

        except requests.exceptions.Timeout:
            log_error("Timeout", f"Request timeout after {self.get_timeout()}s",
                     suggestion="Increase HTTP_TIMEOUT or check Dify server performance")
            return None
        except requests.exceptions.ConnectionError as e:
            log_error("Connection", f"Cannot connect to Dify server: {self._get_chat_endpoint()}",
                     details=str(e),
                     suggestion="Check CHAT_API_URL is correct and Dify server is running")
            return None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 'Unknown'
            error_body = ""
            try:
                error_body = e.response.json() if e.response else {}
            except Exception:
                error_body = e.response.text if e.response else str(e)

            log_error("HTTP", f"Status {status_code}: {error_body}",
                     suggestion=self._get_http_error_suggestion(status_code))
            return None
        except (KeyError, ValueError) as e:
            log_error("Parse", f"Failed to parse Dify response: {str(e)}",
                     suggestion="Dify response format may be invalid")
            return None
        except Exception as e:
            log_error("Unexpected", str(e))
            return None

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 Dify API 连接

        Returns:
            测试结果字典
        """
        logger.info("=" * 50)
        logger.info("🧪 Testing Dify API connection...")
        logger.info("=" * 50)

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

        endpoint = self._get_chat_endpoint()

        # 配置信息
        logger.info(f"📡 API URL: {endpoint}")
        logger.info(f"⏱️  Timeout: {self.get_timeout()}s")
        logger.info(f"🔄 Max Retries: {self.http_config.get('max_retries', 3)}")
        logger.info(f"📝 Response Mode: blocking")

        try:
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

                    logger.info(f"✅ API response successful (time: {response_time:.2f}s)")
                    logger.info(f"🤖 AI reply: {ai_response}")
                    logger.info(f"📋 Conversation ID: {result.get('conversation_id', 'N/A')}")
                    logger.info(f"📋 Message ID: {result.get('message_id', 'N/A')}")

                    # Dify 返回的 metadata
                    if 'metadata' in result:
                        metadata = result['metadata']
                        if 'usage' in metadata:
                            usage = metadata['usage']
                            logger.info(f"📊 Token usage: total={usage.get('total_tokens', 'N/A')}")

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "response": ai_response,
                        "response_time": response_time,
                        "conversation_id": result.get('conversation_id', ''),
                        "message_id": result.get('message_id', '')
                    }
                else:
                    logger.error("❌ API response format error: missing 'answer' field")
                    logger.error(f"   Response body: {result}")
                    return {
                        "success": False,
                        "provider": self.provider_name,
                        "error": "Invalid response format: missing 'answer' field",
                        "details": result
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except Exception:
                    error_msg += f": {response.text}"

                logger.error(f"❌ API request failed: {error_msg}")
                logger.info(f"💡 Suggestion: {self._get_http_error_suggestion(response.status_code)}")

                return {
                    "success": False,
                    "provider": self.provider_name,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "suggestion": self._get_http_error_suggestion(response.status_code)
                }

        except requests.exceptions.Timeout:
            logger.error(f"❌ API request timeout (>{self.get_timeout()}s)")
            logger.info("💡 Suggestion: Increase HTTP_TIMEOUT or check Dify server performance")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Request timeout",
                "suggestion": "Increase HTTP_TIMEOUT or check Dify server performance"
            }
        except requests.exceptions.ConnectionError as e:
            logger.error("❌ Cannot connect to Dify server")
            logger.error(f"   Error: {str(e)}")
            logger.info("💡 Suggestion: Check CHAT_API_URL is correct and Dify server is running")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Connection failed",
                "details": str(e),
                "suggestion": "Check CHAT_API_URL is correct and Dify server is running"
            }
        except Exception as e:
            logger.error(f"❌ API test exception: {str(e)}")
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
        logger.info(f"[User:{user_id}] Conversation cleared, next message will start new conversation")
