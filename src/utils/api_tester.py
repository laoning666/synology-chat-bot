# src/utils/api_tester.py
import requests
import json
import time
from typing import Optional, Dict, Any

class APITester:
    """API测试器 / API Tester"""

    def __init__(self, config: Dict[str, Any]):
        """初始化API测试器 / Initialize API tester"""
        self.config = config
        self.chat_config = config['CHAT_API']
        self.http_config = config['HTTP']

    def test_chat_api(self) -> Dict[str, Any]:
        """测试聊天API是否能正常对话 / Test if chat API can handle conversation normally"""
        print("🧪 Testing LLM API connection...")

        # 测试消息 / Test messages
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

        # API请求数据 / API request data
        request_data = {
            "model": self.chat_config['model'],
            "messages": test_messages,
            "temperature": 0.1,  # 使用较低的temperature确保稳定回复 / Use lower temperature for stable replies
            "max_tokens": 50     # 限制token数量，节省成本 / Limit tokens to save cost
        }

        headers = {
            "Authorization": f"Bearer {self.chat_config['api_key']}",
            "Content-Type": "application/json"
        }

        try:
            print(f"   📡 API URL: {self.chat_config['url']}")
            print(f"   🤖 Model: {self.chat_config['model']}")
            print(f"   💬 Test message: {test_messages[-1]['content']}")

            start_time = time.time()

            response = requests.post(
                self.chat_config['url'],
                headers=headers,
                json=request_data,
                timeout=self.http_config['timeout']
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content'].strip()

                    print(f"   ✅ API response successful (time: {response_time:.2f}s)")
                    print(f"   🤖 AI reply: {ai_response}")

                    # 检查usage信息 / Check usage information
                    if 'usage' in result:
                        usage = result['usage']
                        print(f"   📊 Token usage: {usage}")

                    return {
                        "success": True,
                        "response": ai_response,
                        "response_time": response_time,
                        "usage": result.get('usage', {}),
                        "model": result.get('model', self.chat_config['model'])
                    }
                else:
                    print("   ❌ API response format error: missing choices field")
                    return {
                        "success": False,
                        "error": "Invalid response format",
                        "details": result
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"

                print(f"   ❌ API request failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            print(f"   ❌ API request timeout (>{self.http_config['timeout']}s)")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to API server")
            return {
                "success": False,
                "error": "Connection failed"
            }
        except Exception as e:
            print(f"   ❌ API test exception: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
