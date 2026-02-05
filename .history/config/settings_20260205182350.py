"""
Ayarlar yöneticisi - Uygulama konfigürasyonunu yönetir
"""
import json
import os
from pathlib import Path
from typing import Any, Dict


class Settings:
    """Uygulama ayarları sınıfı"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.settings_file = self.config_dir / "settings.json"
        self.default_file = self.config_dir / "settings_default.json"
        self.settings: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Ayarları yükle"""
        # Varsayılan ayarları yükle
        with open(self.default_file, 'r', encoding='utf-8') as f:
            self.settings = json.load(f)
        
        # Kullanıcı ayarları varsa üzerine yaz
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    self._merge_settings(self.settings, user_settings)
            except Exception as e:
                print(f"Ayarlar yüklenirken hata: {e}")
    
    def save(self) -> None:
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Ayar değerini al
        
        Args:
            key: Nokta ile ayrılmış ayar anahtarı (örn: "radio.port")
            default: Varsayılan değer
        
        Returns:
            Ayar değeri
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Ayar değerini güncelle
        
        Args:
            key: Nokta ile ayrılmış ayar anahtarı (örn: "radio.port")
            value: Yeni değer
        """
        keys = key.split('.')
        target = self.settings
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        self.save()
    
    def _merge_settings(self, base: Dict, updates: Dict) -> None:
        """İki ayar sözlüğünü birleştir"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_settings(base[key], value)
            else:
                base[key] = value


# Global settings instance
settings = Settings()
