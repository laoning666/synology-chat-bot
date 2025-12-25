from typing import Dict, Any, Optional
from ..utils.http_client import HTTPClient
from ..models.conversation import Conversation
from ..providers.factory import ProviderFactory
from ..utils.logger import logger, log_error


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
        logger.info(f"MessageHandler initialized with {self.chat_provider.provider_name}")

    def validate_token(self, token: str) -> bool:
        """验证webhook token"""
        is_valid = token == self.synology_config['outgoing_webhook_token']
        if not is_valid:
            logger.warning("Webhook token validation failed")
        return is_valid

    def send_message(self, user_id: int, text: str) -> bool:
        """发送消息到Synology Chat"""
        logger.debug(f"[User:{user_id}] Sending message to Synology Chat...")
        success = self.http_client.send_chat_message(
            self.synology_config['incoming_webhook_url'],
            text,
            [user_id]
        )
        if success:
            logger.debug(f"[User:{user_id}] Message sent successfully")
        else:
            log_error("Synology", f"Failed to send message to user {user_id}",
                     suggestion="Check SYNOLOGY_INCOMING_WEBHOOK_URL configuration")
        return success

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
        user_id = event.get('user_id', 'unknown')
        
        # Token 验证
        if not self.validate_token(event.get('token', '')):
            logger.warning(f"[User:{user_id}] Invalid webhook token, rejecting request")
            return None

        message = event.get('text', '').strip()
        if not message:
            logger.debug(f"[User:{user_id}] Empty message received, ignoring")
            return None

        logger.info(f"[User:{user_id}] Received message: {message[:50]}{'...' if len(message) > 50 else ''}")

        # 发送输入提示（可选）
        typing_text = self.conversation_config['typing_text']
        if typing_text:
            logger.debug(f"[User:{user_id}] Sending typing indicator")
            self.send_message(event['user_id'], typing_text)

        # 添加用户消息到会话
        conversation.add_message("user", message)
        logger.debug(f"[User:{user_id}] Conversation history: {len(conversation.messages)} messages")

        # 获取API响应
        response = self.get_chat_response(conversation)
        if response:
            conversation.add_message("assistant", response)
            logger.info(f"[User:{user_id}] Response generated: {len(response)} chars")
            return response

        logger.warning(f"[User:{user_id}] Failed to get response from AI API")
        return None