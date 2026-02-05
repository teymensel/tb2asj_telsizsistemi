"""
Deprem Listesi Widget'ı
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from datetime import datetime

class EarthquakeWidget(QWidget):
    """Son depremleri gösteren panel"""
    
    def __init__(self, earthquake_service):
        super().__init__()
        self.service = earthquake_service
        self.init_ui()
        
        # Servis bağlantıları
        self.service.data_updated.connect(self.update_list)
        self.service.error_occurred.connect(self.show_error)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık ve Butonlar
        top_bar = QHBoxLayout()
        
        title_label = QLabel("🌍 Son Depremler")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        top_bar.addWidget(title_label)
        
        top_bar.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Yenile")
        self.refresh_btn.clicked.connect(self.service.check_earthquakes)
        top_bar.addWidget(self.refresh_btn)
        
        layout.addLayout(top_bar)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Saat", "Büyüklük", "Konumu", "Derinlik"])
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        
        # Saat sütunu: Sabit genişlik (Tarih ve Saat için)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 110) # 60 -> 110 (Tarih için yer aç)
        
        # Büyüklük: İçeriğe göre
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # Konum: Kalan alanı kapla
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Derinlik: İçeriğe göre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Bilgi Satırı
        self.status_label = QLabel("Veri bekleniyor...")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.status_label)

    def update_list(self, earthquakes: list):
        """Listeyi güncelle"""
        print(f"[DEBUG] WIDGET UPDATE RECEIVED: {len(earthquakes)} items")
        try:
            self.table.setSortingEnabled(False)
            self.table.setRowCount(0)
            self.table.setRowCount(len(earthquakes))
            
            self.status_label.setText(f"Son Güncelleme: {len(earthquakes)} deprem listelendi.")
            
            for row, eq in enumerate(earthquakes):
                # Tarih/Saat parse et ve formatla
                date_str = str(eq.get('date', '')).strip()
                
                try:
                    # Kandilli formatı genelde: "2024.02.05 20:30:45"
                    # Biz bunu "05.02 20:30" yapmak istiyoruz
                    if '-' in date_str: # YYYY-MM-DD
                         dt_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    else: # YYYY.MM.DD
                         dt_obj = datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                         
                    time_val = dt_obj.strftime("%d.%m %H:%M")
                except Exception as e:
                    # Format uymazsa, direkt stringi göster (varsa)
                    # Yoksa "--" göster
                    # print(f"[DEBUG] Date parse error: {e} for {date_str}")
                    time_val = date_str if date_str else "--:--"
                
                # Renklendirme (Büyüklüğe göre)
                mag = float(eq.get('magnitude', 0.0))
                color = None
                if mag >= 5.0:
                    color = QColor("#e74c3c") # Kırmızı
                elif mag >= 4.0:
                    color = QColor("#e67e22") # Turuncu
                elif mag >= 3.0:
                    color = QColor("#f1c40f") # Sarı
                
                # Hücreleri oluştur
                # 0: Saat
                item_time = QTableWidgetItem(time_val)
                item_time.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, item_time)
                
                # 1: Büyüklük
                item_mag = QTableWidgetItem(f"{mag:.1f}")
                item_mag.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if color:
                    item_mag.setBackground(color)
                    item_mag.setForeground(Qt.GlobalColor.black if mag < 5.0 else Qt.GlobalColor.white)
                self.table.setItem(row, 1, item_mag)
                
                # 2: Konum
                item_loc = QTableWidgetItem(str(eq.get('location', '')))
                self.table.setItem(row, 2, item_loc)
                
                # 3: Derinlik
                depth = eq.get('depth', 0)
                item_depth = QTableWidgetItem(f"{depth} km")
                item_depth.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, item_depth)
                
            self.table.setSortingEnabled(True)
            
        except Exception as e:
            print(f"[HATA] Widget update error: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"Görünüm Hatası: {str(e)}")

    def show_error(self, message):
        self.status_label.setText(f"Hata: {message}")
        self.status_label.setStyleSheet("color: red;")
