"""
Log Penceresi Widget'ı
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                             QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QColor
import datetime

class LogWindow(QWidget):
    """Sistem loglarını gösteren pencere"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Başlık ve Temizle Butonu
        top_bar = QHBoxLayout()
        
        title = QLabel("📝 Sistem Kayıtları")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        top_bar.addWidget(title)
        
        top_bar.addStretch()
        
        clear_btn = QPushButton("Temizle")
        clear_btn.setFixedSize(60, 24)
        clear_btn.setStyleSheet("font-size: 11px; padding: 2px;")
        clear_btn.clicked.connect(self.clear_logs)
        top_bar.addWidget(clear_btn)
        
        layout.addLayout(top_bar)
        
        # Log Alanı
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #333;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Başlangıç mesajı
        self.add_log("Sistem başlatıldı.", "info")

    def add_log(self, message: str, level: str = "info"):
        """Log ekle"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        color = "#dcdcdc" # Default (info)
        if level == "error":
            color = "#ff6b6b"
        elif level == "warning":
            color = "#feca57"
        elif level == "success":
            color = "#1dd1a1"
            
        formatted_msg = f'<span style="color: #666;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        self.text_edit.append(formatted_msg)
        
        # Otomatik kaydır
        sb = self.text_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_logs(self):
        self.text_edit.clear()
        self.add_log("Loglar temizlendi.")
