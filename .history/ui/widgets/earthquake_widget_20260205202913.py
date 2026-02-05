"""
Deprem Listesi Widget'ı
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

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
        self.table.setRowCount(0)
        self.status_label.setText(f"Son Güncelleme: {len(earthquakes)} deprem listelendi.")
        
        for eq in earthquakes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Tarih/Saat parse et (YYYY.MM.DD HH:MM:SS -> HH:MM)
            date_str = eq['date']
            try:
                time_val = date_str.split(' ')[1][:5]
            except:
                time_val = date_str
            
            # Renklendirme (Büyüklüğe göre)
            mag = eq['magnitude']
            color = None
            if mag >= 5.0:
                color = QColor("#ffcccc") # Kırmızımsı
            elif mag >= 3.0:
                color = QColor("#fff4cc") # Sarımsı
            
            # Hücreleri oluştur
            items = [
                QTableWidgetItem(time_val),
                QTableWidgetItem(str(mag)),
                QTableWidgetItem(eq['location']),
                QTableWidgetItem(f"{eq['depth']} km")
            ]
            
            for col, item in enumerate(items):
                if color:
                    item.setBackground(color)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 2 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)

    def show_error(self, message):
        self.status_label.setText(f"Hata: {message}")
        self.status_label.setStyleSheet("color: red;")
