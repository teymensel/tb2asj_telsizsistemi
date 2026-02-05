"""
Ses yöneticisi - Mikrofon ve hoparlör kontrolü (Loopback destekli)
"""
import sounddevice as sd
import numpy as np
from typing import Optional, List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import queue # EKLENDİ


class AudioManager(QObject):
    """Ses yönetimi sınıfı - Full Duplex"""
    
    # Sinyaller
    level_changed = pyqtSignal(float)
    threshold_exceeded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.input_device = None
        self.output_device = None
        self.sample_rate = 44100
        # Blocksize artırıldı ve sabitlendi (performans için)
        self.block_size = 2048 
        self.stream = None
        self.stream_in = None  # AYRI STREAM
        self.stream_out = None # AYRI STREAM
        
        # Seviye ayarları
        self.mic_level = 50  # 0-100 (Giriş kazancı)
        self.speaker_level = 75  # 0-100 (Çıkış kazancı)
        self.vox_threshold = 30
        
        # Loopback kontrolü (Sesi dışarı verme)
        self.loopback_active = False  # PTT basılı mı veya VOX aktif mi?
        
        # Seviye ölçümü için
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self._check_level)
        self.current_level = 0.0
    
    @staticmethod
    def get_audio_devices() -> Tuple[List[dict], List[dict]]:
        """Mevcut ses cihazlarını listele"""
        try:
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
        except Exception as e:
            print(f"Cihaz listeleme hatası: {e}")
            return [], []
    
    def set_input_device(self, device_id: Optional[int]) -> None:
        self.input_device = device_id
        if self.is_monitoring:
            self.restart_monitoring()
    
    def set_output_device(self, device_id: Optional[int]) -> None:
        self.output_device = device_id
        if self.is_monitoring:
            self.restart_monitoring()
    
    def set_mic_level(self, level: int) -> None:
        self.mic_level = max(0, min(100, level))
        # Canlı gain güncellemesi yapılabilir ama şimdilik callback içinde okuyoruz
    
    def set_speaker_level(self, level: int) -> None:
        self.speaker_level = max(0, min(100, level))
    
    def set_vox_threshold(self, threshold: int) -> None:
        self.vox_threshold = max(0, min(100, threshold))
        
    def set_loopback(self, active: bool) -> None:
        """Sesi dışarı vermeyi (loopback) aç/kapat"""
        # print(f"Loopback durumu değiştiriliyor: {active}")
        self.loopback_active = active
    
    def restart_monitoring(self):
        """Monitörü yeniden başlat"""
        self.stop_monitoring()
        self.start_monitoring()

    def start_monitoring(self) -> bool:
        """Ses akışını başlat (Hem giriş hem çıkış)"""
        try:
            def audio_callback(indata, outdata, frames, time, status):
                if status:
                    # Overflow/Underflow hatalarını konsola basıp geçiyoruz, kritik değil
                    # print(f"Ses durumu: {status}") 
                    pass
                
                # 1. Seviye analizi (Input)
                # RMS hesapla (Basit ortalama, NumPy ile hızlı)
                if len(indata) > 0:
                    volume_norm = float(np.linalg.norm(indata) * 10)
                    self.current_level = min(100, volume_norm)
                
                # 2. Loopback (Pass-through)
                if self.loopback_active:
                    # Giriş sesini al, kazanç uygula
                    # Sıfıra bölme hatası olmasın
                    # Kullanıcı yüksek ses istiyor: Gain factor artırıldı.
                    # 50 seviyesi = 2.0x gain, 100 seviyesi = 5.0x gain
                    mic_gain = (self.mic_level / 50.0) * 2.0 if self.mic_level > 0 else 0
                    speaker_gain = (self.speaker_level / 50.0) * 1.5 if self.speaker_level > 0 else 0
                    
                    # Sesi işle ve çıkışa gönder
                    # outdata[:] = indata * mic_gain * speaker_gain
                    # Clipping önleme (basit)
                    processed_audio = indata * mic_gain * speaker_gain
                    np.clip(processed_audio, -1.0, 1.0, out=outdata)
                else:
                    # Sessizlik (Mute) - Çıkışa 0 yaz
                    outdata.fill(0)
            
            # Full Duplex Stream (Giriş ve Çıkış)
            # Latency 'high' yaparak buffer underrun'ları önlüyoruz
            self.stream = sd.Stream(
                device=(self.input_device, self.output_device),
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                latency='high', # Hata toleransı için yüksek gecikme
                callback=audio_callback
            )
            
            self.stream.start()
            self.is_monitoring = True
            self.level_timer.start(100)
            return True
            
        except Exception as e:
            print(f"Ses monitörü başlatılamadı: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Ses akışını durdur"""
        self.level_timer.stop()
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.is_monitoring = False
    
    def _check_level(self) -> None:
        """Timer ile periyodik seviye kontrolü"""
        # Sinyal gönder
        self.level_changed.emit(self.current_level)
        
        # VOX eşiği kontrolü
        # Loopback açıkken (PTT basılıyken) VOX tetiklemeye gerek yok
        if not self.loopback_active and self.current_level > (self.vox_threshold * 1.2): 
             self.threshold_exceeded.emit()

    def play_tone(self, frequency: float = 1000.0, duration: float = 0.5) -> None:
        """Test tonu çal"""
        pass # Stream açıkken sd.play çakışıyor, iptal edildi.
