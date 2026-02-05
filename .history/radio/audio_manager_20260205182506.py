"""
Ses yöneticisi - Mikrofon ve hoparlör kontrolü
"""
import sounddevice as sd
import numpy as np
from typing import Optional, List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class AudioManager(QObject):
    """Ses yönetimi sınıfı"""
    
    # Sinyaller
    level_changed = pyqtSignal(float)  # Ses seviyesi değişti (0-100)
    threshold_exceeded = pyqtSignal()  # Eşik değeri aşıldı
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.input_device = None
        self.output_device = None
        self.sample_rate = 44100
        self.block_size = 1024
        self.stream = None
        
        # Seviye ayarları
        self.mic_level = 50  # 0-100
        self.speaker_level = 75  # 0-100
        self.vox_threshold = 30  # 0-100
        
        # Seviye monitörü için timer
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self._check_level)
        self.current_level = 0.0
    
    @staticmethod
    def get_audio_devices() -> Tuple[List[dict], List[dict]]:
        """
        Mevcut ses cihazlarını listele
        
        Returns:
            (giriş cihazları, çıkış cihazları) tuple'ı
        """
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            device_info = {
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'] if device['max_input_channels'] > 0 
                           else device['max_output_channels']
            }
            
            if device['max_input_channels'] > 0:
                input_devices.append(device_info)
            if device['max_output_channels'] > 0:
                output_devices.append(device_info)
        
        return input_devices, output_devices
    
    def set_input_device(self, device_id: Optional[int]) -> None:
        """Giriş cihazını ayarla"""
        self.input_device = device_id
    
    def set_output_device(self, device_id: Optional[int]) -> None:
        """Çıkış cihazını ayarla"""
        self.output_device = device_id
    
    def set_mic_level(self, level: int) -> None:
        """Mikrofon seviyesini ayarla (0-100)"""
        self.mic_level = max(0, min(100, level))
    
    def set_speaker_level(self, level: int) -> None:
        """Hoparlör seviyesini ayarla (0-100)"""
        self.speaker_level = max(0, min(100, level))
    
    def set_vox_threshold(self, threshold: int) -> None:
        """VOX eşik değerini ayarla (0-100)"""
        self.vox_threshold = max(0, min(100, threshold))
    
    def start_monitoring(self) -> bool:
        """Ses monitörünü başlat"""
        try:
            def audio_callback(indata, frames, time, status):
                """Ses akışı callback fonksiyonu"""
                if status:
                    print(f"Ses akış hatası: {status}")
                
                # RMS (Root Mean Square) ile ses seviyesini hesapla
                volume_norm = np.linalg.norm(indata) * 10
                # 0-100 arasına normalize et
                volume_percent = min(100, volume_norm)
                self.current_level = volume_percent
            
            self.stream = sd.InputStream(
                device=self.input_device,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=audio_callback
            )
            
            self.stream.start()
            self.is_monitoring = True
            self.level_timer.start(100)  # Her 100ms'de seviye kontrolü
            return True
            
        except Exception as e:
            print(f"Ses monitörü başlatılamadı: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Ses monitörünü durdur"""
        self.level_timer.stop()
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_monitoring = False
    
    def _check_level(self) -> None:
        """Ses seviyesini kontrol et ve sinyal gönder"""
        # Mikrofon seviyesi ile çarp
        adjusted_level = (self.current_level * self.mic_level) / 100
        
        self.level_changed.emit(adjusted_level)
        
        # VOX eşik kontrolü
        if adjusted_level > self.vox_threshold:
            self.threshold_exceeded.emit()
    
    def get_current_level(self) -> float:
        """Güncel ses seviyesini al (0-100)"""
        return self.current_level
    
    def play_tone(self, frequency: float = 1000.0, duration: float = 0.5) -> None:
        """
        Test tonu çal
        
        Args:
            frequency: Frekans (Hz)
            duration: Süre (saniye)
        """
        try:
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Hoparlör seviyesi ile ayarla
            tone = tone * (self.speaker_level / 100)
            
            sd.play(tone, sample_rate, device=self.output_device)
            sd.wait()
        except Exception as e:
            print(f"Ton çalınamadı: {e}")
