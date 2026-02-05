from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import psutil

class BatteryService(QObject):
    """Batarya durumu izleme servisi"""
    battery_updated = pyqtSignal(int, bool)  # percent, plugged
    warning_threshold_reached = pyqtSignal(str) # warning_message

    def __init__(self):
        super().__init__()
        self.last_percent = -1
        self.warning_levels = {30: False, 20: False} # Uyarı yapıldı mı flagleri
        self.monitor_enabled = True
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_battery)
        # 10 saniyede bir kontrol et (yormamak için)
        self.timer.start(10000)
        
        # İlk kontrol
        self.check_battery()

    def check_battery(self):
        """Batarya durumunu kontrol et"""
        if not self.monitor_enabled:
            return

        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                # Masaüstü veya batarya yok
                # Yine de sinyali -1 olarak gönderelim ki UI bilsin
                self.battery_updated.emit(100, True) # Varsayılan %100 ve fişe takılı gibi davran
                return

            percent = int(battery.percent)
            plugged = battery.power_plugged
            
            self.battery_updated.emit(percent, plugged)
            
            # Uyarı mantığı (Sadece fişe takılı DEĞİLSE)
            if not plugged:
                self._check_warnings(percent)
            else:
                # Şarja takılınca uyarı flaglerini sıfırla ki tekrar düşerse yine uyarsın
                self.warning_levels = {k: False for k in self.warning_levels}
            
            self.last_percent = percent
            
        except Exception as e:
            print(f"Batarya kontrol hatası: {e}")

    def _check_warnings(self, percent):
        """Kritik seviye kontrolü"""
        # 30% uyarısı
        if percent <= 30 and percent > 20:
             if not self.warning_levels[30]:
                self.warning_threshold_reached.emit(f"Dikkat, batarya seviyesi yüzde {percent}. Şarj gerekli.")
                self.warning_levels[30] = True
        
        # 20% uyarısı
        elif percent <= 20:
             if not self.warning_levels[20]:
                self.warning_threshold_reached.emit(f"Acil durum! Batarya seviyesi yüzde {percent}. Sistem kapanabilir.")
                self.warning_levels[20] = True
