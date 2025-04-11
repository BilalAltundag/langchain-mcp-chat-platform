import asyncio
from contextlib import asynccontextmanager
from mcp import ClientSession
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import logging
import traceback
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
from typing import Dict, List, Optional
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model yapılandırması
try:
    # .env dosyasından API anahtarını al
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not google_api_key:
        logger.warning("GOOGLE_API_KEY bulunamadı. .env dosyasını kontrol edin.")
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None)

    logger.info("Google AI model başarıyla yapılandırıldı")
except Exception as e:
    logger.error(f"Model yapılandırma hatası: {str(e)}")
    logger.error(f"Hata detayı: {traceback.format_exc()}")
    raise

# Global değişken olarak agent tutulacak
agent = None
# Oturum bazlı hafıza saklama
session_memories = {}
# Aktif bağlantıları saklamak için
active_connections: Dict[str, WebSocket] = {}

# FastAPI uygulaması oluştur
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

def get_memory_for_session(session_id: str):
    """Oturum için hafıza döndür, yoksa oluştur"""
    if session_id not in session_memories:
        session_memories[session_id] = ChatMessageHistory(session_id=session_id)
    return session_memories[session_id]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başladığında MCP client'ı başlat
    global agent
    try:
        # .env dosyasından API anahtarlarını al
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        gmail_mcp_key = os.environ.get("GMAIL_MCP_KEY")
        
        if not tavily_api_key:
            logger.warning("TAVILY_API_KEY bulunamadı. .env dosyasını kontrol edin.")
        
        if not gmail_mcp_key:
            logger.warning("GMAIL_MCP_KEY bulunamadı. .env dosyasını kontrol edin.")
            
        async with MultiServerMCPClient(
            {
                "tavily-mcp": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@smithery/cli@latest",
                        "run",
                        "@tavily-ai/tavily-mcp",
                        "--key",
                        tavily_api_key or "API_KEY_REQUIRED"
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
                        gmail_mcp_key or "API_KEY_REQUIRED"
                    ]
                },
                "custom_mcp": {
                    "command": "python",
                    "args": ["./own_mcp/mcp_server.py"],
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
                    prompt="""Ben çok yönlü bir sohbet ve görev asistanıyım. Kullanıcının isteğini doğru anlayarak gerektiğinde aşağıdaki araçları kullanabilirim:

🔎 **Tavily (Web Search & Extract)**  
- Kullanıcı güncel bilgi, haber veya internetten bir şey araştırmamı isterse  
- "Ara", "bul", "güncel", "son gelişmeler", "haber", "webden", "internetten", "makale", "konu hakkında bilgi" gibi ifadeler geçiyorsa
- Hem arama hem içerik çıkarımı gerekiyorsa, "Tavily Search" ve "Tavily Extract" araçlarını beraber kullanırım.

📧 **Gmail Tool**  
- Kullanıcı e-posta göndermek, taslak oluşturmak, gelen kutusunu okumak veya e-postalarla ilgili bir işlem yapmak isterse  
- "Mail at", "e-posta gönder", "taslak hazırla", "şunu oku", "şunu sil", "etiketle", "gelen kutusu", "önemli", "şunu ara", "şunu bul" gibi ifadeler kullanılırsa  
- Uygun Gmail tool fonksiyonlarını çağırarak işlemi yaparım (örn. send_email, read_email, modify_email vs.)
- Kullanıcı mail istediğinde E-posta gövdesi, başlığı veya ekleri ne gerekiyorsa kendin isteğe göre oluştur ve gönder veya işlemleri yap.
- Maili yazarken, en uygun formatta kendine göre, kullanıcının rahat okuaycağı formatta yeniden yaz ve gönderirim.

📊 **Muhasebe Sistemi**  
- Kullanıcı fatura, gelir, gider, kasa, rapor, muhasebe gibi konulara dair bir istekte bulunursa  
- "Fatura kes", "gider raporu", "muhasebe tablosu", "bakiye", "cari hesap" gibi ifadeler geçiyorsa ilgili muhasebe aracını kullanırım.

🧠 Kullanım Kuralları:
- Tool'ları **yalnızca gerekli olduğunda** ve kullanıcı isteği **açıkça veya ima yoluyla** bunu belirttiğinde kullanırım.
- Kullanıcının isteğini analiz edip gereken tool'u **bir kez, birden çok kez veya hiç** kullanmam gerekebilir. Tamamen ihtiyaca bağlıdır.
- Eğer toollarda opsiyonel olan bir parametre varsa ve kullanıcı bunu belirtmezse varsayılan değeri kullanırım.
- Kullanıcı bir şey yapmanı istediyse yap. Spesifik değişken vermediyse genel. Sadece çok belirsiz bir durum varsa kullanıcıyı yönlendirmek için kısa bir açıklama yapabilirim.
- Her durumda, kullanıcının amacını ve bağlamı dikkate alarak en uygun aksiyonu alırım.

Hazırım. Ne yapmamı istersiniz?"""
                )
                
                logger.info("Agent başarıyla oluşturuldu")
                yield
                
            except Exception as e:
                logger.error(f"Agent oluşturma hatası: {str(e)}")
                logger.error(f"Hata detayı: {traceback.format_exc()}")
                yield
                
    except Exception as e:
        logger.error(f"MCP Client hatası: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        yield

app = FastAPI(lifespan=lifespan)

# Statik dosyalar için klasör tanımla
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def process_message(message: str, client_id: str):
    """Mesajı işle ve yanıtı döndür"""
    global agent
    
    if agent is None:
        return "Sistem henüz hazır değil. Lütfen biraz bekleyin."
        
    try:
        logger.info(f"Mesaj işleniyor: {message}")
        
        # Mevcut hafızayı kontrol et ve ekrana yazdır
        history_messages = []
        if client_id in session_memories:
            # Hafızadaki mesajları alıp ekrana yazdır
            messages = session_memories[client_id].messages
            logger.info(f"Hafızada {len(messages)} mesaj bulundu: {messages}")
            
            # Mesajları uygun formata dönüştür
            for msg in messages:
                if hasattr(msg, 'type') and msg.type == 'human':
                    history_messages.append({"role": "user", "content": msg.content})
                elif hasattr(msg, 'type') and msg.type == 'ai':
                    history_messages.append({"role": "assistant", "content": msg.content})
        
        # Kullanıcının yeni mesajını ekle
        all_messages = history_messages + [{"role": "user", "content": message}]
        logger.info(f"Agent'a gönderilen mesajlar: {all_messages}")
        
        # Tüm mesaj geçmişiyle birlikte agent'ı çağır
        response = await agent.ainvoke({"messages": all_messages})
        
        if response and isinstance(response, dict):
            if 'messages' in response and response['messages']:
                content = response['messages'][-1].content
                logger.info("Mesaj başarıyla işlendi")
                
                # Mesaj başarıyla işlendikten sonra hafızaya ekle
                if client_id not in session_memories:
                    session_memories[client_id] = ChatMessageHistory(session_id=client_id)
                session_memories[client_id].add_user_message(message)
                session_memories[client_id].add_ai_message(content)
                
                # Güncellenmiş hafızayı yazdır
                logger.info(f"Güncellenmiş hafıza: {session_memories[client_id].messages}")
                
                return content
        
        logger.warning("Beklenmeyen yanıt formatı")
        return "Yanıt alınamadı. Lütfen tekrar deneyin."
            
    except Exception as e:
        logger.error(f"Mesaj işlenirken hata: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        return f"Bir hata oluştu: {str(e)}"

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            # Mesajı işle (client_id ile oturum kontrolü)
            response = await process_message(user_message, client_id)
            
            # Yanıtı gönder
            await manager.send_message(json.dumps({
                "sender": "assistant",
                "message": response,
                "timestamp": message_data.get("timestamp", "")
            }), client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket hatası: {str(e)}")
        logger.error(f"Hata detayı: {traceback.format_exc()}")
        manager.disconnect(client_id)

if __name__ == "__main__":
    
    
    # Uvicorn web sunucusu ile çalıştır
    uvicorn.run(app, host="127.0.0.1", port=5001)