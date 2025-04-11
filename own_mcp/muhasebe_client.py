import asyncio
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import logging
import traceback

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment değişkenlerini yükle
load_dotenv()

# Groq modelini yapılandır
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    model = ChatGroq(
        model_name="llama3-8b-8192",
        temperature=0.1,
        max_tokens=4096,
        groq_api_key=groq_api_key
    )
    logger.info("Groq model başarıyla yapılandırıldı")
except Exception as e:
    logger.error(f"Groq model yapılandırma hatası: {str(e)}")
    logger.error(f"Hata detayı: {traceback.format_exc()}")
    raise

@asynccontextmanager
async def make_muhasebe_client():
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    logger.info(f"MCP Server yolu: {server_path}")
    
    if not os.path.exists(server_path):
        error_msg = f"MCP Server dosyası bulunamadı: {server_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    server_params = StdioServerParameters(
        command="python",
        args=[server_path]
    )
    
    try:
        logger.info("MCP Client başlatılıyor...")
        async with stdio_client(server_params) as (read, write):
            logger.info("stdio_client başarıyla başlatıldı")
            try:
                async with ClientSession(read, write) as session:
                    logger.info("ClientSession başarıyla oluşturuldu")
                    
                    try:
                        await session.initialize()
                        logger.info("Session başarıyla initialize edildi")
                    except Exception as e:
                        logger.error(f"Session initialize hatası: {str(e)}")
                        logger.error(f"Hata detayı: {traceback.format_exc()}")
                        raise
                    
                    try:
                        # Get tools using the official method
                        logger.info("MCP tools yükleniyor...")
                        tools = await load_mcp_tools(session)
                        logger.info(f"MCP tools başarıyla yüklendi: {len(tools)} tool bulundu")
                        
                        # Create the agent
                        logger.info("Agent oluşturuluyor...")
                        agent = create_react_agent(model, tools)
                        logger.info("Agent başarıyla oluşturuldu")
                        
                        yield agent
                    except Exception as e:
                        logger.error(f"Agent oluşturma hatası: {str(e)}")
                        logger.error(f"Hata detayı: {traceback.format_exc()}")
                        raise
                    
            except Exception as e:
                logger.error(f"ClientSession hatası: {str(e)}")
                logger.error(f"Hata detayı: {traceback.format_exc()}")
                raise
                
    except Exception as e:
        logger.error(f"MCP Client hatası: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        raise

async def run_query(agent, query: str):
    """Sorguyu çalıştır ve sonucu yazdır"""
    try:
        logger.info(f"Sorgu çalıştırılıyor: {query}")
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=query)]}
        )
        if response and 'messages' in response and response['messages']:
            logger.info("Sorgu başarıyla tamamlandı")
            logger.info(f"Yanıt: {response['messages'][-1].content}")
            return response
        else:
            logger.warning("Yanıt alınamadı")
            return None
    except Exception as e:
        logger.error(f"Sorgu çalıştırılırken hata oluştu: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        raise

async def main():
    try:
        async with make_muhasebe_client() as agent:
            logger.info("\nMuhasebe sistemi başlatıldı!")
            print("İnteraktif mod (Çıkmak için 'quit' yazın)")
            
            while True:
                try:
                    user_input = input("\nSorgunuz: ")
                    if user_input.lower() == 'quit':
                        break
                    await run_query(agent, user_input)
                except KeyboardInterrupt:
                    logger.info("Program kullanıcı tarafından sonlandırıldı")
                    break
                except Exception as e:
                    logger.error(f"Beklenmeyen hata: {str(e)}")
                    logger.error(f"Hata detayı: {traceback.format_exc()}")
    except Exception as e:
        logger.error(f"Program başlatılırken hata oluştu: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program sonlandırıldı")
    except Exception as e:
        logger.error(f"Kritik hata: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}") 