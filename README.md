# LangChain MCP Chat Platform

A versatile chat platform that integrates LangChain, custom MCP (Model Control Protocol) servers, and Google's Gemini AI model for enhanced conversational capabilities.

![Ekran Alıntısı](https://github.com/user-attachments/assets/597e1c99-bd52-45aa-9248-35810d597219)

![image](https://github.com/user-attachments/assets/b93d432f-9b2b-4e2e-a070-f016186c05a2)


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

### Step 1: Clone the Repository
```bash
git clone https://github.com/BilalAltundag/langchain-mcp-chat-platform.git
cd langchain-mcp-chat-platform
```

### Step 2: Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Requirements
Make sure to use the exact versions in requirements.txt to avoid compatibility issues:
```bash
pip install -r requirements.txt
```

> **Important**: If you encounter any dependency errors, try installing packages one by one:
> ```bash
> pip install fastapi==0.104.1 uvicorn==0.24.0
> pip install langchain==0.3.23 langchain-community==0.3.21 langchain-core==0.3.51
> pip install langchain-mcp-adapters==0.0.7 langchain-google-genai==2.1.2
> pip install langgraph==0.3.29 langgraph-prebuilt==0.1.5 langgraph-sdk==0.1.61
> ```

### Step 4: Install Node.js Dependencies (for Tavily & Gmail)
If you want to use Tavily search or Gmail features, you'll need to install Node.js and the Smithery CLI:

```bash
# Install Smithery CLI globally
npm install -g @smithery/cli
```

### Step 5: Set up Environment Variables
Copy the example .env file and edit it with your API keys:
```bash
# Copy the example .env file
cp .env.example .env

# Then edit the .env file with your preferred text editor
```

Your `.env` file should contain the following keys:
```
# Google Gemini API key (required for the AI model)
GOOGLE_API_KEY="your_google_api_key"

# Smithery CLI key (required for Tavily and Gmail services)
SMITHERY_KEY="your_smithery_cli_key" 
```

#### About API Keys
- **GOOGLE_API_KEY**: Used by the AI model for natural language understanding
- **SMITHERY_KEY**: Only key required locally to run both Tavily and Gmail MCP servers

> **ÖNEMLİ**: TAVILY_API_KEY ve GMAIL_API_KEY girmenize gerek yoktur. Bu keyler Smithery sitesinde MCP kodları oluşturulurken kullanılır ve bu uygulamada bunlara ihtiyaç yoktur. Sadece SMITHERY_KEY yeterlidir.

#### Alternative: Direct Configuration in Code
If you don't want to use an .env file, you can directly set the API keys in code:

Open `web_js/main.py` and replace the environment variable loading with direct assignment:
```python
# Instead of this:
# google_api_key = os.environ.get("GOOGLE_API_KEY")
# smithery_key = os.environ.get("SMITHERY_KEY")

# Use this (replace with your actual API keys):
google_api_key = "YOUR_GOOGLE_API_KEY_HERE"
smithery_key = "YOUR_SMITHERY_CLI_KEY_HERE"
```

### Step 6: Enable Gmail API (for Email Features)

Before you can use the Gmail functionality, you need to enable the Gmail API in your Google Cloud project:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API" and select it
5. Click "Enable" to activate the API for your project
6. Wait a few minutes for the changes to propagate

If you skip this step, you may encounter an error like:
```
Error: Gmail API has not been used in project XXXXX before or it is disabled.
```

## Running the Application

### Option 1: Run with all MCP services
This will start the application with all services (muhasebe, Tavily search, Gmail):
```bash
cd web_js
python main.py
```

### Option 2: Run with only the muhasebe service (recommended for first time)
To avoid potential issues with external services, you can modify `web_js/main.py` to use only the custom_mcp service:

```python
async with MultiServerMCPClient(
    {
        "custom_mcp": {
            "command": "python",
            "args": [os.path.abspath(os.path.join(os.path.dirname(os.getcwd()), "own_mcp", "mcp_server.py"))],
            "transport": "stdio",
        }
        # Comment out other services for initial testing
    }
) as client:
```

## Troubleshooting

### Application Hangs During Startup
If the application seems to hang during startup, it might be struggling with starting NPX services. Try these steps:

1. Start only with the custom_mcp service (remove or comment out Tavily and Gmail services)
2. Install Node.js and NPM globally on your system
3. Run `npm install -g @smithery/cli` before starting the application
4. Try running the services manually in separate terminals to identify which one is causing issues

### Path Issues with MCP Server
If you encounter errors about not finding the MCP server path, try using the absolute path directly:

```python
"args": ["C:/full/path/to/langchain-mcp-chat-platform/own_mcp/mcp_server.py"]
```

### Static Files Not Found
If you get errors about static files not being found, check that you're running the application from the correct directory. The application expects to find `static` and `templates` folders.

## Integration with External Services

The platform integrates with several external services:

- **Google Gemini**: For natural language understanding and generation
- **Tavily**: For web search and content extraction
- **Gmail**: For email operations and management
- **Accounting System**: For financial management and tracking

## Important Notes

- API keys and sensitive information should be stored in the `.env` file
- The `.env` file is not tracked by Git for security reasons
- Always check the `.env.example` file for required environment variables
- The application is designed to be modular - you can disable specific services if needed
- **Smithery CLI Key**: The same Smithery CLI key is used to run both Tavily and Gmail MCP servers through the Smithery CLI. However, each service still requires its respective API key:
  - Tavily service requires its own TAVILY_API_KEY for web search functionality
  - Gmail service requires its own GMAIL_API_KEY for email operations

## Package Dependencies and Versioning

This application relies on specific versions of packages:
- langchain-prebuilt==0.1.5 is required for the create_react_agent function to work correctly
- Ensure you use langgraph==0.3.29 which is compatible with the other components
- When upgrading any packages, test thoroughly as newer versions may break compatibility

## License

MIT 

## Detailed Component Information

### Import Path for create_react_agent
The correct import for create_react_agent in newer versions of langgraph-prebuilt (0.1.5) is:
```python
from langgraph.prebuilt.task import create_react_agent
```

Do not use:
```python
from langgraph.prebuilt import create_react_agent  # This will cause errors
```

### API Keys Requirements

The following API keys are needed:
- GOOGLE_API_KEY - for Gemini model
- SMITHERY_KEY - for running both Tavily and Gmail MCP servers

