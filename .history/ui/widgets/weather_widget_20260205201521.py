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
        
        # Detaylar
        details_layout = QHBoxLayout()
        
        self.humidity_label = QLabel("💧 --%")
        self.wind_label = QLabel("💨 -- km/s")
        
        details_layout.addWidget(self.humidity_label)
        details_layout.addWidget(self.wind_label)
        
        layout.addLayout(details_layout)
        
        # Yenile butonu
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_clicked)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_clicked(self):
        """Yenile butonuna tıklandı - Ana pencere handle edecek"""
        pass
    
    def update_weather(self, data: dict):
        """Hava durumu verisini güncelle"""
        self.city_label.setText(data.get('city', '--'))
        self.temp_label.setText(f"{data.get('temperature', '--')}°C")
        self.desc_label.setText(data.get('description', '--').capitalize())
        self.humidity_label.setText(f"💧 {data.get('humidity', '--')}%")
        self.wind_label.setText(f"💨 {data.get('wind_speed', '--')} km/s")
