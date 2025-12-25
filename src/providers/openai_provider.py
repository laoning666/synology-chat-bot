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
from ..utils.logger import logger, log_request, log_response, log_error


class OpenAIProvider(ChatProvider):
    """OpenAI 兼容 API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._init_session()
        logger.debug(f"OpenAIProvider initialized with model: {self.chat_config.get('model', 'N/A')}")

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
            messages = context.get_context(system_prompt)
            logger.debug(f"Built message context with {len(messages)} messages")
            return messages

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
        logger.info(f"[User:{user_id}] Sending message to OpenAI API...")
        start_time = time.time()

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

            log_request("POST", self.get_api_url(), headers=headers)

            response = self.session.post(
                self.get_api_url(),
                headers=headers,
                json=json_data,
                timeout=self.get_timeout()
            )
            
            response_time = time.time() - start_time
            log_response(response.status_code, response_time)

            response.raise_for_status()

            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # 记录 token 使用情况
            if 'usage' in result:
                usage = result['usage']
                logger.info(f"[User:{user_id}] Response received in {response_time:.2f}s "
                           f"(tokens: {usage.get('total_tokens', 'N/A')})")
            else:
                logger.info(f"[User:{user_id}] Response received in {response_time:.2f}s")
            
            return ai_response

        except requests.exceptions.Timeout:
            log_error("Timeout", f"Request timeout after {self.get_timeout()}s",
                     suggestion="Increase HTTP_TIMEOUT or check network connection")
            return None
        except requests.exceptions.ConnectionError as e:
            log_error("Connection", f"Cannot connect to API server: {self.get_api_url()}",
                     details=str(e),
                     suggestion="Check CHAT_API_URL is correct and server is accessible")
            return None
        except requests.exceptions.HTTPError as e:
            response_time = time.time() - start_time
            status_code = e.response.status_code if e.response else 'Unknown'
            error_body = ""
            try:
                error_body = e.response.json() if e.response else {}
            except Exception:
                error_body = e.response.text if e.response else str(e)
            
            log_error("HTTP", f"Status {status_code}: {error_body}",
                     suggestion=self._get_http_error_suggestion(status_code))
            return None
        except (KeyError, IndexError) as e:
            log_error("Parse", f"Failed to parse API response: {str(e)}",
                     suggestion="API response format may have changed or is invalid")
            return None
        except Exception as e:
            log_error("Unexpected", str(e))
            return None

    def _get_http_error_suggestion(self, status_code: int) -> str:
        """根据 HTTP 状态码返回建议"""
        suggestions = {
            400: "Check request format and parameters",
            401: "Check CHAT_API_KEY is valid",
            403: "API key may lack permissions",
            404: "Check CHAT_API_URL is correct",
            429: "Rate limit exceeded, wait and retry",
            500: "API server error, try again later",
            502: "API gateway error, try again later",
            503: "API service unavailable, try again later",
        }
        return suggestions.get(status_code, "Check API configuration")

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 OpenAI API 连接

        Returns:
            测试结果字典
        """
        logger.info("=" * 50)
        logger.info("🧪 Testing OpenAI-compatible API connection...")
        logger.info("=" * 50)

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

        # 配置信息
        logger.info(f"📡 API URL: {self.get_api_url()}")
        logger.info(f"🤖 Model: {self.chat_config.get('model', 'N/A')}")
        logger.info(f"⏱️  Timeout: {self.get_timeout()}s")
        logger.info(f"🔄 Max Retries: {self.http_config.get('max_retries', 3)}")

        try:
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

                    logger.info(f"✅ API response successful (time: {response_time:.2f}s)")
                    logger.info(f"🤖 AI reply: {ai_response}")

                    if 'usage' in result:
                        usage = result['usage']
                        logger.info(f"📊 Token usage: prompt={usage.get('prompt_tokens', 'N/A')}, "
                                   f"completion={usage.get('completion_tokens', 'N/A')}, "
                                   f"total={usage.get('total_tokens', 'N/A')}")

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "response": ai_response,
                        "response_time": response_time,
                        "usage": result.get('usage', {}),
                        "model": result.get('model', self.chat_config.get('model', ''))
                    }
                else:
                    logger.error("❌ API response format error: missing 'choices' field")
                    logger.error(f"   Response body: {result}")
                    return {
                        "success": False,
                        "provider": self.provider_name,
                        "error": "Invalid response format: missing 'choices' field",
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
            logger.info("💡 Suggestion: Increase HTTP_TIMEOUT or check network latency")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Request timeout",
                "suggestion": "Increase HTTP_TIMEOUT or check network latency"
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Cannot connect to API server")
            logger.error(f"   Error: {str(e)}")
            logger.info("💡 Suggestion: Check CHAT_API_URL is correct and network is accessible")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": "Connection failed",
                "details": str(e),
                "suggestion": "Check CHAT_API_URL is correct and network is accessible"
            }
        except Exception as e:
            logger.error(f"❌ API test exception: {str(e)}")
            return {
                "success": False,
                "provider": self.provider_name,
                "error": str(e)
            }
