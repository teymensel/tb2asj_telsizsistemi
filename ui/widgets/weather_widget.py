"""
Hava durumu kartı widget'ı
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class WeatherWidget(QWidget):
    """Hava durumu gösterim widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI'ı başlat"""
        self.setObjectName("weather_widget")
        self.setStyleSheet("#weather_widget { background: transparent; }")
        
        layout = QHBoxLayout() # Yatay düzen (Kompakt)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Sol: Şehir ve Durum
        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)
        
        self.city_label = QLabel("--")
        self.city_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #ecf0f1;")
        
        self.desc_label = QLabel("--")
        self.desc_label.setStyleSheet("font-size: 9pt; color: #bdc3c7;")
        
        left_layout.addWidget(self.city_label)
        left_layout.addWidget(self.desc_label)
        layout.addLayout(left_layout)
        
        # Sağ: Sıcaklık
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            color: #3498db;
        """)
        layout.addWidget(self.temp_label)
        
        # Detaylar (Gizle veya çok küçük yap)
        # self.humidity_label... (Kaldırıldı, tooltip yapılabilir)
        
        self.setLayout(layout)
        
    def update_weather(self, data: dict):
        """Hava durumu verisini güncelle"""
        self.city_label.setText(data.get('city', '--'))
        self.temp_label.setText(f"{data.get('temperature', '--')}°")
        self.desc_label.setText(data.get('description', '--').capitalize())
        
        # Tooltip olarak detay ekle
        self.setToolTip(f"Nem: %{data.get('humidity', '--')} | Rüzgar: {data.get('wind_speed', '--')} km/s")
