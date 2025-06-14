#!/usr/bin/env python3
"""
开发环境启动脚本
使用方法: python run.py
"""
import os
import sys
from config.settings import is_development, get_server_config, ENVIRONMENT

def main():
    if not is_development():
        print("❌ This script is only for development!")
        print(f"🔧 Current environment: {ENVIRONMENT}")
        print("🔧 For production, use: gunicorn --bind 0.0.0.0:8008 app:app")
        sys.exit(1)

    server_config = get_server_config()

    print("=" * 50)
    print("🚀 Synology Chat Bot - Development Server")
    print("=" * 50)
    print(f"📍 Environment: {ENVIRONMENT}")
    print(f"🌐 URL: http://localhost:{server_config['port']}")
    print(f"🔍 Health: http://localhost:{server_config['port']}/health")
    print(f"📡 Webhook: http://localhost:{server_config['port']}/webhook")
    print("=" * 50)
    print("💡 Press Ctrl+C to stop")
    print()

    try:
        from app import app
        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug'],
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()