import sqlite3

def create_database():
    # Veritabanı bağlantısını oluştur
    conn = sqlite3.connect('muhasebe.db')
    cursor = conn.cursor()

    # Gelirler tablosunu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gelirler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih DATE NOT NULL,
        aciklama TEXT NOT NULL,
        miktar REAL NOT NULL,
        kategori TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Giderler tablosunu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS giderler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih DATE NOT NULL,
        aciklama TEXT NOT NULL,
        miktar REAL NOT NULL,
        kategori TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Değişiklikleri kaydet ve bağlantıyı kapat
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Veritabanı ve tablolar başarıyla oluşturuldu.") 