"""
VOX (Voice Operated Switch) Kontrolcüsü
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .audio_manager import AudioManager
from .connection import RadioConnection


class VOXController(QObject):
    """VOX kontrol sınıfı - Ses tetiklemeli PTT"""
    
    # Sinyaller
    vox_triggered = pyqtSignal()
    vox_released = pyqtSignal()
    
    def __init__(self, audio_manager: AudioManager, radio_connection: RadioConnection):
        super().__init__()
        self.audio_manager = audio_manager
        self.radio_connection = radio_connection
        
        self.vox_enabled = False
        self.is_transmitting = False
        self.hold_time = 500  # VOX serbest bırakma gecikmesi (ms)
        
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
        if self.vox_enabled:
            self.vox_enabled = False
            if self.is_transmitting:
                self._release_ptt()
    
    def set_hold_time(self, milliseconds: int) -> None:
        """
        VOX serbest bırakma gecikmesini ayarla
        
        Args:
            milliseconds: Milisaniye cinsinden gecikme süresi
        """
        self.hold_time = max(100, min(5000, milliseconds))
    
    def _on_threshold_exceeded(self) -> None:
        """Eşik değeri aşıldığında PTT'yi aktif et"""
        if not self.vox_enabled:
            return
        
        # PTT zaten aktifse timer'ı sıfırla
        if self.is_transmitting:
            self.release_timer.stop()
            self.release_timer.start(self.hold_time)
            return
        
        # PTT'yi aktif et
        if self.radio_connection.ptt_on():
            self.is_transmitting = True
            self.vox_triggered.emit()
            self.release_timer.start(self.hold_time)
    
    def _release_ptt(self) -> None:
        """PTT'yi serbest bırak"""
        if self.is_transmitting:
            self.radio_connection.ptt_off()
            self.is_transmitting = False
            self.vox_released.emit()
    
    def manual_ptt(self, active: bool) -> None:
        """
        Manuel PTT kontrolü
        
        Args:
            active: True ise PTT aktif, False ise pasif
        """
        if active:
            if self.radio_connection.ptt_on():
                self.is_transmitting = True
                self.vox_triggered.emit()
        else:
            self._release_ptt()
