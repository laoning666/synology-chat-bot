from typing import Dict, Any, Optional
from ..utils.http_client import HTTPClient
from ..models.conversation import Conversation
from ..providers.factory import ProviderFactory

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
        # 使用 Provider 工厂创建对应的 Chat Provider
        self.chat_provider = ProviderFactory.create(config)

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
        """从Chat API获取响应（使用 Provider 抽象层）"""
        # 获取最后一条用户消息
        last_message = ''
        if conversation.messages:
            last_message = conversation.messages[-1].get('content', '')

        return self.chat_provider.send_message(
            conversation.user_id,
            last_message,
            conversation
        )

    def handle_message(self, event: Dict[str, Any], conversation: Conversation) -> Optional[str]:
        """处理接收到的消息"""
        if not self.validate_token(event.get('token', '')):
            return None

        message = event.get('text', '').strip()
        if not message:
            return None

        # 发送输入提示（可选）
        # 注意：Synology Chat 不支持撤回/编辑消息，所以此提示会保留在聊天记录中
        # 如果不需要此提示，可以将 CONVERSATION_TYPING_TEXT 设置为空
        typing_text = self.conversation_config['typing_text']
        if typing_text:
            self.send_message(event['user_id'], typing_text)

        # 添加用户消息到会话
        conversation.add_message("user", message)

        # 获取API响应
        response = self.get_chat_response(conversation)
        if response:
            conversation.add_message("assistant", response)
            return response

        return None