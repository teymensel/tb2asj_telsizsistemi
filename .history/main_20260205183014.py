"""
TB2ASJ - Telsiz Yönetim Sistemi
Ana uygulama giriş noktası
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("TB2ASJ")
    app.setOrganizationName("TB2ASJ")
    
    # Ana pencereyi oluştur
    window = MainWindow()
    window.show()
    
    # Uygulamayı başlat
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
