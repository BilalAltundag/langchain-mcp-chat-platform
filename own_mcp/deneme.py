import asyncio
import asyncio
from contextlib import asynccontextmanager
from mcp import ClientSession
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import signal
import os
import sys
import time
import logging
import traceback

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Model yapılandırması
try:
    os.environ["GROQ_API_KEY"] ="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"
    # Initialize Groq model with llama3
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAg3NSss60mZ4SOtRzeu1Pu-YGaoiIT9MA"
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    model = ChatGoogleGenerativeAI(
        model="gemini-exp-1206",
        temperature=0,
        max_tokens=None)

    logger.info("Google AI model başarıyla yapılandırıldı")
except Exception as e:
    logger.error(f"Model yapılandırma hatası: {str(e)}")
    logger.error(f"Hata detayı: {traceback.format_exc()}")
    raise
    
@asynccontextmanager
async def make_mcp_client():
    try:  
        async with MultiServerMCPClient(
            {
                "mcp-tavily": {
                    "command": "cmd",
                    "args": [
                        "/c",
                        "npx",
                        "-y",
                        "@smithery/cli@latest",
                        "run",
                        "mcp-tavily",
                        "--key",
                        "9304aa7f-e1c2-4449-b560-2d22691df4af"
                    ]
                    },
                        "server-gmail-autoauth-mcp": {
                        "command": "cmd",
                        "args": [
                            "/c",
                            "npx",
                            "-y",
                            "@smithery/cli@latest",
                            "run",
                            "@gongrzhe/server-gmail-autoauth-mcp",
                            "--key",
                            "9304aa7f-e1c2-4449-b560-2d22691df4af"
                        ]
                        },
                "custom_mcp": {
                    "command": "python",
                    "args": ["./mcp_server.py"],
                    "transport": "stdio",
                }
            }
        ) as client:
                logger.info("MCP Client başarıyla başlatıldı")
                
                try:
                    # Create the agent with tools
                    agent = create_react_agent(
                        model, 
                        client.get_tools(),
                        prompt="""Ben genel bir sohbet asistanıyım. İhtiyaç duyulduğunda şu araçları kullanabilirim:

    - Güncel bilgi araması gerektiğinde Tavily'yi kullanabilirim
    - E-posta göndermem istendiğinde Gmail'i kullanabilirim
    - Muhasebe işlemleri sorulduğunda muhasebe sistemini kullanabilirim

    Ancak bu araçları sadece açıkça istendiğinde kullanırım. """
                    )
                    logger.info("Agent başarıyla oluşturuldu")
                    yield agent
                    
                except Exception as e:
                    logger.error(f"Agent oluşturma hatası: {str(e)}")
                    logger.error(f"Hata detayı: {traceback.format_exc()}")
                    raise

    except Exception as e:
            logger.error(f"MCP Client hatası: {str(e)}")
            logger.error(f"Hata detayı: {traceback.format_exc()}")
            raise

async def process_message(agent, message: str):
    """Mesajı işle ve yanıtı döndür"""
    try:
        logger.info(f"Mesaj işleniyor: {message}")
        response = await agent.ainvoke({"messages": message})
        
        if response and 'messages' in response:
            content = response['messages'][-1].content
            logger.info("Mesaj başarıyla işlendi")
            return content
        else:
            logger.warning("Yanıt alınamadı")
            return None
            
    except Exception as e:
        logger.error(f"Mesaj işlenirken hata: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        raise

async def main():
    try:
        async with make_mcp_client() as agent:
            logger.info("Sistem başlatıldı!")
            print("İnteraktif mod (Çıkmak için 'quit' yazın)")
            
            while True:
                try:
                    user_input = input("\nSiz: ")
                    if user_input.lower() == 'quit':
                        break
                        
                    response = await process_message(agent, user_input)
                    if response:
                        print("\nAssistant:", response)
                        
                except KeyboardInterrupt:
                    logger.info("Program kullanıcı tarafından sonlandırıldı")
                    break
                except Exception as e:
                    logger.error(f"Beklenmeyen hata: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Program başlatılırken hata: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())