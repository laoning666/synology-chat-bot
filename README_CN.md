# Synology Chat AI 助手

一个集成了AI能力的群晖聊天机器人，允许用户直接在Synology Chat中与AI模型（如GPT）进行对话。

## 功能特性

- 🤖 AI驱动的智能对话
- 💬 无缝集成Synology Chat
- 🔄 保持对话上下文
- ⚡ 自动消息处理
- 🕒 会话超时管理
- 🔁 API调用自动重试机制
- 🔒 Webhook令牌验证
- 🐳 Docker支持
- 🧪 启动时API连接测试

## 环境要求

- Synology Chat服务器
- AI API访问权限（例如OpenAI API密钥）
- Docker

## 安装说明

### 使用Docker安装

1.  **拉取镜像：**
    ```bash
    docker pull laoning666/synology-chat-bot:latest
    ```
2.  **运行容器：**
    ```bash
    docker run -d \
      --name synology-chat-bot \
      -p 8008:8008 \
      -e CHAT_API_URL=YOUR_API_URL \
      -e CHAT_API_KEY=YOUR_API_KEY \
      -e CHAT_API_MODEL=YOUR_MODEL \
      -e SYNOLOGY_INCOMING_WEBHOOK_URL=YOUR_WEBHOOK_URL \
      -e SYNOLOGY_OUTGOING_WEBHOOK_TOKEN=YOUR_TOKEN \
      laoning666/synology-chat-bot:latest
    ```

### 使用Docker Compose安装（推荐）

1. 拷贝`.env.example`文件到本地重命名为`.env`
2. 修改`.env`中的环境变量
3. 运行 `docker-compose up -d`

```yaml
version: '3.8'

services:
  synology-chat-bot:
    build: .
    container_name: synology-chat-bot
    ports:
      - "8008:8008"
    env_file:
      - .env
    restart: unless-stopped
```

### 开发环境设置

1.  克隆仓库
2.  复制 `.env.example` 为 `.env.dev`
3.  在 `.env.dev` 中设置 `ENVIRONMENT=development`
4.  运行开发服务器：
    ```bash
    python run.py
    ```

## 配置说明

### AI接口配置

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `CHAT_API_URL` | AI API接口地址 | - |
| `CHAT_API_KEY` | API认证密钥 | - |
| `CHAT_API_MODEL` | AI模型标识符 | - |
| `CHAT_API_TEMPERATURE` | 响应随机性（0.0-1.0） | `0.7` |
| `CHAT_API_MAX_TOKENS` | 最大响应长度 | `4096` |
| `CHAT_API_SYSTEM_PROMPT` | AI系统提示词 | `"你是一个智能助手，可以帮助用户解答问题。"` |

### 群晖聊天配置

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `SYNOLOGY_INCOMING_WEBHOOK_URL` | 发送消息的Webhook地址 | - |
| `SYNOLOGY_OUTGOING_WEBHOOK_TOKEN` | 验证接收webhook的令牌 | - |

### 会话设置

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `CONVERSATION_MAX_HISTORY` | 最大会话历史记录数 | `10` |
| `CONVERSATION_TIMEOUT` | 会话超时时间（秒） | `1800` |
| `CONVERSATION_TYPING_TEXT`| 输入提示文本 | `AI正在思考中...` |

### HTTP客户端设置

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `HTTP_TIMEOUT` | HTTP请求超时时间（秒） | `30` |
| `HTTP_MAX_RETRIES` | 最大重试次数 | `3` |


## 群晖Chat配置步骤

1.  **创建机器人**
    - 点击右上角的个人头像
    - 选择【整合】
    - 点击【机器人】标签
    - 点击【+ 创建】按钮，创建新的机器人
2.  **配置Webhook**
    - **创建传入Webhook：**
        - 打开Synology Chat
        - 进入 **集成 → 传入Webhook**
        - 创建新的webhook并复制URL
        - 将URL设置为 `SYNOLOGY_INCOMING_WEBHOOK_URL`
    - **创建传出Webhook：**
        - 进入 **集成 → 传出Webhook**
        - 创建新的webhook
        - 设置URL为机器人的接口地址：`http://your_server_ip:8008/webhook`
        - 生成并复制令牌
        - 将令牌设置为 `SYNOLOGY_OUTGOING_WEBHOOK_TOKEN`

## 使用方法

1.  安装并配置项目
2.  在Synology Chat中添加机器人
3.  在频道中发送消息即可与AI对话

## API端点

- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /api-test` - 测试AI API连接
- `POST /webhook` - Synology Chat webhook端点

## 开发说明

### 项目结构

```
synology-chat-bot/
├── config/
│   └── settings.py          # 配置管理
├── src/
│   ├── bot/
│   │   ├── chat_manager.py    # 聊天会话管理
│   │   └── message_handler.py # 消息处理
│   ├── models/
│   │   └── conversation.py    # 会话状态
│   └── utils/
│       ├── http_client.py     # HTTP客户端工具
│       └── api_tester.py      # API连接测试器
├── app.py                   # 应用程序入口
├── run.py                   # 开发服务器
├── start.sh                 # 生产环境启动脚本
├── docker_test.sh           # Docker测试脚本
├── Dockerfile               # Docker配置
├── requirements.txt         # Python依赖
└── .env.example             # 环境变量模板
```

### 测试

- **测试Docker构建**
  ```bash
  ./docker_test.sh
  ```
- **开发服务器**
  ```bash
  python run.py
  ```

## 参与贡献

1.  Fork 项目
2.  创建功能分支 (`git checkout -b feature/新功能`)
3.  提交更改 (`git commit -m '添加新功能'`)
4.  推送到分支 (`git push origin feature/新功能`)
5.  创建 Pull Request

## 常见问题

**Q: 如何修改AI模型的回复风格？**
A: 可以通过修改 `CHAT_API_SYSTEM_PROMPT` 环境变量来自定义AI的系统提示词。

**Q: 会话超时后数据会丢失吗？**
A: 是的，超时的会话会被自动清理。可以通过调整 `CONVERSATION_TIMEOUT` 来修改超时时间。

**Q: 支持哪些AI模型？**
A: 理论上支持任何兼容OpenAI API格式的模型，包括OpenAI的GPT系列、Claude等等。

**Q: 如何保证消息安全？**
A: 系统通过webhook令牌验证来确保消息安全，并支持HTTPS加密传输。

**Q: 是否支持流式输出？**
A: 不支持，主要是Synology Chat不支持此功能。

**Q: 启动时API测试失败会怎样？**
A: 应用程序会退出并显示错误信息。请检查您的API配置和网络连接。

## 安全注意事项

- 请妥善保管所有API密钥和Webhook令牌
- 建议在内网环境中部署使用
- 定期更新依赖包以修复潜在的安全漏洞
- 使用环境变量管理敏感配置，避免硬编码
- 建议启用HTTPS以加密传输数据


## 版权说明

本项目采用MIT许可证 - 详见LICENSE文件。