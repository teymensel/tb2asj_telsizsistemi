from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class BatteryWidget(QWidget):
    """Batarya durumunu gösteren widget"""
    def __init__(self, battery_service):
        super().__init__()
        self.battery_service = battery_service
        self.setup_ui()
        
        # Sinyal
        self.battery_service.battery_updated.connect(self.update_status)
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Yüzde etiketi
        self.percent_label = QLabel("-%")
        self.percent_label.setStyleSheet("font-weight: bold; color: #bdc3c7;")
        
        # İkon etiketi (Basit bir Unicode pil veya text)
        self.icon_label = QLabel("🔋") 
        self.icon_label.setStyleSheet("font-size: 16px;")
        
        layout.addWidget(self.percent_label)
        layout.addWidget(self.icon_label)
        
        self.setLayout(layout)
        
    def update_status(self, percent: int, plugged: bool):
        """Durumu güncelle"""
        if plugged:
            status_text = f"%{percent} (Şarjda)"
            color = "#2ecc71" # Yeşil
            icon = "⚡"
        else:
            status_text = f"%{percent}"
            if percent <= 30:
                color = "#e74c3c" # Kırmızı
                icon = "🪫"
            else:
                color = "#bdc3c7" # Normal gri
                icon = "🔋"
                
        self.percent_label.setText(status_text)
        self.percent_label.setStyleSheet(f"font-weight: bold; color: {color};")
        self.icon_label.setText(icon)
        
        self.setToolTip(f"Batarya Durumu: {status_text}")
