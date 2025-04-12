# LangChain MCP Chat Platform

A versatile chat platform that integrates LangChain, custom MCP (Model Control Protocol) servers, and Google's Gemini AI model for enhanced conversational capabilities.

![WhatsApp Image 2025-04-11 at 4 58 04 PM](https://github.com/user-attachments/assets/1fc93db4-9cc9-4fde-9a2b-fa3b77615682)

## Features

- **Langchain Integration**: Utilize the power of LangChain for advanced conversation management and tool usage  
- **Google Gemini AI**: Powered by Google's powerful Gemini 2.0 Flash model for natural conversations  
- **Custom MCP Servers**: Integrates with various MCP servers for specialized functionalities:
  - **Tavily web search and extraction** ([Tavily MCP Link](https://smithery.ai/server/@tavily-ai/tavily-mcp))  
    > Please check the repository and follow setup instructions for integration.
  - **Gmail integration for email operations** ([Gmail MCP GitHub Repo](https://github.com/GongRzhe/Gmail-MCP-Server))  
    > Make sure to clone and configure it as per the instructions to enable Gmail features.
  - **Custom accounting system (muhasebe)**
- **Memory Management**: Conversation history tracking for contextual responses  
- **Web Interface**: Responsive web UI for user interactions  
- **Extensible Architecture**: Easy to add new tools and capabilities  


## Project Structure

```
langchain-mcp-chat-platform/
├── web_js/               # Web interface using FastAPI and WebSockets
│   ├── main.py           # Main FastAPI application with WebSocket connections
│   ├── templates/        # HTML templates
│   └── static/           # Static assets (CSS, JS)
├── own_mcp/              # Custom MCP server implementations
│   ├── mcp_server.py     # Main MCP server implementation
│   ├── muhasebe_client.py # Accounting system client
│   └── __init__.py       # Package initialization
└── app/                  # Desktop application
    ├── main.py           # Main application entry point
    ├── database/         # Database operations
    └── ui/               # UI components
```

## Setup and Installation

1. Clone this repository:
```bash
git clone https://github.com/BilalAltundag/langchain-mcp-chat-platform.git
cd langchain-mcp-chat-platform
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your API keys
# Required:
# - GOOGLE_API_KEY for Gemini AI
# - TAVILY_API_KEY for web search
# - GMAIL_MCP_KEY for email operations
```

### Obtaining API Keys

- **Google Gemini API Key**: Visit the [Google AI Studio](https://ai.google.dev/) to create an API key
- **Tavily API Key**: Sign up at [Tavily AI](https://tavily.com/) to get your API key for web search
- **Gmail MCP Key**: This is a Smithery MCP key, see documentation for details

## Running the Applications

### Web Interface
```bash
cd web_js
uvicorn main:app --reload --port 5001
```

### Custom MCP Server
```bash
cd own_mcp
python mcp_server.py
```

### Desktop Application
```bash
cd app
python main.py
```

## Integration with External Services

The platform integrates with several external services:

- **Google Gemini**: For natural language understanding and generation
- **Tavily**: For web search and content extraction
- **Gmail**: For email operations and management
- **Accounting System**: For financial management and tracking

## Extending the Platform

You can extend the platform by:

1. Creating new MCP servers for additional functionality
2. Adding new tools to the existing LangChain agent
3. Enhancing the UI with additional features

## Important Notes

- API keys and sensitive information should be stored in the `.env` file
- The `.env` file is not tracked by Git for security reasons
- Always check the `.env.example` file for required environment variables

## License

MIT 
