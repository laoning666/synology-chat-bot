from typing import Dict, Any
from ..models.conversation import Conversation
from .message_handler import MessageHandler

class ChatManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversations: Dict[str, Conversation] = {}
        self.message_handler = MessageHandler(config)

    def get_conversation(self, user_id: str) -> Conversation:
        """获取或创建用户会话"""
        if user_id not in self.conversations:
            self.conversations[user_id] = Conversation(
                user_id,
                self.config['CONVERSATION']['max_history'],
                self.config['CONVERSATION']['timeout']
            )
        return self.conversations[user_id]

    def cleanup_expired_conversations(self) -> None:
        """清理过期的会话"""
        expired_users = [
            user_id for user_id, conv in self.conversations.items()
            if conv.is_expired()
        ]
        for user_id in expired_users:
            del self.conversations[user_id]

    def handle_event(self, event: Dict[str, Any]) -> None:
        """处理webhook事件"""
        user_id = str(event.get('user_id'))
        if not user_id:
            return

        # 清理过期会话
        self.cleanup_expired_conversations()

        # 获取用户会话
        conversation = self.get_conversation(user_id)

        # 处理消息
        response = self.message_handler.handle_message(event, conversation)

        # 发送响应
        if response:
            self.message_handler.send_message(int(user_id), response)