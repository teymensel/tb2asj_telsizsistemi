"""
Deprem bildirim servisi - AFAD ve Kandilli Rasathanesi API
"""
import requests
from typing import Optional, List, Dict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime, timedelta


class EarthquakeService(QObject):
    """Deprem bildirim servisi"""
    
    # Sinyaller
    earthquake_detected = pyqtSignal(dict)  # Yeni deprem tespit edildi
    error_occurred = pyqtSignal(str)  # Hata oluştu
    
    def __init__(self, min_magnitude: float = 4.0):
        super().__init__()
        # Kandilli Rasathanesi API (AFAD API istikrarsız olduğu için alternatif)
        self.api_url = "http://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        self.min_magnitude = min_magnitude
        
        self.check_interval = 60  # Kontrol aralığı (saniye)
        self.last_check_time: Optional[datetime] = None
        self.known_earthquakes: List[str] = []  # Bilinen deprem ID'leri
        
        # Otomatik kontrol timer'ı
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_earthquakes)
    
    def set_min_magnitude(self, magnitude: float) -> None:
        """Minimum deprem büyüklüğünü ayarla"""
        self.min_magnitude = max(0.0, magnitude)
    
    def set_check_interval(self, seconds: int) -> None:
        """Kontrol aralığını ayarla"""
        self.check_interval = max(30, seconds)  # Minimum 30 saniye
    
    def start_monitoring(self) -> None:
        """Deprem monitörünü başlat"""
        if not self.check_timer.isActive():
            self.check_earthquakes()  # İlk kontrol
            self.check_timer.start(self.check_interval * 1000)  # ms'ye çevir
    
    def stop_monitoring(self) -> None:
        """Deprem monitörünü durdur"""
        self.check_timer.stop()
    
    def check_earthquakes(self) -> None:
        """Yeni depremleri kontrol et"""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('result'):
                return
            
            earthquakes = data['result']
            current_time = datetime.now()
            
            # İlk çalıştırmada sadece listeyi doldur
            if self.last_check_time is None:
                self.last_check_time = current_time
                for eq in earthquakes[:10]:  # Son 10 depremi sakla
                    eq_id = self._generate_earthquake_id(eq)
                    self.known_earthquakes.append(eq_id)
                return
            
            # Yeni depremleri kontrol et
            for eq in earthquakes:
                magnitude = float(eq.get('mag', 0))
                
                # Minimum büyüklük kontrolü
                if magnitude < self.min_magnitude:
                    continue
                
                eq_id = self._generate_earthquake_id(eq)
                
                # Yeni deprem mi?
                if eq_id not in self.known_earthquakes:
                    earthquake_info = {
                        'magnitude': magnitude,
                        'location': eq.get('title', 'Bilinmiyor'),
                        'depth': eq.get('depth', 0),
                        'date': eq.get('date', ''),
                        'lat': eq.get('geojson', {}).get('coordinates', [0, 0])[1],
                        'lon': eq.get('geojson', {}).get('coordinates', [0, 0])[0]
                    }
                    
                    self.known_earthquakes.append(eq_id)
                    self.earthquake_detected.emit(earthquake_info)
            
            # Eski depremleri temizle (son 100 deprem)
            if len(self.known_earthquakes) > 100:
                self.known_earthquakes = self.known_earthquakes[-100:]
            
            self.last_check_time = current_time
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Deprem verisi alınamadı: {str(e)}"
            self.error_occurred.emit(error_msg)
        except Exception as e:
            error_msg = f"Beklenmeyen hata: {str(e)}"
            self.error_occurred.emit(error_msg)
    
    def _generate_earthquake_id(self, earthquake: Dict) -> str:
        """
        Deprem için benzersiz ID oluştur
        
        Args:
            earthquake: Deprem verisi
        
        Returns:
            Benzersiz ID
        """
        date = earthquake.get('date', '')
        mag = earthquake.get('mag', '')
        location = earthquake.get('title', '')
        return f"{date}_{mag}_{location}"
    
    def get_announcement_text(self, earthquake: Dict) -> str:
        """
        Deprem duyurusu için metin oluştur
        
        Args:
            earthquake: Deprem bilgisi
        
        Returns:
            Duyuru metni
        """
        text = (
            f"Deprem bildirimi! "
            f"{earthquake['location']} bölgesinde "
            f"büyüklüğü {earthquake['magnitude']} olan bir deprem meydana geldi. "
            f"Derinlik {earthquake['depth']} kilometre. "
            f"Tarih: {earthquake['date']}"
        )
        return text
