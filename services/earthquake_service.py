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
        # Kandilli Rasathanesi API Endpoints
        self.providers = {
            "Kandilli": "https://api.orhanaydogdu.com.tr/deprem/kandilli/live",
            "AFAD": "https://api.orhanaydogdu.com.tr/deprem/afad/live",
            "Tümü (Kandilli+AFAD)": "https://api.orhanaydogdu.com.tr/deprem"
        }
        self.current_provider = "Kandilli"
        self.api_url = self.providers[self.current_provider]
        
        self.min_magnitude = min_magnitude
        self.city_filter: Optional[str] = None
        
        self.check_interval = 60  # Kontrol aralığı (saniye)
        self.last_check_time: Optional[datetime] = None
        self.known_earthquakes: List[str] = []  # Bilinen deprem ID'leri
        self.last_data: List[Dict] = []         # Son çekilen ham veri
        
        # Otomatik kontrol timer'ı
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_earthquakes)
    
    def set_provider(self, provider_name: str) -> None:
        """Veri sağlayıcıyı değiştir"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            self.api_url = self.providers[provider_name]
            # Değişiklik sonrası hemen kontrol et
            QTimer.singleShot(100, self.check_earthquakes)

    def set_min_magnitude(self, magnitude: float) -> None:
        """Minimum deprem büyüklüğünü ayarla (Bildirim için)"""
        self.min_magnitude = max(0.0, magnitude)
        
    def set_city_filter(self, city: str) -> None:
        """Şehir filtresi ayarla (Opsiyonel)"""
        self.city_filter = city.lower().strip() if city else None
    
    def set_min_magnitude(self, magnitude: float) -> None:
        """Minimum deprem büyüklüğünü ayarla (Bildirim için)"""
        self.min_magnitude = max(0.0, magnitude)
        
    def set_check_interval(self, seconds: int) -> None:
        """Sorgulama aralığını saniye cinsinden ayarla"""
        self.check_interval = max(10, seconds)  # Minimum 10 saniye
        if self.check_timer.isActive():
            self.check_timer.start(self.check_interval * 1000)
            
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
        print(f"[DEBUG] Deprem kontrolü başlatıldı... URL: {self.api_url}")
        try:
            response = requests.get(self.api_url, timeout=10)
            print(f"[DEBUG] API Yanıt Kodu: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            if not data.get('result'):
                print("[DEBUG] API yanıtında 'result' boş veya yok!")
                return
            
            earthquakes = data['result']
            print(f"[DEBUG] Çekilen ham deprem sayısı: {len(earthquakes)}")
            if len(earthquakes) > 0:
                print(f"[DEBUG] İlk deprem örneği: {earthquakes[0]}")
            
            self.last_data = earthquakes # Veriyi sakla
            
            # Filtrelenmiş listeyi UI için hazırla ve gönder
            display_list = []
            for eq in earthquakes[:100]: # Son 100 deprem
                if self._passes_basic_filter(eq):
                     display_list.append(self._parse_earthquake(eq))
            
            print(f"[DEBUG] UI listesi için filtrelenen deprem sayısı: {len(display_list)}")
            self.data_updated.emit(display_list)
            
            # Yeni deprem kontrolü (Sadece bildirim için)
            self._process_new_events(earthquakes)
            
        except requests.exceptions.RequestException as e:
            print(f"[HATA] İstek hatası: {e}")
            self.error_occurred.emit(f"Deprem verisi alınamadı: {str(e)}")
        except Exception as e:
            print(f"[HATA] Beklenmeyen hata: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Beklenmeyen hata: {str(e)}")

    def _passes_basic_filter(self, eq: Dict) -> bool:
        """UI listesi için temel filtre"""
        # 1. Şehir Filtresi
        if self.city_filter:
            # print(f"[DEBUG] Şehir filtresi aktif: {self.city_filter}")
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
                eq_date_str = eq.get('date_time') or eq.get('date')
                # Tarih formatını düzelt (API tire veya nokta kullanabiliyor)
                eq_date_str = eq_date_str.replace('.', '-')
                eq_date = datetime.strptime(eq_date_str, "%Y-%m-%d %H:%M:%S")
                
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
            'date': eq.get('date_time') or eq.get('date', ''),
            'lat': eq.get('geojson', {}).get('coordinates', [0, 0])[1],
            'lon': eq.get('geojson', {}).get('coordinates', [0, 0])[0]
        }

    def _generate_id(self, eq: Dict) -> str:
        date_str = eq.get('date_time') or eq.get('date')
        return f"{date_str}_{eq.get('mag')}_{eq.get('title')}"

    def get_announcement_text(self, eq: Dict) -> str:
        return (
            f"Deprem uyarısı! Deprem uyarısı! {eq['location']} bölgesinde "
            f"{eq['magnitude']} büyüklüğünde deprem oldu. "
            f"Derinlik {eq['depth']} kilometre."
        )
