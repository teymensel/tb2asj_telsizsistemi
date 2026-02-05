"""
Bildirim yöneticisi - Telsiz üzerinden sesli bildirim gönderimi
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional
import pyttsx3


class NotificationManager(QObject):
    """Bildirim yönetici sınıfı"""
    
    # Sinyaller
    notification_started = pyqtSignal(str)  # Bildirim başladı
    notification_finished = pyqtSignal()  # Bildirim tamamlandı
    
    def __init__(self, radio_connection=None, vox_controller=None):
        super().__init__()
        self.radio_connection = radio_connection
        self.vox_controller = vox_controller
        
        # Text-to-Speech motoru
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Konuşma hızı
            self.tts_engine.setProperty('volume', 1.0)  # Ses seviyesi
            
            # Türkçe ses varsa ayarla
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'turkish' in voice.name.lower() or 'türk' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"TTS motoru başlatılamadı: {e}")
            self.tts_engine = None
    
    def send_notification(self, message: str, use_radio: bool = True) -> None:
        """
        Bildirim gönder
        
        Args:
            message: Bildirim mesajı
            use_radio: Telsiz üzerinden gönderilsin mi?
        """
        self.notification_started.emit(message)
        
        if use_radio and self.vox_controller:
            # VOX'u geçici olarak devre dışı bırak
            vox_was_enabled = self.vox_controller.vox_enabled
            if vox_was_enabled:
                self.vox_controller.disable_vox()
            
            # PTT'yi manuel aktif et
            if self.radio_connection and self.radio_connection.is_connected:
                self.radio_connection.ptt_on()
                
                # TTS ile konuş
                if self.tts_engine:
                    try:
                        self.tts_engine.say(message)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        print(f"TTS hatası: {e}")
                
                # PTT'yi kapat
                QTimer.singleShot(500, self.radio_connection.ptt_off)
                
                # VOX'u geri aç
                if vox_was_enabled:
                    QTimer.singleShot(1000, self.vox_controller.enable_vox)
        else:
            # Sadece bilgisayar hoparlöründen çal
            if self.tts_engine:
                try:
                    self.tts_engine.say(message)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS hatası: {e}")
        
        self.notification_finished.emit()
    
    def send_weather_notification(self, weather_data: dict) -> None:
        """Hava durumu bildirimi gönder"""
        message = (
            f"{weather_data.get('city', 'Bilinmeyen şehir')} için hava durumu bilgisi. "
            f"Sıcaklık {weather_data.get('temperature', 0)} derece. "
            f"Hissedilen {weather_data.get('feels_like', 0)} derece. "
            f"{weather_data.get('description', '')}."
        )
        self.send_notification(message)
    
    def send_earthquake_notification(self, earthquake_data: dict) -> None:
        """Deprem bildirimi gönder"""
        message = (
            f"DİKKAT! Deprem bildirimi! "
            f"{earthquake_data.get('location', 'Bilinmeyen konum')} bölgesinde "
            f"büyüklüğü {earthquake_data.get('magnitude', 0)} olan bir deprem meydana geldi. "
        )
        self.send_notification(message)
    
    def send_test_notification(self) -> None:
        """Test bildirimi gönder"""
        message = "TB2ASJ telsiz sistemi test bildirimi. Sistem normal çalışıyor."
        self.send_notification(message)
