#!/bin/bash
set -e

echo "🚀 Starting Synology Chat Bot..."
echo "Environment: ${ENVIRONMENT:-production}"

# 快速检查关键环境变量
echo "Checking critical environment variables..."
if [ -z "$CHAT_API_KEY" ] || [ -z "$SYNOLOGY_INCOMING_WEBHOOK_URL" ] || [ -z "$SYNOLOGY_OUTGOING_WEBHOOK_TOKEN" ]; then
    echo "❌ Missing required environment variables:"
    echo "   - CHAT_API_KEY: ${CHAT_API_KEY:+SET}"
    echo "   - SYNOLOGY_INCOMING_WEBHOOK_URL: ${SYNOLOGY_INCOMING_WEBHOOK_URL:+SET}"
    echo "   - SYNOLOGY_OUTGOING_WEBHOOK_TOKEN: ${SYNOLOGY_OUTGOING_WEBHOOK_TOKEN:+SET}"
    exit 1
fi

# 测试应用导入
echo "Testing application..."
python -c "from app import app; print('✅ Application ready')" || {
    echo "❌ Failed to import application"
    exit 1
}

# 启动gunicorn
echo "✅ Starting gunicorn with ${GUNICORN_WORKERS:-1} worker..."
exec gunicorn \
    --bind "0.0.0.0:8008" \
    --workers "${GUNICORN_WORKERS:-1}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app