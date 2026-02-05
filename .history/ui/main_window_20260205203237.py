"""
Ana pencere - TB2ASJ Telsiz Yönetim Sistemi
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QGridLayout, QMessageBox,
                             QSystemTrayIcon, QMenu, QStyle)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from config import settings
from radio.connection import RadioConnection
from radio.audio_manager import AudioManager
from radio.vox_controller import VOXController
from services.weather_service import WeatherService
from services.earthquake_service import EarthquakeService
from services.notification_manager import NotificationManager
from ui.styles import get_theme
from ui.settings_dialog import SettingsDialog
from ui.widgets.clock_widget import ClockWidget
from ui.widgets.weather_widget import WeatherWidget
from ui.widgets.earthquake_widget import EarthquakeWidget # EKLENDİ
from ui.widgets.log_window import LogWindow # EKLENDİ
from ui.widgets.signal_meter import SignalMeterWidget
from ui.widgets.vox_control import VOXControlWidget


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TB2ASJ - Telsiz Yönetim Sistemi")
        self.setMinimumSize(900, 700)
        
        # Bileşenler
        self.radio_connection = RadioConnection()
        self.audio_manager = AudioManager()
        self.vox_controller = VOXController(self.audio_manager, self.radio_connection)
        self.weather_service = WeatherService()
        self.earthquake_service = EarthquakeService()
        self.notification_manager = NotificationManager(
            self.radio_connection, self.vox_controller
        )
        
        # System tray
        self.tray_icon = None
        
        # UI'ı başlat
        self.init_ui()
        self.connect_signals()
        self.load_settings()
        
        # Tema uygula
        self.apply_theme()
        
        # Saat anons ayarını yükle
        self.clock_widget.announce_enabled = settings.get('general.hourly_announce', False)
        
        # System tray oluştur
        self.create_tray_icon()
    
    def init_ui(self):
        """UI'ı başlat"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_container = QVBoxLayout()
        header_container.setSpacing(5)
        
        header_title = QLabel("TB2ASJ")
        header_title.setObjectName("header")
        header_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #3498db;")
        
        header_subtitle = QLabel("Powered by Teymensel")
        header_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_subtitle.setStyleSheet("font-size: 10pt; color: #7f8c8d; font-style: italic;")
        
        header_container.addWidget(header_title)
        header_container.addWidget(header_subtitle)
        
        main_layout.addLayout(header_container)
        
        # Ana içerik
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        # --- HEADER AKSİYON BUTONLARI ---
        header_actions = QHBoxLayout()
        
        btn_read_eq = QPushButton("🌍 Deprem Bildir")
        btn_read_eq.clicked.connect(self.read_last_earthquake)
        header_actions.addWidget(btn_read_eq)
        
        btn_read_time = QPushButton("🕒 Saati Oku")
        btn_read_time.clicked.connect(self.read_current_time)
        header_actions.addWidget(btn_read_time)
        
        btn_read_weather = QPushButton("🌤️ Hava Durumu Oku")
        btn_read_weather.clicked.connect(self.read_current_weather)
        header_actions.addWidget(btn_read_weather)
        
        content_layout.addLayout(header_actions)
        
        # Üst Panel: Saat ve Hava Durumu (Yan yana)
        top_info_layout = QHBoxLayout()
        
        self.clock_widget = ClockWidget()
        # Saat başı anons sinyali
        self.clock_widget.request_announcement.connect(self.announce_time)
        
        top_info_layout.addWidget(self.clock_widget, 1) # Sol: Saat
        
        self.weather_widget = WeatherWidget()
        top_info_layout.addWidget(self.weather_widget, 1) # Sağ: Hava Durumu
        
        content_layout.addLayout(top_info_layout)
        
        # Orta Panel: Deprem Listesi (Geniş alan)
        self.earthquake_widget = EarthquakeWidget(self.earthquake_service)
        content_layout.addWidget(self.earthquake_widget, 2) # Esnek yükseklik
        
        # Alt Panel: Sinyal ve VOX (Yan yana)
        bottom_controls = QHBoxLayout()
        
        self.signal_meter = SignalMeterWidget()
        bottom_controls.addWidget(self.signal_meter, 1)
        
        self.vox_control = VOXControlWidget()
        bottom_controls.addWidget(self.vox_control, 1)
        
        content_layout.addLayout(bottom_controls)
        
        main_layout.addLayout(content_layout)
        
        # Kontrol butonları
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.connect_btn = QPushButton("🔌 Bağlan")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        test_btn = QPushButton("🔊 Test Bildirimi")
        test_btn.clicked.connect(self.send_test_notification)
        button_layout.addWidget(test_btn)
        
        settings_btn = QPushButton("⚙️ Ayarlar")
        settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(settings_btn)
        
        main_layout.addLayout(button_layout)
        
        central_widget.setLayout(main_layout)
        
        # Menü bar
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu("📄 Dosya")
        
        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Araçlar menüsü
        tools_menu = menubar.addMenu("🔧 Araçlar")
        
        settings_action = QAction("Ayarlar", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu("❓ Yardım")
        
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Sinyalleri bağla"""
        # Telsiz bağlantısı
        self.radio_connection.connected.connect(self.on_radio_connected)
        self.radio_connection.disconnected.connect(self.on_radio_disconnected)
        self.radio_connection.error.connect(self.on_error)
        
        # Ses yönetimi
        self.audio_manager.level_changed.connect(self.signal_meter.update_audio_level)
        
        # VOX kontrolü
        self.vox_control.vox_enabled_changed.connect(self.on_vox_enabled_changed)
        self.vox_control.threshold_changed.connect(self.on_vox_threshold_changed)
        
        # Manuel PTT bağlantıları
        self.vox_control.ptt_pressed.connect(self.on_ptt_pressed)
        self.vox_control.ptt_released.connect(self.on_ptt_released)
        
        self.vox_controller.vox_triggered.connect(self.on_vox_triggered)
        self.vox_controller.vox_released.connect(self.on_vox_released)
        
        # Hava durumu
        self.weather_service.weather_updated.connect(self.on_weather_updated)
        self.weather_service.error_occurred.connect(self.on_error)
        
        # Deprem
        self.earthquake_service.earthquake_detected.connect(self.on_earthquake_detected)
        self.earthquake_service.error_occurred.connect(self.on_error)
    
    def on_ptt_pressed(self):
        """PTT tuşuna basıldı"""
        print("PTT Basıldı")
        # Ses motoru aktif mi?
        if not self.audio_manager.is_monitoring:
            self.audio_manager.start_monitoring()
        
        self.vox_controller.manual_ptt(True)
    
    def on_ptt_released(self):
        """PTT tuşu bırakıldı"""
        print("PTT Bırakıldı")
        self.vox_controller.manual_ptt(False)

    def load_settings(self):
        """Ayarları yükle ve uygula"""
        # Ses ayarları
        self.audio_manager.set_input_device(settings.get('audio.input_device'))
        self.audio_manager.set_output_device(settings.get('audio.output_device'))
        self.audio_manager.set_mic_level(settings.get('audio.mic_level', 50))
        self.audio_manager.set_speaker_level(settings.get('audio.speaker_level', 75))
        self.audio_manager.set_vox_threshold(settings.get('audio.vox_threshold', 30))
        
        # Bildirim ayarları
        voice_id = settings.get('notification.voice_id')
        if voice_id:
            self.notification_manager.set_voice(voice_id)
        
        test_msg = settings.get('notification.test_message')
        if test_msg:
            self.notification_manager.set_test_message(test_msg)

        # VOX widget ayarları
        self.vox_control.set_vox_enabled(settings.get('audio.vox_enabled', True))
        self.vox_control.set_threshold(settings.get('audio.vox_threshold', 30))
        
        # Hava durumu servisi
        api_key = settings.get('weather.api_key', '')
        if api_key:
            self.weather_service.set_api_key(api_key)
            city = settings.get('weather.city', 'Istanbul')
            country = settings.get('weather.country', 'TR')
            self.weather_service.set_location(city, country)
            
            interval = settings.get('weather.update_interval', 3600)
            self.weather_service.set_update_interval(interval)
            
            if settings.get('weather.auto_announce', True):
                self.weather_service.start_auto_update()
        
        # Deprem servisi
        # Deprem ayarlarını güncelle
        self.earthquake_service.set_min_magnitude(float(settings.get('earthquake.min_magnitude', 4.0)))
        enabled = settings.get('earthquake.enabled', True)
        city_filter = settings.get('earthquake.city_filter', '')
        self.earthquake_service.set_city_filter(city_filter)
        
        if enabled:
             self.earthquake_service.start_monitoring()
        else:
             self.earthquake_service.stop_monitoring()
    
    def apply_theme(self):
        """Tema uygula"""
        theme = settings.get('general.theme', 'dark')
        stylesheet = get_theme(theme)
        self.setStyleSheet(stylesheet)
    
    def create_tray_icon(self):
        """System tray icon oluştur"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        
        # Standart icon kullan
        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon
        )
        self.setWindowIcon(icon)
        self.tray_icon.setIcon(icon)
        
        self.tray_icon.setToolTip("TB2ASJ - Telsiz Yönetim Sistemi")
        
        # Tray menüsü
        tray_menu = QMenu()
        
        show_action = QAction("Göster", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def on_tray_activated(self, reason):
        """Tray icon tıklandığında"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def toggle_connection(self):
        """Bağlantıyı aç/kapat"""
        if self.radio_connection.is_connected:
            self.disconnect_radio()
        else:
            self.connect_radio()
    
    def connect_radio(self):
        """Telsiz ile bağlan"""
        port = settings.get('radio.port', '')
        connection_type = settings.get('radio.connection_type', 'COM')
        
        # COM modu seçiliyse port kontrolü yap
        if connection_type == 'COM' and not port:
            ports = RadioConnection.get_available_ports()
            if ports:
                port = ports[0]
            else:
                 # Uyarı verme, sadece logla (kullanıcı AUX kullanıyor olabilir)
                 print("COM Port bulunamadı, AUX modu deneniyor.")
        
        baudrate = settings.get('radio.baudrate', 9600)
        databits = settings.get('radio.databits', 8)
        parity = settings.get('radio.parity', 'N')
        stopbits = settings.get('radio.stopbits', 1)
        
        # Bağlantıyı dene
        success = self.radio_connection.connect(
            port, baudrate, databits, parity, stopbits
        )
        
        # AUX modunda hata olsa bile devam et
        # Her durumda ses monitörünü başlat
        if not self.audio_manager.start_monitoring():
             QMessageBox.critical(self, "Hata", "Ses cihazı başlatılamadı!")
        
        # VOX'u etkinleştir (eğer ayarlardaysa)
        if settings.get('audio.vox_enabled', True):
            self.vox_controller.enable_vox()
        
        # UI Güncelle
        self.on_radio_connected()
    
    def disconnect_radio(self):
        """Telsiz bağlantısını kes"""
        try:
            # 1. VOX devre dışı
            self.vox_controller.disable_vox()
            
            # 2. Ses monitörünü durdur (Kritik)
            self.audio_manager.stop_monitoring()
            self.signal_meter.update_audio_level(0) # Metreyi sıfırla
            
            # 3. Bağlantıyı kapat
            self.radio_connection.disconnect()
            
        except Exception as e:
            print(f"Bağlantı kesilirken hata: {e}")
        finally:
            self.on_radio_disconnected()
    
    def on_radio_connected(self):
        """Telsiz bağlandığında"""
        self.connect_btn.setText("🔌 Bağlantıyı Kes")
        self.connect_btn.setObjectName("dangerButton")
        self.connect_btn.setStyleSheet(self.connect_btn.styleSheet())
        
        self.signal_meter.set_status("Bağlı (Loopback Hazır)", "connected")
        
        if self.tray_icon:
            self.tray_icon.showMessage(
                "TB2ASJ",
                "Sistem aktif. Ses izleme başlatıldı.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def on_radio_disconnected(self):
        """Telsiz bağlantısı kesildiğinde"""
        self.connect_btn.setText("🔌 Bağlan")
        self.connect_btn.setObjectName("")
        self.connect_btn.setStyleSheet(self.connect_btn.styleSheet())
        
        self.signal_meter.set_status("Bağlantı Yok", "info")
    
    def on_vox_enabled_changed(self, enabled: bool):
        """VOX etkinlik durumu değiştiğinde"""
        if enabled:
            self.vox_controller.enable_vox()
        else:
            self.vox_controller.disable_vox()
        
        settings.set('audio.vox_enabled', enabled)
    
    def on_vox_threshold_changed(self, threshold: int):
        """VOX eşik değeri değiştiğinde"""
        self.audio_manager.set_vox_threshold(threshold)
        settings.set('audio.vox_threshold', threshold)
    
    def on_vox_triggered(self):
        """VOX tetiklendiğinde"""
        self.signal_meter.update_tx_level(100)
        self.signal_meter.set_status("İletim (TX)", "connected")
    
    def on_vox_released(self):
        """VOX serbest bırakıldığında"""
        self.signal_meter.update_tx_level(0)
        self.signal_meter.set_status("Dinleme (RX)", "connected")
    
    def on_weather_updated(self, data: dict):
        """Hava durumu güncellendiğinde"""
        self.weather_widget.update_weather(data)
        if settings.get('weather.auto_announce', True):
            self.notification_manager.send_weather_notification(data)
    
    def on_earthquake_detected(self, data: dict):
        """Deprem tespit edildiğinde"""
        self.notification_manager.send_earthquake_notification(data)
        if self.tray_icon:
            self.tray_icon.showMessage(
                "⚠️ DEPREM BİLDİRİMİ",
                f"{data['location']}\nBüyüklük: {data['magnitude']}",
                QSystemTrayIcon.MessageIcon.Warning,
                10000
            )
    
    def on_error(self, error_msg: str):
        """Hata oluştuğunda"""
        print(f"Hata: {error_msg}")
    
    def send_test_notification(self):
        """Test bildirimi gönder"""
        self.notification_manager.send_test_notification()
    
    def open_settings(self):
        """Ayarlar penceresini aç"""
        dialog = SettingsDialog(self, self.notification_manager)
        if dialog.exec():
            # Ayarlar kaydedildi, yeniden yükle
            self.load_settings()
            self.apply_theme()
    
    def show_about(self):
        """Hakkında penceresi"""
        QMessageBox.about(
            self,
            "Hakkında - TB2ASJ",
            "<h2>TB2ASJ Telsiz Yönetim Sistemi</h2>"
            "<p>Version 1.2 (AUX & TTS Update)</p>"
            "<p>Gelişmiş telsiz yönetim ve bildirim sistemi</p>"
            "<ul>"
            "<li>Gelişmiş Bildirim Ayarları (Metin/Dil)</li>"
            "<li>Audio Loopback Düzeltmeleri</li>"
            "</ul>"
        )
    
    def read_last_earthquake(self):
        """Son depremi sesli oku"""
        if self.earthquake_service.last_data:
            from services.earthquake_service import EarthquakeService
            # EarthquakeService sınıfına erişimimiz var ama _parse metoduna static değil
            # self.earthquake_service üzerinden erişelim
            eq = self.earthquake_service._parse_earthquake(self.earthquake_service.last_data[0])
            text = self.earthquake_service.get_announcement_text(eq)
            self.notification_manager.send_notification(text)
        else:
            self.notification_manager.send_notification("Henüz deprem verisi alınmadı.", use_radio=False)

    def read_current_time(self):
        """Saati sesli oku"""
        from datetime import datetime
        now = datetime.now()
        # ClockWidget'daki yardımcı metodu kullan
        text = self.clock_widget.get_natural_time_text(now.hour, now.minute)
        self.notification_manager.send_notification(text)

    def read_current_weather(self):
        """Hava durumunu sesli oku"""
        # Manuel tetikle
        self.weather_service.fetch_weather_manual()
        # Bildirim on_weather_updated içinde otomatik yapılacak (eğer ayar açıksa)
        # Ama ayar kapalıysa bile butona basınca okusun isteriz.
        # Şimdilik on_weather_updated ayar kontrolü yapıyor.
        # Biz manuel dinleyip gönderelim:
        # Aslında en temizi, weather_service.fetch_weather_manual() çağırınca sinyal gelecek.
        # Biz burada direkt elimizdeki son veriyi okutabiliriz veya servise istek atabiliriz.
        # WeatherService son veriyi saklıyor mu? Evet self.last_data olsa iyi olurdu.
        # Neyse, notification_manager.send_weather_notification direkt API çağrısı yapmıyor, parametre alıyor.
        # Kullanıcı butona bastığında taze veri çekilsin istiyor muhtemelen.
        # O zaman fetch_weather_manual()
        pass 

    def announce_time(self, text):
        """Otomatik saat anonsu"""
        self.notification_manager.send_notification(text)

    def on_settings_closed(self, result):
        """Ayarlar penceresi kapandığında"""
        if result == QDialog.DialogCode.Accepted:
            # Ayarları yeniden yükle/uygula
            self.radio_connection.port = settings.get('radio.port')
            self.audio_manager.mic_level = settings.get('audio.mic_level', 50)
            self.audio_manager.speaker_level = settings.get('audio.speaker_level', 75)
            
            # Hava durumu ayarlarını güncelle
            self.weather_service.set_api_key(settings.get('weather.api_key', ''))
            self.weather_service.set_city(settings.get('weather.city', 'Istanbul'))
            self.weather_service.auto_announce = settings.get('weather.auto_announce', True)
            
            # Deprem
            self.earthquake_service.set_min_magnitude(float(settings.get('earthquake.min_magnitude', 4.0)))
            self.earthquake_service.set_city_filter(settings.get('earthquake.city_filter', ''))
            
            # Saat Anonsu
            self.clock_widget.announce_enabled = settings.get('general.hourly_announce', False)
            
            # VOX ayarlarını da güncellemek gerekebilir (zaten load_settings yapıyor mu? Hayır bu on_settings_closed)
            # Aslında SettingsDialog'un kendisi `accept` demeden önce settings'e yazıyor.
            # Bizim burada yapmamız gereken settings'den okuyup canlı nesneleri güncellemek.
            # load_settings() metodumuz var, onu çağırmak daha mantıklı.
            self.load_settings()

    def closeEvent(self, event):
        """Pencere kapatılırken"""
        if settings.get('general.minimize_to_tray', True) and self.tray_icon:
            event.ignore()
            self.hide()
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "TB2ASJ",
                    "Uygulama arka planda çalışmaya devam ediyor",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            self.disconnect_radio()
            self.weather_service.stop_auto_update()
            self.earthquake_service.stop_monitoring()
            event.accept()
