"""
Bildirim yöneticisi - Telsiz üzerinden sesli bildirim gönderimi
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional, List, Dict
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
        
        # Varsayılan ayarlar
        self.test_message = "Bu bir sesli test bildirimidir."
        self.voice_id = None
    
    def get_available_voices(self) -> List[Dict]:
        """Sistemdeki mevcut sesleri listele"""
        voices_list = []
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                voices_list.append({
                    'id': voice.id,
                    'name': voice.name,
                    'lang': voice.languages[0] if hasattr(voice, 'languages') and voice.languages else 'Unknown'
                })
        except Exception as e:
            print(f"Ses listesi alınamadı: {e}")
        return voices_list
    
    def set_voice(self, voice_id: str):
        """Kullanılacak sesi ayarla"""
        self.voice_id = voice_id
    
    def set_test_message(self, message: str):
        """Test bildirim metnini ayarla"""
        if message:
            self.test_message = message
    
    def _speak_thread(self, message: str):
        """TTS işlemini ayrı thread'de yap"""
        with self.tts_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0) # Max ses
                
                # Seçili ses varsa onu kullan
                if self.voice_id:
                    engine.setProperty('voice', self.voice_id)
                else:
                    # Yoksa Türkçe bulmaya çalış (fallback)
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if 'turkish' in voice.name.lower() or 'türk' in voice.name.lower() or 'tr' in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                
                print(f"Konuşuluyor: {message}")
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS hatası: {e}")
            finally:
                pass
            
            # PTT kapat
            if self.radio_connection:
                QTimer.singleShot(200, self._finish_notification)
            else:
                self._finish_notification()
    
    def _finish_notification(self):
        """Bildirimi sonlandır"""
        if self.radio_connection:
            self.radio_connection.ptt_off()
        if self.vox_controller:
            # VOX durumunu geri yükle
            if hasattr(self, 'vox_was_enabled') and self.vox_was_enabled:
                self.vox_controller.enable_vox()
        
        self.notification_finished.emit()

    def send_notification(self, message: str, use_radio: bool = True) -> None:
        """Bildirim gönder"""
        self.notification_started.emit(message)
        
        if use_radio and self.vox_controller:
            self.vox_was_enabled = self.vox_controller.vox_enabled
            if self.vox_was_enabled:
                self.vox_controller.disable_vox()
            
            if self.radio_connection:
                self.radio_connection.ptt_on()
        
        # TTS thread başlat
        threading.Thread(target=self._speak_thread, args=(message,), daemon=True).start()

    def send_test_notification(self) -> None:
        """Test bildirimi gönder"""
        self.send_notification(self.test_message)
        
    def send_weather_notification(self, weather_data: dict) -> None:
        message = (
            f"{weather_data.get('city', '')} hava durumu. "
            f"Sıcaklık {weather_data.get('temperature', 0)} derece. "
            f"{weather_data.get('description', '')}."
        )
        self.send_notification(message)

    def send_earthquake_notification(self, earthquake_data: dict) -> None:
        message = (
            f"Deprem uyarısı! {earthquake_data.get('location', '')}. "
            f"Büyüklük {earthquake_data.get('magnitude', 0)}."
        )
        self.send_notification(message)
