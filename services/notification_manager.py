"""
Bildirim yöneticisi - Gelişmiş TTS ve Çoklu Motor Desteği
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional, List, Dict
import threading
import os
import time
import pygame
from services.tts.factory import TTSFactory

# Pygame mixer init
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Pygame mixer başlatılamadı: {e}")

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
        
        # TTS Provider kurulumu
        self.providers = TTSFactory.get_providers()
        self.current_provider = self.providers[0] # Varsayılan: Edge TTS
        
        # Varsayılan ayarlar
        self.test_message = "TB2ASJ telsiz sistemi ses kontrolü. Bir iki üç."
        
        # Temp klasörü
        self.temp_dir = os.path.join(os.getcwd(), 'temp_audio')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        # Roger Beep Ayarı
        self.roger_beep_enabled = False
        self.roger_beep_path = os.path.join(self.temp_dir, 'roger_beep.wav')
        self._generate_roger_beep() # Dosyayı oluştur
            
    def get_providers_list(self) -> List[str]:
        return [p.get_name() for p in self.providers]
        
    def set_provider(self, provider_name: str):
        for p in self.providers:
            if p.get_name() == provider_name:
                self.current_provider = p
                print(f"Provider değişti: {provider_name}")
                break
                
    def get_available_voices(self) -> List[Dict]:
        return self.current_provider.get_voices()
    
    def set_voice(self, voice_id: str):
        self.current_provider.set_voice(voice_id)
    
    def set_test_message(self, message: str):
        if message:
            self.test_message = message

    def _generate_roger_beep(self):
        """Basit bir sinüs dalgası beep sesi oluştur (1000Hz, 200ms)"""
        if os.path.exists(self.roger_beep_path):
            return
            
        import wave
        import math
        import struct
        
        sample_rate = 44100
        duration = 0.2 # saniye
        frequency = 1000.0 # Hz
        
        try:
            with wave.open(self.roger_beep_path, 'w') as obj:
                obj.setnchannels(1) # mono
                obj.setsampwidth(2) # 2 byte (16 bit)
                obj.setframerate(sample_rate)
                
                for i in range(int(duration * sample_rate)):
                    value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                    data = struct.pack('<h', value)
                    obj.writeframesraw(data)
        except Exception as e:
            print(f"Roger beep oluşturulamadı: {e}")
    
    def _speak_thread(self, message: str):
        """TTS işlemini ayrı thread'de yap"""
        with self.tts_lock:
            try:
                # 1. Ses dosyasını oluştur
                filename = f"tts_{int(time.time())}.mp3"
                filepath = os.path.join(self.temp_dir, filename)
                
                print(f"TTS Oluşturuluyor ({self.current_provider.get_name()}): {message}")
                success = self.current_provider.speak(message, filepath)
                
                if success and os.path.exists(filepath):
                    # 2. Dosyayı çal (Pygame ile)
                    # PTT zaten açık, sesi gönder
                    print(f"Ses çalınıyor: {filepath}")
                    
                    # 2.1 Roger Beep (Önce)
                    if self.roger_beep_enabled and os.path.exists(self.roger_beep_path):
                         pygame.mixer.music.load(self.roger_beep_path)
                         pygame.mixer.music.play()
                         while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                         time.sleep(0.1) # Kısa bekleme
                    
                    # 2.2 Ana Mesaj
                    pygame.mixer.music.load(filepath)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                        
                    # 3. Temizlik
                    pygame.mixer.music.unload()
                    try:
                        os.remove(filepath)
                    except:
                        pass
                else:
                    print("TTS oluşturma başarısız oldu.")
                    
            except Exception as e:
                print(f"TTS/Playback hatası: {e}")
            finally:
                pass
            
            # PTT kapat (gecikmeli)
            if self.radio_connection:
                QTimer.singleShot(200, self._finish_notification)
            else:
                self._finish_notification()
    
    def _finish_notification(self):
        """Bildirimi sonlandır"""
        if self.radio_connection:
            self.radio_connection.ptt_off()
            
        if self.vox_controller:
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
