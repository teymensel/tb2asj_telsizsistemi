"""
Bildirim yöneticisi - Telsiz üzerinden sesli bildirim gönderimi
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional
import pyttsx3
import threading


class NotificationManager(QObject):
    """Bildirim yönetici sınıfı"""
    
    # Sinyaller
    notification_started = pyqtSignal(str)
    notification_finished = pyqtSignal()
    
    def __init__(self, radio_connection=None, vox_controller=None):
        super().__init__()
        self.radio_connection = radio_connection
        self.vox_controller = vox_controller
        self.tts_lock = threading.Lock()
    
    def _speak_thread(self, message: str):
        """TTS işlemini ayrı thread'de yap"""
        with self.tts_lock:
            try:
                # Her çağrıda motoru yeniden başlatmak daha güvenli olabilir
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0) # Max ses
                
                # Türkçe ses
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'turkish' in voice.name.lower() or 'türk' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS hatası: {e}")
            finally:
                # Bildirim bitti sinyali
                # Thread güvenliği için signal emit edilmeli ama burada basitçe geçelim
                pass
            
            # PTT kapat (gecikmeli)
            if self.radio_connection:
                # PTT'yi biraz daha tut ki telsiz kapanmasın
                QTimer.singleShot(500, self._finish_notification)
    
    def _finish_notification(self):
        """Bildirimi sonlandır"""
        if self.radio_connection:
            self.radio_connection.ptt_off()
        if self.vox_controller:
            # Loopback kapatmak gerekebilir mi? Hayır, zaten PTT açarken loopback açmadık.
            # TTS sesi sistem sesinden gidiyor, loopback mikrofon sesi için.
            # Ancak AUX ile bağlı olduğu için sistem çıkışı zaten telsize gidiyor.
            # Sadece PTT (eğer COM varsa) kapatmak yeterli.
            
            # VOX'u geri getir
            if hasattr(self, 'vox_was_enabled') and self.vox_was_enabled:
                self.vox_controller.enable_vox()
        
        self.notification_finished.emit()

    def send_notification(self, message: str, use_radio: bool = True) -> None:
        """Bildirim gönder"""
        print(f"Bildirim gönderiliyor: {message}")
        self.notification_started.emit(message)
        
        if use_radio and self.vox_controller:
            # VOX durumunu kaydet ve kapat
            self.vox_was_enabled = self.vox_controller.vox_enabled
            if self.vox_was_enabled:
                self.vox_controller.disable_vox()
            
            # PTT aç (COM port varsa telsizi açar)
            if self.radio_connection:
                self.radio_connection.ptt_on()
        
        # TTS thread başlat
        threading.Thread(target=self._speak_thread, args=(message,), daemon=True).start()

    def send_test_notification(self) -> None:
        """Test bildirimi gönder"""
        message = "TB2ASJ telsiz sistemi ses testi. Bir, iki, üç. Ses kontrol."
        self.send_notification(message)
        
    def send_weather_notification(self, weather_data: dict) -> None:
        message = (
            f"Hava durumu raporu. {weather_data.get('city', '')}. "
            f"Sıcaklık {weather_data.get('temperature', 0)} derece."
        )
        self.send_notification(message)

    def send_earthquake_notification(self, earthquake_data: dict) -> None:
        message = (
            f"Dikkat! Deprem uyarısı. {earthquake_data.get('location', '')}. "
            f"Büyüklük {earthquake_data.get('magnitude', 0)}."
        )
        self.send_notification(message)
