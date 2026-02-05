"""
Deprem bildirim servisi - Kandilli Rasathanesi API
"""
import requests
from typing import Optional, List, Dict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime, timedelta

class EarthquakeService(QObject):
    """Deprem bildirim servisi"""
    
    # Sinyaller
    earthquake_detected = pyqtSignal(dict)  # Yeni kritik deprem (Bildirim için)
    data_updated = pyqtSignal(list)         # Liste güncellendi (UI için)
    error_occurred = pyqtSignal(str)        # Hata oluştu
    
    def __init__(self, min_magnitude: float = 4.0):
        super().__init__()
        # Kandilli Rasathanesi API
        self.api_url = "http://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        self.min_magnitude = min_magnitude
        self.city_filter: Optional[str] = None
        
        self.check_interval = 60  # Kontrol aralığı (saniye)
        self.last_check_time: Optional[datetime] = None
        self.known_earthquakes: List[str] = []  # Bilinen deprem ID'leri
        self.last_data: List[Dict] = []         # Son çekilen ham veri
        
        # Otomatik kontrol timer'ı
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_earthquakes)
    
    def set_min_magnitude(self, magnitude: float) -> None:
        """Minimum deprem büyüklüğünü ayarla (Bildirim için)"""
        self.min_magnitude = max(0.0, magnitude)
        
    def set_city_filter(self, city: str) -> None:
        """Şehir filtresi ayarla (Opsiyonel)"""
        self.city_filter = city.lower().strip() if city else None
    
    def start_monitoring(self) -> None:
        """Deprem monitörünü başlat"""
        if not self.check_timer.isActive():
            self.check_earthquakes()  # İlk kontrol
            self.check_timer.start(self.check_interval * 1000)
    
    def stop_monitoring(self) -> None:
        """Deprem monitörünü durdur"""
        self.check_timer.stop()
        
    def check_earthquakes(self) -> None:
        """Yeni depremleri kontrol et (Otomatik/Manuel)"""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('result'):
                return
            
            earthquakes = data['result']
            self.last_data = earthquakes # Veriyi sakla
            
            # Filtrelenmiş listeyi UI için hazırla ve gönder
            display_list = []
            for eq in earthquakes[:100]: # Son 100 deprem
                if self._passes_basic_filter(eq):
                     display_list.append(self._parse_earthquake(eq))
            
            self.data_updated.emit(display_list)
            
            # Yeni deprem kontrolü (Sadece bildirim için)
            self._process_new_events(earthquakes)
            
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Deprem verisi alınamadı: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Beklenmeyen hata: {str(e)}")

    def _passes_basic_filter(self, eq: Dict) -> bool:
        """UI listesi için temel filtre"""
        # 1. Şehir Filtresi
        if self.city_filter:
            location = eq.get('title', '').lower()
            filters = [f.strip().lower() for f in self.city_filter.split(',')]
            if not any(f in location for f in filters):
                return False
        
        # Büyüklük filtresi kaldırıldı: Listede tüm depremler görünsün (Kullanıcı isteği)
        return True

    def _process_new_events(self, earthquakes: List[Dict]):
        """Yeni ve kritik depremleri tespit et (Bildirim Mantığı)"""
        if self.last_check_time is None:
            self.last_check_time = datetime.now()
            for eq in earthquakes[:50]:
                self.known_earthquakes.append(self._generate_id(eq))
            return

        for eq in earthquakes:
            # Bildirim için daha sıkı filtreler
            
            # 1. Şehir ve Temel Filtre
            if not self._passes_basic_filter(eq):
                continue

            # 2. Bildirim Limiti (Min Magnitude)
            mag = float(eq.get('mag', 0))
            if mag < self.min_magnitude:
                continue
                
            # 3. Zaman Kontrolü (Son 15 dakika)
            try:
                eq_date_str = eq.get('date')
                eq_date = datetime.strptime(eq_date_str, "%Y.%m.%d %H:%M:%S")
                if datetime.now() - eq_date > timedelta(minutes=15):
                    continue
            except:
                pass 

            # 4. Yeni mi?
            eq_id = self._generate_id(eq)
            if eq_id not in self.known_earthquakes:
                self.known_earthquakes.append(eq_id)
                self.earthquake_detected.emit(self._parse_earthquake(eq))
        
        # Temizlik
        if len(self.known_earthquakes) > 200:
            self.known_earthquakes = self.known_earthquakes[-100:]
            
        self.last_check_time = datetime.now()

    def _parse_earthquake(self, eq: Dict) -> Dict:
        """API verisini standart formata çevir"""
        return {
            'magnitude': float(eq.get('mag', 0)),
            'location': eq.get('title', 'Bilinmiyor'),
            'depth': eq.get('depth', 0),
            'date': eq.get('date', ''),
            'lat': eq.get('geojson', {}).get('coordinates', [0, 0])[1],
            'lon': eq.get('geojson', {}).get('coordinates', [0, 0])[0]
        }

    def _generate_id(self, eq: Dict) -> str:
        return f"{eq.get('date')}_{eq.get('mag')}_{eq.get('title')}"

    def get_announcement_text(self, eq: Dict) -> str:
        return (
            f"Deprem uyarısı! Deprem uyarısı! {eq['location']} bölgesinde "
            f"{eq['magnitude']} büyüklüğünde deprem oldu. "
            f"Derinlik {eq['depth']} kilometre."
        )
