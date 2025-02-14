from flask import Flask, request
from config.settings import CHAT_API, SYNOLOGY, SERVER, CONVERSATION, HTTP
from src.bot.chat_manager import ChatManager

# 创建配置字典
config = {
    'CHAT_API': CHAT_API,
    'SYNOLOGY': SYNOLOGY,
    'SERVER': SERVER,
    'CONVERSATION': CONVERSATION,
    'HTTP': HTTP
}

# 初始化Flask应用
app = Flask(__name__)

# 初始化聊天管理器
chat_manager = ChatManager(config)

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理来自Synology Chat的webhook请求"""
    try:
        # 获取表单数据
        form_data = request.form
        event = {key: form_data.get(key) for key in form_data}

        # 处理事件
        chat_manager.handle_event(event)

        return 'OK', 200
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(
        host=SERVER['host'],
        port=SERVER['port'],
        debug=SERVER['debug']
    )