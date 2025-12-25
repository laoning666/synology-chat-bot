FROM python:3.10-slim

ARG APP_VERSION=2.0.0

LABEL maintainer="laoning"
LABEL version="${APP_VERSION}"
LABEL description="Synology Chat Bot with AI integration"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . /app/

# 设置启动脚本权限
RUN chmod +x /app/start.sh

EXPOSE 8008

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

# 使用启动脚本
CMD ["/app/start.sh"]