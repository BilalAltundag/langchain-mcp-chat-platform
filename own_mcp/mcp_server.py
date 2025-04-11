from mcp.server.fastmcp import FastMCP
import sqlite3
import time
import signal
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Get the absolute path for the database
DB_PATH = "D:/cursor_project/app/muhasebe.db"

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    print("Shutting down server gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Database initialization
def init_db():
    print(f"Initializing database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS gelirler
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  aciklama TEXT NOT NULL,
                  miktar REAL NOT NULL,
                  kategori TEXT NOT NULL,
                  tarih TEXT NOT NULL)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS giderler
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  aciklama TEXT NOT NULL,
                  miktar REAL NOT NULL,
                  kategori TEXT NOT NULL,
                  tarih TEXT NOT NULL)''')
                  
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Initialize database on startup
init_db()

# Create an MCP server
mcp = FastMCP(
    name="muhasebe-r",
    host="127.0.0.1",
    port=5000,
    timeout=30
)

# Database helper functions
def get_db():
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def gelir_ekle(aciklama: str, miktar: float, kategori: str = "Genel") -> Dict:
    """Yeni bir gelir kaydı ekle. Eğer kategori girilmezse varsayılan olarak Genel kategorisi seçilir.
    
    Args:
        aciklama: Gelirin açıklaması
        miktar: Gelir miktarı (TL)
        kategori: Gelir kategorisi (varsayılan: Genel)
    
    Returns:
        Eklenen gelir kaydı bilgileri
    """
    try:
        if not isinstance(miktar, (int, float)) or miktar <= 0:
            return {"error": "Geçersiz miktar"}
            
        conn = get_db()
        c = conn.cursor()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''INSERT INTO gelirler (aciklama, miktar, kategori, tarih)
                    VALUES (?, ?, ?, ?)''', (aciklama, miktar, kategori, tarih))
        
        gelir_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": gelir_id,
            "aciklama": aciklama,
            "miktar": miktar,
            "kategori": kategori,
            "tarih": tarih
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def gider_ekle(aciklama: str, miktar: float, kategori: str = "Genel") -> Dict:
    """Yeni bir gider kaydı ekle. Eğer kategori girilmezse varsayılan olarak Genel kategorisi seçilir.
    
    Args:
        aciklama: Giderin açıklaması
        miktar: Gider miktarı (TL)
        kategori: Gider kategorisi (varsayılan: Genel)
    
    Returns:
        Eklenen gider kaydı bilgileri
    """
    try:
        if not isinstance(miktar, (int, float)) or miktar <= 0:
            return {"error": "Geçersiz miktar"}
            
        conn = get_db()
        c = conn.cursor()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''INSERT INTO giderler (aciklama, miktar, kategori, tarih)
                    VALUES (?, ?, ?, ?)''', (aciklama, miktar, kategori, tarih))
        
        gider_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": gider_id,
            "aciklama": aciklama,
            "miktar": miktar,
            "kategori": kategori,
            "tarih": tarih
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def gelirleri_listele(kategori: Optional[str] = None) -> List[Dict]:
    """Gelir kayıtlarını listeler. İsteğe bağlı olarak kategoriye göre filtreleme yapılabilir.
    
    Args:
        kategori: Filtrelemek için kategori (opsiyonel)
    
    Returns:
        Gelir kayıtları listesi
    """
    try:
        conn = get_db()
        c = conn.cursor()
        
        if kategori:
            c.execute('SELECT * FROM gelirler WHERE kategori = ? ORDER BY tarih DESC', (kategori,))
        else:
            c.execute('SELECT * FROM gelirler ORDER BY tarih DESC')
            
        gelirler = []
        for row in c.fetchall():
            gelirler.append({
                "id": row[0],
                "aciklama": row[1],
                "miktar": row[2],
                "kategori": row[3],
                "tarih": row[4]
            })
            
        conn.close()
        return gelirler
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def giderleri_listele(kategori: Optional[str] = None) -> List[Dict]:
    """Gelir kayıtlarını listeler. İsteğe bağlı olarak kategoriye göre filtreleme yapılabilir.Gider kayıtlarını listele.
    
    Args:
        kategori: Filtrelemek için kategori (opsiyonel)
    
    Returns:
        Gider kayıtları listesi
    """
    try:
        conn = get_db()
        c = conn.cursor()
        
        if kategori:
            c.execute('SELECT * FROM giderler WHERE kategori = ? ORDER BY tarih DESC', (kategori,))
        else:
            c.execute('SELECT * FROM giderler ORDER BY tarih DESC')
            
        giderler = []
        for row in c.fetchall():
            giderler.append({
                "id": row[0],
                "aciklama": row[1],
                "miktar": row[2],
                "kategori": row[3],
                "tarih": row[4]
            })
            
        conn.close()
        return giderler
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def rapor_getir(baslangic_tarih: Optional[str] = None, bitis_tarih: Optional[str] = None) -> Dict:
    """Finansal raporu getir. İsteğe bağlı baslangic_tarih ve bitis_tarih girebilir. Girilmez ise tüm zamanlar için rapor getirir.
    
    Args:
        baslangic_tarih: Başlangıç tarihi (YYYY-MM-DD formatında, opsiyonel)
        bitis_tarih: Bitiş tarihi (YYYY-MM-DD formatında, opsiyonel)
    
    Returns:
        Toplam gelir, gider ve bakiye bilgileri
    """
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Tarih filtreleri için SQL sorguları
        date_filter = ""
        params = []
        if baslangic_tarih and bitis_tarih:
            date_filter = "WHERE date(tarih) BETWEEN ? AND ?"
            params = [baslangic_tarih, bitis_tarih]
        
        # Toplam gelir
        c.execute(f'SELECT SUM(miktar) FROM gelirler {date_filter}', params)
        toplam_gelir = c.fetchone()[0] or 0
        
        # Toplam gider
        c.execute(f'SELECT SUM(miktar) FROM giderler {date_filter}', params)
        toplam_gider = c.fetchone()[0] or 0
        
        # Kategori bazlı gelirler
        c.execute(f'''SELECT kategori, SUM(miktar) 
                     FROM gelirler {date_filter}
                     GROUP BY kategori''', params)
        gelir_kategorileri = {row[0]: row[1] for row in c.fetchall()}
        
        # Kategori bazlı giderler
        c.execute(f'''SELECT kategori, SUM(miktar) 
                     FROM giderler {date_filter}
                     GROUP BY kategori''', params)
        gider_kategorileri = {row[0]: row[1] for row in c.fetchall()}
        
        conn.close()
        
        return {
            "toplam_gelir": toplam_gelir,
            "toplam_gider": toplam_gider,
            "net_durum": toplam_gelir - toplam_gider,
            "gelir_kategorileri": gelir_kategorileri,
            "gider_kategorileri": gider_kategorileri,
            "tarih_araligi": {
                "baslangic": baslangic_tarih or "Tüm zamanlar",
                "bitis": bitis_tarih or "Tüm zamanlar"
            }
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        print("Starting MCP server 'muhasebe-r' on 127.0.0.1:5000")
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)