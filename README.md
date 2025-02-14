# Synology Chat AI Assistant

An AI-powered chatbot for Synology Chat that enables users to interact directly with AI models (such as GPT) within their chat interface.

## Features

- 🤖 AI-driven intelligent conversations
- 💬 Seamless Synology Chat integration
- 🔄 Conversation context maintenance
- ⚡ Automatic message processing
- 🕒 Session timeout management
- 🔁 API call retry mechanism
- 🔒 Webhook token validation
- 🐳 Docker support

## Requirements
- Synology Chat server
- AI API access (e.g., OpenAI API key)
- Docker

## Installation

### Using Docker

1. Pull the image:
```bash
docker pull laoning666/synology-chat-bot:latest
```

2. Run the container:
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

### Using Docker-compose (Recommended)

1. Copy `.env.example` to `.env` in your local directory

2. Modify the environment variables in `.env`

3. Run with the following docker-compose.yml:
```yaml
version: '3.8'

services:
  synology-chat-bot:
    image: laoning666/synology-chat-bot
    container_name: synology-chat-bot
    ports:
      - "8008:8008"
    restart: unless-stopped
```

## Synology Chat Setup
1. Create Bot

- Click your profile picture in the top right corner
- Select [Integration]
- Click [Bots] tab
- Click [+ Create] button to create a new bot

2. Configure Webhook

- In the bot details page, set [Outgoing Webhook] to `http://your_server_ip:8008/webhook` (Note: your_server_ip is the IP address of the server running the bot service)
- Set [Incoming URL] as the container's SYNOLOGY_INCOMING_WEBHOOK_URL variable
- Set [Token] as the container's SYNOLOGY_OUTGOING_WEBHOOK_TOKEN variable
- Click [OK] to save all settings

### AI Interface Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| CHAT_API_URL | AI API endpoint | - |
| CHAT_API_KEY | API authentication key | - |
| CHAT_API_MODEL | AI model identifier | - |
| CHAT_API_TEMPERATURE | Response randomness (0.0-1.0) | 0.7 |
| CHAT_API_MAX_TOKENS | Maximum response length | 4096 |
| CHAT_API_SYSTEM_PROMPT | AI system prompt | "I'm an AI assistant ready to help you." |

### Synology Chat Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| SYNOLOGY_INCOMING_WEBHOOK_URL | Webhook URL for sending messages | - |
| SYNOLOGY_OUTGOING_WEBHOOK_TOKEN | Token for validating incoming webhooks | - |

### Server Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| SERVER_HOST | Server host address | 0.0.0.0 |
| SERVER_PORT | Server port | 8008 |
| SERVER_DEBUG | Debug mode | False |

### Session Settings
| Variable | Description | Default |
|----------|-------------|---------|
| CONVERSATION_MAX_HISTORY | Maximum conversation history entries | 10 |
| CONVERSATION_TIMEOUT | Session timeout (seconds) | 1800 |
| CONVERSATION_TYPING_TEXT | Typing indicator text | ... |

### HTTP Client Settings
| Variable | Description | Default |
|----------|-------------|---------|
| HTTP_TIMEOUT | HTTP request timeout (seconds) | 30 |
| HTTP_MAX_RETRIES | Maximum retry attempts | 3 |

## Synology Chat Setup Steps

1. Create Incoming Webhook:
   - Open Synology Chat
   - Go to Integration -> Incoming Webhook
   - Create a new webhook and copy the URL
   - Set the URL as SYNOLOGY_INCOMING_WEBHOOK_URL

2. Create Outgoing Webhook:
   - Go to Integration -> Outgoing Webhook
   - Create a new webhook
   - Set URL to your bot's endpoint (e.g., http://your-server:8008/webhook)
   - Generate and copy the token
   - Set the token as SYNOLOGY_OUTGOING_WEBHOOK_TOKEN

## Usage

1. Install the project
2. Add the bot to Synology Chat
3. Send messages in the channel to interact with AI

## Development Guide

### Project Structure
```
synology-chat-bot/
├── app.py                 # Application entry
├── config/
│   └── settings.py       # Configuration management
├── src/
│   ├── bot/
│   │   ├── chat_manager.py     # Chat session management
│   │   └── message_handler.py  # Message processing
│   ├── models/
│   │   └── conversation.py     # Session state
│   └── utils/
│       └── http_client.py      # HTTP client utilities
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

### Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Create a Pull Request

## FAQ

**Q: How to modify the AI model's response style?**
A: Customize the AI's system prompt by modifying the CHAT_API_SYSTEM_PROMPT environment variable.

**Q: Will data be lost after session timeout?**
A: Yes, expired sessions are automatically cleared. Adjust CONVERSATION_TIMEOUT to modify the timeout duration.

**Q: Which AI models are supported?**
A: Any model compatible with the OPEN API format, including OpenAI's GPT series, Claude, etc.

**Q: How is message security ensured?**
A: The system uses webhook token validation and supports HTTPS encrypted transmission.

**Q: Is streaming output supported?**
A: No, as Synology Chat doesn't support this feature.

## Security Notes

1. Securely store all API keys and webhook tokens
2. Recommended for internal network deployment
3. Regularly update dependencies to patch potential security vulnerabilities
4. Use environment variables for sensitive configurations
5. Enable HTTPS for encrypted data transmission

## License

This project is licensed under the MIT License - see the LICENSE file for details