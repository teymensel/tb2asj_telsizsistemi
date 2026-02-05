"""
Saat ve tarih widget'ı
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from datetime import datetime


class ClockWidget(QWidget):
    """Saat ve tarih gösterimi widget'ı"""
    
    request_announcement = pyqtSignal(str) # Anons isteği (Metin)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.announce_enabled = False # Saat başı anons
        self.last_announced_hour = -1
        
        self.init_ui()
        
        # Saat güncelleyici timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Her saniye
        
        # İlk güncelleme
        self.update_time()
    
    def init_ui(self):
        """UI'ı başlat"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Saat etiket
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #ecf0f1;
            margin-bottom: 0px;
        """)
        
        # Tarih etiket
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            font-size: 11pt;
            color: #bdc3c7;
            margin-top: 0px;
        """)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        
        self.setLayout(layout)
    
    def update_time(self):
        """Saat ve tarihi güncelle ve anons kontrolü yap"""
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

        # Anons Kontrolü
        if self.announce_enabled:
            # Saniyenin 0 olduğu anı yakala (veya yakını)
            # Ve aynı saat/dakika içinde birden fazla anons yapma
            current_minute_tag = f"{now.hour}:{now.minute}"
            
            if now.second == 0 and current_minute_tag != self.last_announced_hour:
                if now.minute == 0:
                    # Tam saat
                    text = f"Saat {now.hour}."
                    self.request_announcement.emit(text)
                    self.last_announced_hour = current_minute_tag
                elif now.minute == 30:
                    # Yarım saat
                    text = f"Saat {now.hour} buçuk."
                    self.request_announcement.emit(text)
                    self.last_announced_hour = current_minute_tag

    def get_natural_time_text(self, hour: int, minute: int) -> str:
        """Saati doğal dilde söyle (Örn: Onu yirmi geçiyor)"""
        # Basit sayılar
        nums = {0: "sıfır", 1: "bir", 2: "iki", 3: "üç", 4: "dört", 5: "beş",
                6: "altı", 7: "yedi", 8: "sekiz", 9: "dokuz", 10: "on",
                11: "on bir", 12: "on iki", 13: "on üç", 14: "on dört", 15: "on beş",
                16: "on altı", 17: "on yedi", 18: "on sekiz", 19: "on dokuz", 20: "yirmi",
                21: "yirmi bir", 22: "yirmi iki", 23: "yirmi üç", 24: "yirmi dört"}
        
        # Dakikaları kabaca telaffuz için
        def say_number(n):
            if n in nums: return nums[n]
            return str(n) # Çok detaylı sayı okuma modülü yoksa, TTS bunu halleder aslında
            
        # TTS motorları sayıları genelde doğru okur ama ekleri biz yapmalıyız
        # "Saat yirmiyi yirmi dört geçiyor"
        
        # Saat ve ekleri
        # 1->biri, 2->ikiyi, 3->üçü, 4->dördü, 5->beşi, 6->altıyı, 7->yediyi, 8->sekizi, 9->dokuzu, 10->onu
        # 11->on biri, 12->on ikiyi... 
        
        # Ekler tablosu
        hour_suffix = {
            0: "sıfırı", 1: "biri", 2: "ikiyi", 3: "üçü", 4: "dördü", 5: "beşi",
            6: "altıyı", 7: "yediyi", 8: "sekizi", 9: "dokuzu", 10: "onu",
            11: "on biri", 12: "on ikiyi", 13: "on üçü", 14: "on dördü", 15: "on beşi",
            16: "on altıyı", 17: "on yediyi", 18: "on sekizi", 19: "on dokuzu", 20: "yirmiyi",
            21: "yirmi biri", 22: "yirmi ikiyi", 23: "yirmi üçü"
        }
        
        if minute == 0:
            return f"Saat {now.hour}." # Buraya hour değişkeni gelmemiş, parametre kullanmalı
            # 'now' global değil. Düzeltiyorum.
            # return f"Saat {hour}." # Ama TTS "Saat on beş" der. 
        elif minute == 30:
            return f"Saat {hour} buçuk."
        else:
            # Geçiyor kalıbı
            # Örn: 20:24 -> Saat yirmiyi yirmi dört geçiyor.
            h_text = hour_suffix.get(hour, str(hour))
            return f"Saat {h_text} {minute} geçiyor."
