#!/bin/bash
# docker_test.sh
set -e

# =============================================================================
# 配置变量
# =============================================================================
# 端口配置
HOST_PORT=${HOST_PORT:-8008}           # 宿主机端口，默认8008
CONTAINER_PORT=${CONTAINER_PORT:-8008} # 容器端口，默认8008

# 容器配置
CONTAINER_NAME=${CONTAINER_NAME:-synology-chat-bot-test}
IMAGE_NAME=${IMAGE_NAME:-synology-chat-bot-test}
ENV_FILE=${ENV_FILE:-.env.dev}

# 测试配置
HEALTH_CHECK_RETRIES=${HEALTH_CHECK_RETRIES:-5}
STARTUP_WAIT_TIME=${STARTUP_WAIT_TIME:-10}

# =============================================================================
# 脚本开始
# =============================================================================
echo "🐳 Docker 测试脚本"
echo "=" * 50
echo "📊 配置信息:"
echo "   宿主机端口: $HOST_PORT"
echo "   容器端口: $CONTAINER_PORT"
echo "   容器名称: $CONTAINER_NAME"
echo "   镜像名称: $IMAGE_NAME"
echo "   环境文件: $ENV_FILE"
echo "=" * 50

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 环境文件 $ENV_FILE 不存在"
    echo "💡 请先创建环境文件: cp .env.example $ENV_FILE"
    exit 1
fi

# 检查端口是否被占用
if lsof -Pi :$HOST_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $HOST_PORT 已被占用"
    echo "💡 当前占用进程:"
    lsof -Pi :$HOST_PORT -sTCP:LISTEN

    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 测试取消"
        exit 1
    fi
fi

# 清理旧的容器和镜像
echo "🧹 清理旧的容器和镜像..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
docker rmi $IMAGE_NAME 2>/dev/null || true

# 构建镜像
echo "🔨 构建Docker镜像..."
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Docker镜像构建失败"
    exit 1
fi

echo "✅ Docker镜像构建成功"

# 运行容器
echo "🚀 启动Docker容器..."
echo "   端口映射: $HOST_PORT:$CONTAINER_PORT"
docker run -d \
    --name $CONTAINER_NAME \
    -p $HOST_PORT:$CONTAINER_PORT \
    --env-file $ENV_FILE \
    $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Docker容器启动失败"
    exit 1
fi

echo "✅ Docker容器启动成功"

# 等待容器启动
echo "⏳ 等待容器启动 ($STARTUP_WAIT_TIME 秒)..."
sleep $STARTUP_WAIT_TIME

# 检查容器状态
echo "🔍 检查容器状态..."
if docker ps | grep $CONTAINER_NAME >/dev/null; then
    echo "✅ 容器正在运行"
else
    echo "❌ 容器未运行"
    echo "📝 容器日志:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# 检查容器日志
echo "📝 容器启动日志:"
docker logs $CONTAINER_NAME | tail -20

# 测试健康检查
echo "🏥 测试健康检查..."
HEALTH_URL="http://localhost:$HOST_PORT/health"
echo "   健康检查URL: $HEALTH_URL"

for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
    if curl -f $HEALTH_URL >/dev/null 2>&1; then
        echo "✅ 健康检查通过"
        break
    else
        echo "⏳ 等待服务启动... ($i/$HEALTH_CHECK_RETRIES)"
        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            echo "❌ 健康检查失败"
            echo "📝 容器日志:"
            docker logs $CONTAINER_NAME
            exit 1
        fi
        sleep 5
    fi
done

# 测试API端点
echo "🧪 测试API端点..."
BASE_URL="http://localhost:$HOST_PORT"

echo "Root endpoint ($BASE_URL/):"
curl -s $BASE_URL/ | jq . 2>/dev/null || curl -s $BASE_URL/

echo -e "\nHealth endpoint ($BASE_URL/health):"
curl -s $BASE_URL/health | jq . 2>/dev/null || curl -s $BASE_URL/health

# 显示容器信息
echo -e "\n📊 容器信息:"
echo "状态: $(docker inspect $CONTAINER_NAME --format='{{.State.Status}}')"
echo "IP地址: $(docker inspect $CONTAINER_NAME --format='{{.NetworkSettings.IPAddress}}')"
echo "端口映射: $(docker port $CONTAINER_NAME)"

# 显示访问信息
echo -e "\n🌐 访问信息:"
echo "本地访问: http://localhost:$HOST_PORT"
echo "健康检查: http://localhost:$HOST_PORT/health"
echo "Webhook: http://localhost:$HOST_PORT/webhook"

echo -e "\n🎉 Docker测试完成"
echo "💡 容器正在运行，可以进行进一步测试"
echo "💡 停止容器: docker stop $CONTAINER_NAME"
echo "💡 查看日志: docker logs -f $CONTAINER_NAME"
echo "💡 删除容器: docker rm -f $CONTAINER_NAME"

# 询问是否保持容器运行
echo ""
read -p "是否保持容器运行？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 停止并删除容器..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "✅ 清理完成"
fi
