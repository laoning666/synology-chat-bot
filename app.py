# app.py
import os
import sys
from flask import Flask, request, jsonify
from config.settings import (
    CHAT_API, SYNOLOGY, CONVERSATION, HTTP,
    get_server_config, is_development, ENVIRONMENT
)
from src.bot.chat_manager import ChatManager
from src.utils.api_tester import APITester

def validate_startup_requirements():
    """验证启动所需的配置 / Validate startup requirements"""
    print("🔍 Validating startup configuration...")

    # 检查必要的配置 / Check required configurations
    required_configs = {
        'CHAT_API_URL': CHAT_API['url'],
        'CHAT_API_KEY': CHAT_API['api_key'],
        'CHAT_API_MODEL': CHAT_API['model'],
    }

    missing_configs = []
    for key, value in required_configs.items():
        if not value or value == '' or 'your_' in value.lower():
            missing_configs.append(key)

    if missing_configs:
        print("❌ Missing required configurations:")
        for config in missing_configs:
            print(f"   - {config}")
        return False

    print("✅ Configuration validation passed")
    return True

def test_api_connectivity():
    """测试API连接性 / Test API connectivity"""
    print("🧪 Testing LLM API connectivity...")

    config = {
        'CHAT_API': CHAT_API,
        'HTTP': HTTP
    }

    tester = APITester(config)
    result = tester.test_chat_api()

    if not result['success']:
        print("❌ API test failed:")
        print(f"   Error: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
        return False

    print("✅ API test passed")
    return True

def create_app():
    """应用工厂函数 / Application factory function"""
    print("🚀 Starting Synology Chat Bot")
    print("=" * 50)

    # 验证启动要求 / Validate startup requirements
    if not validate_startup_requirements():
        print("❌ Startup configuration validation failed")
        sys.exit(1)

    # 测试API连接 / Test API connection
    if not test_api_connectivity():
        print("❌ API connectivity test failed")
        print("💡 Please check:")
        print("   1. CHAT_API_URL is correct")
        print("   2. CHAT_API_KEY is valid")
        print("   3. CHAT_API_MODEL is correct")
        print("   4. Network connection is working")
        sys.exit(1)

    print("✅ All startup checks passed, initializing application...")

    # 创建配置字典 / Create configuration dictionary
    config = {
        'CHAT_API': CHAT_API,
        'SYNOLOGY': SYNOLOGY,
        'CONVERSATION': CONVERSATION,
        'HTTP': HTTP
    }

    # 初始化Flask应用 / Initialize Flask application
    app = Flask(__name__)

    # 设置Flask配置 / Set Flask configuration
    server_config = get_server_config()
    app.config['DEBUG'] = server_config['debug']

    # 初始化聊天管理器 / Initialize chat manager
    chat_manager = ChatManager(config)

    @app.route('/webhook', methods=['POST'])
    def webhook():
        """处理来自Synology Chat的webhook请求 / Handle webhook requests from Synology Chat"""
        try:
            form_data = request.form
            event = {key: form_data.get(key) for key in form_data}
            chat_manager.handle_event(event)
            return 'OK', 200
        except Exception as e:
            app.logger.error(f"Error processing webhook: {str(e)}")
            return 'Error', 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点 / Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'synology-chat-bot',
            'environment': ENVIRONMENT,
            'debug_mode': server_config['debug'],
            'version': '1.0.0',
            'api_model': CHAT_API['model']
        }), 200

    @app.route('/api-test', methods=['GET'])
    def api_test():
        """API测试端点 / API test endpoint"""
        tester = APITester(config)
        result = tester.test_chat_api()
        return jsonify(result)

    @app.route('/', methods=['GET'])
    def root():
        """根路径 / Root path"""
        return jsonify({
            'message': 'Synology Chat Bot is running',
            'status': 'ok',
            'environment': ENVIRONMENT,
            'api_model': CHAT_API['model']
        }), 200

    print("🎉 Application initialization completed!")
    return app

# 创建应用实例（用于gunicorn）/ Create application instance (for gunicorn)
app = create_app()

# 开发环境启动代码 / Development environment startup code
if __name__ == '__main__':
    server_config = get_server_config()

    if is_development():
        print(f"\n🌐 Development server starting:")
        print(f"   Local access: http://localhost:{server_config['port']}")
        print(f"   Health check: http://localhost:{server_config['port']}/health")
        print(f"   API test: http://localhost:{server_config['port']}/api-test")
        print("=" * 50)

        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug'],
            threaded=True
        )
    else:
        print("⚠️  Production environment detected")
        print("🔧 Please use gunicorn to start the server")
