"""
Saat ve tarih widget'ı
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime


class ClockWidget(QWidget):
    """Saat ve tarih gösterimi widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Saat güncelleyici timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Her saniye
        
        # İlk güncelleme
        self.update_time()
    
    def init_ui(self):
        """UI'ı başlat"""
        layout =VBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Saat etiket
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 32pt;
            font-weight: bold;
            color: #3282b8;
        """)
        
        # Tarih etiket
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            font-size: 14pt;
            color: #aaa;
        """)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        
        self.setLayout(layout)
    
    def update_time(self):
        """Saat ve tarihi güncelle"""
        now = datetime.now()
        
        # Türkçe gün isimleri
        days_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        months_tr = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        
        # Saat formatı
        time_str = now.strftime('%H:%M:%S')
        self.time_label.setText(time_str)
        
        # Tarih formatı
        day_name = days_tr[now.weekday()]
        month_name = months_tr[now.month - 1]
        date_str = f"{day_name}, {now.day} {month_name} {now.year}"
        self.date_label.setText(date_str)
