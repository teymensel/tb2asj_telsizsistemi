"""
VOX (Voice Operated Switch) Kontrolcüsü
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .audio_manager import AudioManager
from .connection import RadioConnection


class VOXController(QObject):
    """VOX kontrol sınıfı - Ses tetiklemeli PTT ve Loopback"""
    
    # Sinyaller
    vox_triggered = pyqtSignal()
    vox_released = pyqtSignal()
    
    def __init__(self, audio_manager: AudioManager, radio_connection: RadioConnection):
        super().__init__()
        self.audio_manager = audio_manager
        self.radio_connection = radio_connection
        
        self.vox_enabled = False
        self.is_transmitting = False
        self.hold_time = 1000  # Gecikme süresi (ms)
        
        # Gecikme timer'ı
        self.release_timer = QTimer()
        self.release_timer.setSingleShot(True)
        self.release_timer.timeout.connect(self._release_ptt)
        
        # Ses seviyesi bağlantısı
        self.audio_manager.threshold_exceeded.connect(self._on_threshold_exceeded)
    
    def enable_vox(self) -> None:
        """VOX'u etkinleştir"""
        if not self.vox_enabled:
            self.vox_enabled = True
            if not self.audio_manager.is_monitoring:
                self.audio_manager.start_monitoring()
    
    def disable_vox(self) -> None:
        """VOX'u devre dışı bırak"""
        self.vox_enabled = False
        self._release_ptt()
    
    def set_hold_time(self, milliseconds: int) -> None:
        self.hold_time = max(100, min(5000, milliseconds))
    
    def _on_threshold_exceeded(self) -> None:
        """Eşik değeri aşıldığında PTT ve Loopback aktif et"""
        if not self.vox_enabled:
            return
            
        # Zaten iletişimdeysek süreyi uzat
        if self.is_transmitting:
            self.release_timer.stop()
            self.release_timer.start(self.hold_time)
            return
            
        # İletişimi başlat
        self._start_transmission()
        self.release_timer.start(self.hold_time)
    
    def _start_transmission(self):
        """İletimi başlat (PTT + Loopback)"""
        self.is_transmitting = True
        
        # 1. COM Port PTT (varsa)
        self.radio_connection.ptt_on()
        
        # 2. Audio Loopback (Sesi çıkışa ver)
        self.audio_manager.set_loopback(True)
        
        self.vox_triggered.emit()
    
    def _release_ptt(self) -> None:
        """İletimi durdur"""
        if self.is_transmitting:
            # 1. COM Port PTT kapa
            self.radio_connection.ptt_off()
            
            # 2. Audio Loopback kapa
            self.audio_manager.set_loopback(False)
            
            self.is_transmitting = False
            self.vox_released.emit()
    
    def manual_ptt(self, active: bool) -> None:
        """Manuel PTT kontrolü"""
        if active:
            # Timer'ı durdur (elle basılı tutuluyor)
            self.release_timer.stop()
            if not self.is_transmitting:
                self._start_transmission()
        else:
            # Elle bırakıldı, VOX devrede değilse kapat
            # Eğer VOX açıksa ve ses varsa timer başlatılabilir ama
            # manuel mod genellikle önceliklidir. Direkt kesiyoruz.
            self._release_ptt()
