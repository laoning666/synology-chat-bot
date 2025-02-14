from typing import Dict, Any, Optional
from ..utils.http_client import HTTPClient
from ..models.conversation import Conversation

class MessageHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.http_client = HTTPClient(
            timeout=config['HTTP']['timeout'],
            max_retries=config['HTTP']['max_retries']
        )
        self.chat_config = config['CHAT_API']
        self.synology_config = config['SYNOLOGY']
        self.conversation_config = config['CONVERSATION']

    def validate_token(self, token: str) -> bool:
        """验证webhook token"""
        return token == self.synology_config['outgoing_webhook_token']

    def send_message(self, user_id: int, text: str) -> bool:
        """发送消息到Synology Chat"""
        return self.http_client.send_chat_message(
            self.synology_config['incoming_webhook_url'],
            text,
            [user_id]
        )

    def get_chat_response(self, conversation: Conversation) -> Optional[str]:
        """从Chat API获取响应"""
        messages = conversation.get_context(self.chat_config['system_prompt'])
        return self.http_client.send_chat_api_request(
            self.chat_config['url'],
            messages,
            self.chat_config['api_key'],
            self.chat_config['model'],
            self.chat_config['temperature'],
            self.chat_config['max_tokens']
        )

    def handle_message(self, event: Dict[str, Any], conversation: Conversation) -> Optional[str]:
        """处理接收到的消息"""
        if not self.validate_token(event.get('token', '')):
            return None

        message = event.get('text', '').strip()
        if not message:
            return None

        # 发送输入提示
        self.send_message(event['user_id'], self.conversation_config['typing_text'])

        # 添加用户消息到会话
        conversation.add_message("user", message)

        # 获取API响应
        response = self.get_chat_response(conversation)
        if response:
            conversation.add_message("assistant", response)
            return response

        return None