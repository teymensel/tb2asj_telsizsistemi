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
        
        try:
            params = {
                'q': f"{self.city},{self.country}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                self.error_occurred.emit("API Hatası (401): API anahtarı geçersiz veya yetkisiz.")
                return None
                
            response.raise_for_status()
            
            data = response.json()
            
            # Veriyi işle
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
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Hava durumu alınamadı: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None
        except Exception as e:
            error_msg = f"Beklenmeyen hata: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None
    
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
