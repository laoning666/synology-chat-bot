import json
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HTTPClient:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """发送POST请求"""
        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {str(e)}")
            raise

    def send_chat_message(self, webhook_url: str, text: str, user_ids: list) -> bool:
        """发送消息到Synology Chat"""
        try:
            payload = {
                "text": text,
                "user_ids": user_ids
            }
            data = {'payload': json.dumps(payload)}
            response = self.post(webhook_url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send chat message: {str(e)}")
            return False

    def send_chat_api_request(self, api_url: str, messages: list,
                              api_key: str, model: str,
                              temperature: float = 0.7,
                              max_tokens: int = 2048) -> Optional[str]:
        """发送请求到Chat API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            json_data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            response = self.post(api_url, json_data=json_data, headers=headers)
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Failed to get chat API response: {str(e)}")
            return None