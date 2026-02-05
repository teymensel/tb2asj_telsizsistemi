"""
Hava durumu servisi - OpenWeatherMap API entegrasyonu
"""
import requests
from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime


class WeatherService(QObject):
    """Hava durumu servisi"""
    
    # Sinyaller
    weather_updated = pyqtSignal(dict)  # Hava durumu güncellendi
    error_occurred = pyqtSignal(str)  # Hata oluştu
    
    def __init__(self, api_key: str = "", city: str = "Istanbul", country: str = "TR"):
        super().__init__()
        self.api_key = api_key
        self.city = city
        self.country = country
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        self.last_weather_data: Optional[Dict] = None
        self.update_interval = 3600  # 1 saat (saniye)
        
        # Otomatik güncelleme timer'ı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_weather)
    
    def set_api_key(self, api_key: str) -> None:
        """API anahtarını ayarla"""
        self.api_key = api_key
    
    def set_location(self, city: str, country: str = "TR") -> None:
        """Konum ayarla"""
        self.city = city
        self.country = country
    
    def set_update_interval(self, seconds: int) -> None:
        """Güncelleme aralığını ayarla"""
        self.update_interval = max(300, seconds)  # Minimum 5 dakika
    
    def start_auto_update(self) -> None:
        """Otomatik güncellemeyi başlat"""
        if not self.update_timer.isActive():
            self.fetch_weather()  # İlk güncelleme
            self.update_timer.start(self.update_interval * 1000)  # ms'ye çevir
    
    def stop_auto_update(self) -> None:
        """Otomatik güncellemeyi durdur"""
        self.update_timer.stop()
    
    def fetch_weather_manual(self):
        """Manuel hava durumu güncelleme"""
        return self.fetch_weather()

    def fetch_weather(self) -> Optional[Dict]:
        """
        Hava durumunu getir
        
        Returns:
            Hava durumu verisi veya None
        """
        if not self.api_key:
            self.error_occurred.emit("API anahtarı eksik. Ayarlardan ekleyin.")
            return None
        
    def fetch_weather(self) -> Optional[Dict]:
        """
        Hava durumunu getir (Otomatik: 2.5/weather veya 3.0/onecall dener)
        """
        if not self.api_key:
            self.error_occurred.emit("API anahtarı eksik. Ayarlardan ekleyin.")
            return None
        
        # 1. Yöntem: Standart 2.5/weather API (Şehir ismiyle)
        try:
            params = {
                'q': f"{self.city},{self.country}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_weather_data(data)
            
            elif response.status_code == 401:
                # 401 Hatası: Belki One Call API 3.0 anahtarıdır?
                # One Call API şehir ismi desteklemez, önce koordinat bulmalıyız.
                print("2.5/weather 401 döndü, One Call 3.0 deneniyor...")
                return self._fetch_weather_onecall()
                
            else:
                response.raise_for_status()
                
        except Exception as e:
            print(f"Standart API hatası: {e}")
            # Hata durumunda da One Call denenebilir
            return self._fetch_weather_onecall()

        return None

    def _fetch_weather_onecall(self) -> Optional[Dict]:
        """One Call API 3.0 ile hava durumu getir (Geocoding -> OneCall)"""
        try:
            # 1. Geocoding: Şehirden koordinat bul
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': f"{self.city},{self.country}",
                'limit': 1,
                'appid': self.api_key
            }
            
            geo_res = requests.get(geo_url, params=geo_params, timeout=10)
            
            if geo_res.status_code == 401:
                self.error_occurred.emit("API Hatası (401): Anahtar geçersiz veya henüz aktif değil.")
                return None
                
            if geo_res.status_code != 200 or not geo_res.json():
                self.error_occurred.emit(f"Konum bulunamadı: {self.city}")
                return None
                
            location = geo_res.json()[0]
            lat, lon = location['lat'], location['lon']
            
            # 2. One Call API 3.0
            onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
            onecall_params = {
                'lat': lat,
                'lon': lon,
                'exclude': 'minutely,hourly,daily,alerts', # Sadece current yeterli
                'units': 'metric',
                'lang': 'tr',
                'appid': self.api_key
            }
            
            oc_res = requests.get(onecall_url, params=onecall_params, timeout=10)
            oc_res.raise_for_status()
            
            data = oc_res.json()
            
            # Veriyi işle (One Call formatı biraz farklıdır)
            current = data['current']
            weather_info = {
                'city': self.city, # OneCall şehir ismi dönmez, elimizdekini kullanırız
                'temperature': round(current['temp'], 1),
                'feels_like': round(current['feels_like'], 1),
                'humidity': current['humidity'],
                'pressure': current['pressure'],
                'description': current['weather'][0]['description'],
                'wind_speed': round(current['wind_speed'], 1),
                'timestamp': datetime.now().isoformat()
            }
            
            self.last_weather_data = weather_info
            self.weather_updated.emit(weather_info)
            return weather_info
            
        except Exception as e:
            error_msg = f"Hava durumu alınamadı (OneCall): {str(e)}"
            self.error_occurred.emit(error_msg)
            return None

    def _process_weather_data(self, data):
        """Standard API verisini işle"""
        weather_info = {
            'city': data['name'],
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'wind_speed': round(data['wind']['speed'], 1),
            'timestamp': datetime.now().isoformat()
        }
        self.last_weather_data = weather_info
        self.weather_updated.emit(weather_info)
        return weather_info
    
    def get_announcement_text(self) -> str:
        """
        Telsiz duyurusu için metin oluştur
        
        Returns:
            Duyuru metni
        """
        if not self.last_weather_data:
            return "Hava durumu bilgisi mevcut değil"
        
        data = self.last_weather_data
        text = (
            f"{data['city']} için hava durumu bilgisi. "
            f"Sıcaklık {data['temperature']} derece. "
            f"Hissedilen {data['feels_like']} derece. "
            f"Nem yüzde {data['humidity']}. "
            f"{data['description']}. "
            f"Rüzgar hızı saatte {data['wind_speed']} kilometre."
        )
        return text
    
    def get_last_data(self) -> Optional[Dict]:
        """Son hava durumu verisini al"""
        return self.last_weather_data
