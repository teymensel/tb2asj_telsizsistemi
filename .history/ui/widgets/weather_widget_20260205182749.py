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
        self.setObjectName("card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("🌤️ Hava Durumu")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Şehir
        self.city_label = QLabel("--")
        self.city_label.setStyleSheet("font-size: 12pt; color: #aaa;")
        layout.addWidget(self.city_label)
        
        # Sıcaklık
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("""
            font-size: 36pt;
            font-weight: bold;
            color: #3282b8;
        """)
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.temp_label)
        
        # Açıklama
        self.desc_label = QLabel("--")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.desc_label)
        
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
