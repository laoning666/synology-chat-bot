English / [简体中文](./README_CN.md)

# Synology Chat AI Assistant

An AI-powered chatbot for Synology Chat, allowing users to interact directly with AI models (like GPT) within Synology Chat.

## Features

- 🤖 AI-Powered Intelligent Conversations
- 💬 Seamless Integration with Synology Chat
- 🔄 Conversation Context Awareness
- ⚡ Automatic Message Processing
- 🕒 Session Timeout Management
- 🔁 Automatic API Call Retry Mechanism
- 🔒 Webhook Token Validation
- 🐳 Docker Support
- 🧪 API Connection Test on Startup

## Requirements

- A Synology Chat server
- Access to an AI API (e.g., an OpenAI API Key)
- Docker

## Installation

### Install using Docker

1.  **Pull the image:**
    ```bash
    docker pull laoning666/synology-chat-bot:latest
    ```
2.  **Run the container:**

    **For OpenAI-compatible API:**
    ```bash
    docker run -d \
      --name synology-chat-bot \
      -p 8008:8008 \
      -e CHAT_API_TYPE=openai \
      -e CHAT_API_URL=https://api.openai.com/v1/chat/completions \
      -e CHAT_API_KEY=YOUR_API_KEY \
      -e CHAT_API_MODEL=gpt-4o \
      -e SYNOLOGY_INCOMING_WEBHOOK_URL=YOUR_WEBHOOK_URL \
      -e SYNOLOGY_OUTGOING_WEBHOOK_TOKEN=YOUR_TOKEN \
      laoning666/synology-chat-bot:latest
    ```

    **For Dify API:**
    ```bash
    docker run -d \
      --name synology-chat-bot \
      -p 8008:8008 \
      -e CHAT_API_TYPE=dify \
      -e CHAT_API_URL=https://api.dify.ai/v1/chat-messages \
      -e CHAT_API_KEY=app-YOUR_DIFY_APP_KEY \
      -e SYNOLOGY_INCOMING_WEBHOOK_URL=YOUR_WEBHOOK_URL \
      -e SYNOLOGY_OUTGOING_WEBHOOK_TOKEN=YOUR_TOKEN \
      laoning666/synology-chat-bot:latest
    ```

### Install using Docker Compose (Recommended)

1. Copy the `.env.example` file and rename it to `.env`.
2. Modify the environment variables in the `.env` file.
3. Run `docker-compose up -d`.

```yaml
version: '3.8'

services:
  synology-chat-bot:
    image: laoning666/synology-chat-bot:latest
    container_name: synology-chat-bot
    restart: unless-stopped
    ports:
      - "8008:8008"
    env_file:
      - .env
```

### Development Setup

1.  Clone the repository.
2.  Copy `.env.example` to `.env.dev`.
3.  Set `ENVIRONMENT=development` in `.env.dev`.
4.  Run the development server:
    ```bash
    python run.py
    ```

## Configuration

### AI Interface Configuration

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `CHAT_API_TYPE` | API type: `openai` or `dify` | `openai` |
| `CHAT_API_URL` | AI API endpoint URL | - |
| `CHAT_API_KEY` | API authentication key | - |
| `CHAT_API_MODEL` | AI model identifier (OpenAI only) | - |
| `CHAT_API_TEMPERATURE`| Response randomness (0.0-1.0, OpenAI only) | `0.7` |
| `CHAT_API_MAX_TOKENS` | Maximum response length (OpenAI only) | `4096` |
| `CHAT_API_SYSTEM_PROMPT`| AI system prompt (OpenAI only) | `"You are an intelligent assistant..."` |

> **Note**: When using Dify (`CHAT_API_TYPE=dify`), the `MODEL`, `TEMPERATURE`, `MAX_TOKENS`, and `SYSTEM_PROMPT` settings are configured in the Dify dashboard, not via environment variables.

### Synology Chat Configuration

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `SYNOLOGY_INCOMING_WEBHOOK_URL`| Webhook URL for sending messages | - |
| `SYNOLOGY_OUTGOING_WEBHOOK_TOKEN`| Token to validate incoming webhooks | - |

### Session Settings

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `CONVERSATION_MAX_HISTORY`| Maximum number of conversation history records | `10` |
| `CONVERSATION_TIMEOUT`| Session timeout in seconds | `1800` |
| `CONVERSATION_TYPING_TEXT`| Typing indicator text | `AI is thinking...` |

### HTTP Client Settings

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `HTTP_TIMEOUT` | HTTP request timeout in seconds | `30` |
| `HTTP_MAX_RETRIES` | Maximum number of retries | `3` |

## Synology Chat Configuration Steps

1.  **Create a Bot**
   - Click your profile picture in the upper-right corner.
   - Select **Integration**.
   - Go to the **Bot** tab.
   - Click the **+ Create** button to create a new bot.
2.  **Configure Webhooks**
   - **Create an Incoming Webhook:**
      - Open Synology Chat.
      - Go to **Integration → Incoming Webhooks**.
      - Create a new webhook and copy the URL.
      - Set this URL as the `SYNOLOGY_INCOMING_WEBHOOK_URL` environment variable.
   - **Create an Outgoing Webhook:**
      - Go to **Integration → Outgoing Webhooks**.
      - Create a new webhook.
      - Set the URL to the bot's endpoint: `http://your_server_ip:8008/webhook`.
      - Generate and copy the token.
      - Set this token as the `SYNOLOGY_OUTGOING_WEBHOOK_TOKEN` environment variable.

## Usage

1.  Install and configure the project.
2.  Add the bot in Synology Chat.
3.  Send a message in a channel to start talking with the AI.

## API Endpoints

- `GET /` - Root path
- `GET /health` - Health check
- `GET /api-test` - Test AI API connection
- `POST /webhook` - Synology Chat webhook endpoint

## Development

### Project Structure

```
synology-chat-bot/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── bot/
│   │   ├── chat_manager.py    # Chat session management
│   │   └── message_handler.py # Message processing
│   ├── models/
│   │   └── conversation.py    # Conversation state
│   ├── providers/             # AI provider abstraction
│   │   ├── base.py            # Base provider class
│   │   ├── factory.py         # Provider factory
│   │   ├── openai_provider.py # OpenAI implementation
│   │   └── dify_provider.py   # Dify implementation
│   └── utils/
│       ├── http_client.py     # HTTP client utility
│       └── api_tester.py      # API connection tester
├── app.py                   # Application entry point
├── run.py                   # Development server
├── start.sh                 # Production environment startup script
├── docker_test.sh           # Docker test script
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

### Testing

- **Test Docker build**
  ```bash
  ./docker_test.sh
  ```
- **Development server**
  ```bash
  python run.py
  ```

## Contributing

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/NewFeature`).
3.  Commit your changes (`git commit -m 'Add some NewFeature'`).
4.  Push to the branch (`git push origin feature/NewFeature`).
5.  Open a Pull Request.

## FAQ

**Q: How can I change the AI model's response style?**
A: For OpenAI-compatible APIs, customize the `CHAT_API_SYSTEM_PROMPT` environment variable. For Dify, configure the prompt in the Dify dashboard.

**Q: Is conversation data lost after a session timeout?**
A: Yes, timed-out sessions are automatically cleared. You can adjust the timeout duration with `CONVERSATION_TIMEOUT`.

**Q: Which AI APIs are supported?**
A: Two types are supported:
- **OpenAI-compatible**: Any API following the OpenAI Chat Completions format (OpenAI GPT, Azure OpenAI, Claude, local LLMs with OpenAI-compatible endpoints, etc.)
- **Dify**: Dify platform's Chat API

**Q: How do I use Dify instead of OpenAI?**
A: Set `CHAT_API_TYPE=dify`, configure `CHAT_API_URL` to your Dify API endpoint, and set `CHAT_API_KEY` to your Dify app's API key. Model and prompt settings are configured in the Dify dashboard.

**Q: How is message security ensured?**
A: The system uses webhook token validation to secure messages and supports HTTPS for encrypted data transmission.

**Q: Is streaming output supported?**
A: No, mainly because Synology Chat does not support this feature.

**Q: What happens if the API test fails on startup?**
A: The application will exit and display an error message. Please check your API configuration and network connection.

## Security Considerations

- Keep all API keys and webhook tokens secure.
- It is recommended to deploy and use this bot in a private network environment.
- Regularly update dependencies to patch potential security vulnerabilities.
- Use environment variables to manage sensitive configurations; avoid hardcoding.
- It is recommended to enable HTTPS to encrypt data in transit.

## License

This project is licensed under the MIT License - see the LICENSE file for details.