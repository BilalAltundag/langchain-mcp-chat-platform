import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QMessageBox, QComboBox, QFrame, QHeaderView,
                             QSplitter, QToolBar, QStatusBar)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap

class MacStyleFrame(QFrame):
    """Mac tarzında bir çerçeve"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)

class ModernButton(QPushButton):
    """Modern Mac tarzı buton"""
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0062CC;
                }
                QPushButton:pressed {
                    background-color: #0051A8;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F2F2F7;
                    color: #007AFF;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #E5E5EA;
                }
                QPushButton:pressed {
                    background-color: #D1D1D6;
                }
            """)

class ModernLineEdit(QLineEdit):
    """Modern Mac tarzı metin girişi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #E5E5EA;
                padding: 8px;
                background-color: #F2F2F7;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #007AFF;
                background-color: #FFFFFF;
            }
        """)

class ModernComboBox(QComboBox):
    """Modern Mac tarzı açılır liste"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: none;
                border-bottom: 2px solid #E5E5EA;
                padding: 8px;
                background-color: #F2F2F7;
                border-radius: 6px;
            }
            QComboBox:focus {
                border-bottom: 2px solid #007AFF;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

class MuhasebeProgrami(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Muhasebe Asistanı")
        self.setGeometry(100, 100, 1200, 800)
        
        # Mac tarzı arka plan rengi
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F7;
            }
            QTableWidget {
                border: none;
                gridline-color: #E0E0E0;
                background-color: white;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #007AFF20;
                color: black;
            }
            QHeaderView::section {
                background-color: #F2F2F7;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: none;
                background-color: #F5F5F7;
            }
            QTabBar::tab {
                background-color: #F2F2F7;
                border: none;
                padding: 12px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007AFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E5E5EA;
            }
        """)
        
        # Veritabanı bağlantısını oluştur
        self.conn = sqlite3.connect('muhasebe.db')
        self.create_tables()
        
        # Ana widget'ı oluştur
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Üst bilgi alanı
        self.setup_header()
        
        # Tab widget'ı oluştur
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Daha modern görünüm
        self.layout.addWidget(self.tabs)
        
        # Tabları oluştur
        self.setup_gelir_tab()
        self.setup_gider_tab()
        self.setup_rapor_tab()
        
        # Durum çubuğu oluştur
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("QStatusBar{background-color: white; padding: 5px;}")
        self.status_bar.showMessage("Hazır")

        # Otomatik güncelleme için zamanlayıcı oluştur
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(1000)  # Her 1 saniyede bir güncelle
    
    def setup_header(self):
        """Üst bilgi alanını oluştur"""
        header_frame = MacStyleFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Başlık alanı
        app_title = QLabel("<h1>Muhasebe Asistanı</h1>")
        app_title.setStyleSheet("color: #333333; font-weight: bold;")
        
        date_label = QLabel(f"<h3>{datetime.now().strftime('%d %B %Y')}</h3>")
        date_label.setStyleSheet("color: #666666;")
        
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        
        self.layout.addWidget(header_frame)
    
    def update_all(self):
        """Tüm verileri güncelle"""
        self.gelir_listele()
        self.gider_listele()
        self.rapor_guncelle()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Gelirler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gelirler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT NOT NULL,
            aciklama TEXT NOT NULL,
            miktar REAL NOT NULL,
            kategori TEXT NOT NULL
        )
        ''')
        
        # Giderler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS giderler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT NOT NULL,
            aciklama TEXT NOT NULL,
            miktar REAL NOT NULL,
            kategori TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
    
    def setup_gelir_tab(self):
        gelir_tab = QWidget()
        layout = QVBoxLayout(gelir_tab)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # Gelir giriş formu
        form_frame = MacStyleFrame()
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Tarih - Bugünün tarihini otomatik ekle
        self.gelir_tarih = ModernLineEdit()
        self.gelir_tarih.setText(datetime.now().strftime('%Y-%m-%d'))
        
        tarih_label = QLabel("Tarih:")
        tarih_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(tarih_label)
        form_layout.addWidget(self.gelir_tarih)
        
        # Açıklama
        self.gelir_aciklama = ModernLineEdit()
        self.gelir_aciklama.setPlaceholderText("Gelir açıklaması...")
        
        aciklama_label = QLabel("Açıklama:")
        aciklama_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(aciklama_label)
        form_layout.addWidget(self.gelir_aciklama)
        
        # Miktar
        self.gelir_miktar = ModernLineEdit()
        self.gelir_miktar.setPlaceholderText("0.00")
        
        miktar_label = QLabel("Miktar (TL):")
        miktar_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(miktar_label)
        form_layout.addWidget(self.gelir_miktar)
        
        # Kategori
        self.gelir_kategori = ModernComboBox()
        self.gelir_kategori.addItems(["Satış", "Hizmet", "Diğer"])
        
        kategori_label = QLabel("Kategori:")
        kategori_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(kategori_label)
        form_layout.addWidget(self.gelir_kategori)
        
        # Ekle butonu
        ekle_btn = ModernButton("Gelir Ekle", primary=True)
        ekle_btn.clicked.connect(self.gelir_ekle)
        form_layout.addWidget(ekle_btn)
        
        layout.addWidget(form_frame)
        
        # Gelirler tablosu
        table_frame = MacStyleFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        table_title = QLabel("<h3>Gelir Kayıtları</h3>")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        self.gelirler_tablo = QTableWidget()
        self.gelirler_tablo.setColumnCount(5)
        self.gelirler_tablo.setHorizontalHeaderLabels(["ID", "Tarih", "Açıklama", "Miktar", "Kategori"])
        self.gelirler_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gelirler_tablo.setAlternatingRowColors(True)
        self.gelirler_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Sütun genişliklerini ayarla
        self.gelirler_tablo.setColumnWidth(0, 50)  # ID
        self.gelirler_tablo.setColumnWidth(1, 100)  # Tarih
        self.gelirler_tablo.setColumnWidth(2, 300)  # Açıklama
        self.gelirler_tablo.setColumnWidth(3, 100)  # Miktar
        self.gelirler_tablo.setColumnWidth(4, 100)  # Kategori
        
        table_layout.addWidget(self.gelirler_tablo)
        layout.addWidget(table_frame)
        
        self.tabs.addTab(gelir_tab, "Gelirler")
        self.gelir_listele()
    
    def setup_gider_tab(self):
        gider_tab = QWidget()
        layout = QVBoxLayout(gider_tab)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # Gider giriş formu
        form_frame = MacStyleFrame()
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Tarih - Bugünün tarihini otomatik ekle
        self.gider_tarih = ModernLineEdit()
        self.gider_tarih.setText(datetime.now().strftime('%Y-%m-%d'))
        
        tarih_label = QLabel("Tarih:")
        tarih_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(tarih_label)
        form_layout.addWidget(self.gider_tarih)
        
        # Açıklama
        self.gider_aciklama = ModernLineEdit()
        self.gider_aciklama.setPlaceholderText("Gider açıklaması...")
        
        aciklama_label = QLabel("Açıklama:")
        aciklama_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(aciklama_label)
        form_layout.addWidget(self.gider_aciklama)
        
        # Miktar
        self.gider_miktar = ModernLineEdit()
        self.gider_miktar.setPlaceholderText("0.00")
        
        miktar_label = QLabel("Miktar (TL):")
        miktar_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(miktar_label)
        form_layout.addWidget(self.gider_miktar)
        
        # Kategori
        self.gider_kategori = ModernComboBox()
        self.gider_kategori.addItems(["Kira", "Elektrik", "Su", "Personel", "Diğer"])
        
        kategori_label = QLabel("Kategori:")
        kategori_label.setStyleSheet("font-weight: bold;")
        
        form_layout.addWidget(kategori_label)
        form_layout.addWidget(self.gider_kategori)
        
        # Ekle butonu
        ekle_btn = ModernButton("Gider Ekle", primary=True)
        ekle_btn.clicked.connect(self.gider_ekle)
        form_layout.addWidget(ekle_btn)
        
        layout.addWidget(form_frame)
        
        # Giderler tablosu
        table_frame = MacStyleFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        table_title = QLabel("<h3>Gider Kayıtları</h3>")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        self.giderler_tablo = QTableWidget()
        self.giderler_tablo.setColumnCount(5)
        self.giderler_tablo.setHorizontalHeaderLabels(["ID", "Tarih", "Açıklama", "Miktar", "Kategori"])
        self.giderler_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.giderler_tablo.setAlternatingRowColors(True)
        self.giderler_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Sütun genişliklerini ayarla
        self.giderler_tablo.setColumnWidth(0, 50)  # ID
        self.giderler_tablo.setColumnWidth(1, 100)  # Tarih
        self.giderler_tablo.setColumnWidth(2, 300)  # Açıklama
        self.giderler_tablo.setColumnWidth(3, 100)  # Miktar
        self.giderler_tablo.setColumnWidth(4, 100)  # Kategori
        
        table_layout.addWidget(self.giderler_tablo)
        layout.addWidget(table_frame)
        
        self.tabs.addTab(gider_tab, "Giderler")
        self.gider_listele()
    
    def setup_rapor_tab(self):
        rapor_tab = QWidget()
        layout = QVBoxLayout(rapor_tab)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # Rapor özeti
        report_frame = MacStyleFrame()
        report_layout = QVBoxLayout(report_frame)
        report_layout.setContentsMargins(20, 20, 20, 20)
        
        self.rapor_ozet = QLabel()
        self.rapor_ozet.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 20px;
                background-color: #FFFFFF;
                border: none;
            }
        """)
        report_layout.addWidget(self.rapor_ozet)
        
        layout.addWidget(report_frame)
        
        # Kategoriye göre grafikler (gelecekte eklenebilir)
        charts_frame = MacStyleFrame()
        charts_layout = QVBoxLayout(charts_frame)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        charts_title = QLabel("<h3>Kategori Bazlı Analiz</h3>")
        charts_title.setAlignment(Qt.AlignCenter)
        charts_layout.addWidget(charts_title)
        
        # Grafikler için yer tutucu (gelecekte eklenebilir)
        charts_placeholder = QLabel("Kategori bazlı analizler burada görüntülenecek.")
        charts_placeholder.setAlignment(Qt.AlignCenter)
        charts_placeholder.setStyleSheet("color: #666666; padding: 40px;")
        charts_layout.addWidget(charts_placeholder)
        
        layout.addWidget(charts_frame)
        
        self.tabs.addTab(rapor_tab, "Rapor")
        self.rapor_guncelle()
    
    def gelir_ekle(self):
        try:
            tarih = self.gelir_tarih.text()
            aciklama = self.gelir_aciklama.text()
            miktar = float(self.gelir_miktar.text().replace(",", "."))
            kategori = self.gelir_kategori.currentText()
            
            # Veri doğrulama
            if not aciklama:
                raise ValueError("Açıklama boş olamaz!")
            if miktar <= 0:
                raise ValueError("Miktar 0'dan büyük olmalıdır!")
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO gelirler (tarih, aciklama, miktar, kategori)
            VALUES (?, ?, ?, ?)
            ''', (tarih, aciklama, miktar, kategori))
            
            self.conn.commit()
            
            # Formu temizle
            self.gelir_aciklama.clear()
            self.gelir_miktar.clear()
            
            # Tabloları ve raporu güncelle
            self.update_all()
            
            self.status_bar.showMessage(f"{aciklama} geliri başarıyla eklendi!", 3000)
        except ValueError as ve:
            QMessageBox.warning(self, "Hata", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Gelir eklenirken bir hata oluştu: {str(e)}")
    
    def gider_ekle(self):
        try:
            tarih = self.gider_tarih.text()
            aciklama = self.gider_aciklama.text()
            miktar = float(self.gider_miktar.text().replace(",", "."))
            kategori = self.gider_kategori.currentText()
            
            # Veri doğrulama
            if not aciklama:
                raise ValueError("Açıklama boş olamaz!")
            if miktar <= 0:
                raise ValueError("Miktar 0'dan büyük olmalıdır!")
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO giderler (tarih, aciklama, miktar, kategori)
            VALUES (?, ?, ?, ?)
            ''', (tarih, aciklama, miktar, kategori))
            
            self.conn.commit()
            
            # Formu temizle
            self.gider_aciklama.clear()
            self.gider_miktar.clear()
            
            # Tabloları ve raporu güncelle
            self.update_all()
            
            self.status_bar.showMessage(f"{aciklama} gideri başarıyla eklendi!", 3000)
        except ValueError as ve:
            QMessageBox.warning(self, "Hata", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Gider eklenirken bir hata oluştu: {str(e)}")
    
    def gelir_listele(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM gelirler ORDER BY tarih DESC')
        self.gelirler_tablo.setRowCount(0)
        
        for row_number, row_data in enumerate(cursor):
            self.gelirler_tablo.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if column_number == 3:  # Miktar sütunu
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    item.setText(f"{float(data):,.2f}")
                self.gelirler_tablo.setItem(row_number, column_number, item)
    
    def gider_listele(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM giderler ORDER BY tarih DESC')
        self.giderler_tablo.setRowCount(0)
        
        for row_number, row_data in enumerate(cursor):
            self.giderler_tablo.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if column_number == 3:  # Miktar sütunu
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    item.setText(f"{float(data):,.2f}")
                self.giderler_tablo.setItem(row_number, column_number, item)
    
    def rapor_guncelle(self):
        cursor = self.conn.cursor()
        
        # Toplam gelir
        cursor.execute('SELECT SUM(miktar) FROM gelirler')
        toplam_gelir = cursor.fetchone()[0] or 0
        
        # Toplam gider
        cursor.execute('SELECT SUM(miktar) FROM giderler')
        toplam_gider = cursor.fetchone()[0] or 0
        
        # Net durum
        net_durum = toplam_gelir - toplam_gider
        
        # Kategori bazlı gelirler
        cursor.execute('''
            SELECT kategori, SUM(miktar) 
            FROM gelirler 
            GROUP BY kategori 
            ORDER BY SUM(miktar) DESC
        ''')
        gelir_kategorileri = cursor.fetchall()
        
        # Kategori bazlı giderler
        cursor.execute('''
            SELECT kategori, SUM(miktar) 
            FROM giderler 
            GROUP BY kategori 
            ORDER BY SUM(miktar) DESC
        ''')
        gider_kategorileri = cursor.fetchall()
        
        # Rapor metnini güncelle
        rapor_text = f"""
        <div style='padding: 20px; background-color: white; border-radius: 10px;'>
            <h2 style='color: #333333; text-align: center; margin-bottom: 20px;'>Finansal Durum Raporu</h2>
            
            <div style='display: flex; justify-content: space-between; margin-bottom: 30px;'>
                <div style='background-color: #E8F5E9; padding: 20px; border-radius: 10px; width: 30%;'>
                    <h3 style='color: #2E7D32; text-align: center;'>Toplam Gelir</h3>
                    <p style='font-size: 24px; text-align: center; font-weight: bold; color: #2E7D32;'>{toplam_gelir:,.2f} TL</p>
                </div>
                
                <div style='background-color: #FFF3E0; padding: 20px; border-radius: 10px; width: 30%;'>
                    <h3 style='color: #E65100; text-align: center;'>Toplam Gider</h3>
                    <p style='font-size: 24px; text-align: center; font-weight: bold; color: #E65100;'>{toplam_gider:,.2f} TL</p>
                </div>
                
                <div style='background-color: {"#E8F5E9" if net_durum >= 0 else "#FFEBEE"}; padding: 20px; border-radius: 10px; width: 30%;'>
                    <h3 style='color: {"#2E7D32" if net_durum >= 0 else "#C62828"}; text-align: center;'>Net Durum</h3>
                    <p style='font-size: 24px; text-align: center; font-weight: bold; color: {"#2E7D32" if net_durum >= 0 else "#C62828"};'>{net_durum:,.2f} TL</p>
                </div>
            </div>
            
            <div style='display: flex; justify-content: space-between;'>
                <div style='width: 48%;'>
                    <h3 style='color: #2E7D32; margin-bottom: 10px;'>Gelir Kategorileri</h3>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <tr style='background-color: #E8F5E9;'>
                            <th style='padding: 10px; text-align: left;'>Kategori</th>
                            <th style='padding: 10px; text-align: right;'>Tutar</th>
                        </tr>
        """
        
        for kategori, miktar in gelir_kategorileri:
            rapor_text += f"""
                        <tr>
                            <td style='padding: 10px; border-bottom: 1px solid #E0E0E0;'>{kategori}</td>
                            <td style='padding: 10px; border-bottom: 1px solid #E0E0E0; text-align: right;'>{miktar:,.2f} TL</td>
                        </tr>
            """
        
        rapor_text += """
                    </table>
                </div>
                
                <div style='width: 48%;'>
                    <h3 style='color: #E65100; margin-bottom: 10px;'>Gider Kategorileri</h3>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <tr style='background-color: #FFF3E0;'>
                            <th style='padding: 10px; text-align: left;'>Kategori</th>
                            <th style='padding: 10px; text-align: right;'>Tutar</th>
                        </tr>
        """
        
        for kategori, miktar in gider_kategorileri:
            rapor_text += f"""
                        <tr>
                            <td style='padding: 10px; border-bottom: 1px solid #E0E0E0;'>{kategori}</td>
                            <td style='padding: 10px; border-bottom: 1px solid #E0E0E0; text-align: right;'>{miktar:,.2f} TL</td>
                        </tr>
            """
        
        rapor_text += f"""
                    </table>
                </div>
            </div>
            
            <p style='text-align: right; margin-top: 20px; color: #757575;'>
                <small>Son Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
            </p>
        </div>
        """
        
        self.rapor_ozet.setText(rapor_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Mac tarzı font ayarları
    font = QFont("SF Pro Display", 10)
    app.setFont(font)
    
    # Stil ayarları
    app.setStyle('Fusion')
    
    window = MuhasebeProgrami()
    window.show()
    sys.exit(app.exec()) 