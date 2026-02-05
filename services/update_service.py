import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import os

class UpdateChecker(QThread):
    """Arka planda güncelleme kontrolü yapan thread"""
    update_available = pyqtSignal(dict)  # {version, url, notes}
    error = pyqtSignal(str)

    def __init__(self, current_version, repo_url):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url # "teymensel/tb2asj_telsizsistemi"

    def run(self):
        print(f"[GÜNCELLEME] Kontrol ediliyor: {self.repo_url} (Mevcut: {self.current_version})")
        try:
            # GitHub API'den son release bilgisini al
            api_url = f"https://api.github.com/repos/{self.repo_url}/releases/latest"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', '').replace('v', '')
                print(f"[GÜNCELLEME] Son sürüm: v{latest_version}")
                
                if self.is_newer(latest_version, self.current_version):
                    print(f"[GÜNCELLEME] Yeni sürüm bulundu! v{latest_version}")
                    update_info = {
                        'version': data.get('tag_name'),
                        'url': data.get('html_url'),
                        'notes': data.get('body', ''),
                        'assets': data.get('assets', [])
                    }
                    self.update_available.emit(update_info)
            else:
                self.error.emit(f"GitHub API hatası: {response.status_code}")
                
        except Exception as e:
            self.error.emit(str(e))

    def is_newer(self, latest, current):
        """Versiyon karşılaştırması (basit)"""
        try:
            l_parts = [int(p) for p in latest.split('.')]
            c_parts = [int(p) for p in current.split('.')]
            return l_parts > c_parts
        except:
            return latest != current

class UpdateService(QObject):
    """Güncelleme yönetim servisi"""
    def __init__(self, current_version="1.0.0", repo="teymensel/tb2asj_telsizsistemi"):
        super().__init__()
        self.current_version = current_version
        self.repo = repo
        self.checker = None

    def check_for_updates(self):
        """Güncelleme kontrolünü başlat"""
        self.checker = UpdateChecker(self.current_version, self.repo)
        return self.checker
