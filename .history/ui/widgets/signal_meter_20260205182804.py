"""
Sinyal seviyesi göstergesi widget'ı
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class SignalMeterWidget(QWidget):
    """RX/TX sinyal göstergesi widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI'ı başlat"""
        self.setObjectName("card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("📡 Sinyal Seviyesi")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # RX (Alıcı) sinyal
        rx_layout = QHBoxLayout()
        rx_label = QLabel("RX:")
        rx_label.setMinimumWidth(50)
        self.rx_bar = QProgressBar()
        self.rx_bar.setRange(0, 100)
        self.rx_bar.setValue(0)
        self.rx_bar.setTextVisible(True)
        self.rx_bar.setFormat("%v%")
        rx_layout.addWidget(rx_label)
        rx_layout.addWidget(self.rx_bar)
        layout.addLayout(rx_layout)
        
        # TX (Verici) sinyal
        tx_layout = QHBoxLayout()
        tx_label = QLabel("TX:")
        tx_label.setMinimumWidth(50)
        self.tx_bar = QProgressBar()
        self.tx_bar.setRange(0, 100)
        self.tx_bar.setValue(0)
        self.tx_bar.setTextVisible(True)
        self.tx_bar.setFormat("%v%")
        tx_layout.addWidget(tx_label)
        tx_layout.addWidget(self.tx_bar)
        layout.addLayout(tx_layout)
        
        # Ses seviyesi (Mikrofon)
        audio_layout = QHBoxLayout()
        audio_label = QLabel("MİK:")
        audio_label.setMinimumWidth(50)
        self.audio_bar = QProgressBar()
        self.audio_bar.setRange(0, 100)
        self.audio_bar.setValue(0)
        self.audio_bar.setTextVisible(True)
        self.audio_bar.setFormat("%v%")
        audio_layout.addWidget(audio_label)
        audio_layout.addWidget(self.audio_bar)
        layout.addLayout(audio_layout)
        
        # Durum
        self.status_label = QLabel("● Bağlantı Bekleniyor")
        self.status_label.setStyleSheet("color: #888;")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_rx_level(self, level: int):
        """RX sinyal seviyesini güncelle (0-100)"""
        self.rx_bar.setValue(max(0, min(100, level)))
    
    def update_tx_level(self, level: int):
        """TX sinyal seviyesini güncelle (0-100)"""
        self.tx_bar.setValue(max(0, min(100, level)))
    
    def update_audio_level(self, level: float):
        """Ses seviyesini güncelle (0-100)"""
        self.audio_bar.setValue(int(max(0, min(100, level))))
    
    def set_status(self, status: str, status_type: str = "info"):
        """
        Durum mesajını ayarla
        
        Args:
            status: Durum mesajı
            status_type: "info", "connected", "error"
        """
        icons = {
            "info": "●",
            "connected": "✓",
            "error": "✗"
        }
        colors = {
            "info": "#888",
            "connected": "#06d6a0",
            "error": "#e63946"
        }
        
        icon = icons.get(status_type, "●")
        color = colors.get(status_type, "#888")
        
        self.status_label.setText(f"{icon} {status}")
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setProperty("status", status_type)
