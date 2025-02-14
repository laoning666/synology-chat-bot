from time import time
from typing import List, Dict, Optional

class Conversation:
    def __init__(self, user_id: str, max_history: int = 10, timeout: int = 1800):
        self.user_id = user_id
        self.max_history = max_history
        self.timeout = timeout
        self.messages: List[Dict[str, str]] = []
        self.last_activity = time()

    def add_message(self, role: str, content: str) -> None:
        """添加新消息到历史记录"""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_history:
            self.messages.pop(0)
        self.last_activity = time()

    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有消息历史"""
        return self.messages

    def clear_history(self) -> None:
        """清空历史记录"""
        self.messages = []
        self.last_activity = time()

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return (time() - self.last_activity) > self.timeout

    def get_context(self, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """获取完整的对话上下文，包括系统提示"""
        if system_prompt:
            return [{"role": "system", "content": system_prompt}] + self.messages
        return self.messages.copy()