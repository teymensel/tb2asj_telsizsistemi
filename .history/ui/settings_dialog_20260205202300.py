"""
Ayarlar penceresi
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QComboBox, QSpinBox,
                             QCheckBox, QSlider, QPushButton, QGroupBox, 
                             QFormLayout, QTextEdit, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from config import settings
from radio.connection import RadioConnection
from radio.audio_manager import AudioManager


class SettingsDialog(QDialog):
    """Ayarlar penceresi"""
    
    def __init__(self, parent=None, notification_manager=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.setWindowTitle("Ayarlar - TB2ASJ")
        self.setMinimumSize(600, 550)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """UI'ı başlat"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        
        # Sekmeler
        tabs.addTab(self.create_radio_tab(), "📡 Telsiz")
        tabs.addTab(self.create_audio_tab(), "🎙️ Ses")
        tabs.addTab(self.create_notification_tab(), "🔔 Bildirimler")
        tabs.addTab(self.create_weather_tab(), "🌤️ Hava Durumu")
        tabs.addTab(self.create_earthquake_tab(), "🌍 Deprem")
        tabs.addTab(self.create_general_tab(), "⚙️ Genel")
        
        layout.addWidget(tabs)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Kaydet")
        save_btn.setObjectName("successButton")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_radio_tab(self) -> QWidget:
        """Telsiz ayarları sekmesi"""
        widget = QWidget()
        layout = QFormLayout()
        
        # COM port
        self.port_combo = QComboBox()
        ports = RadioConnection.get_available_ports()
        self.port_combo.addItems(["Otomatik"] + ports)
        layout.addRow("COM Port:", self.port_combo)
        
        # Baud rate
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        layout.addRow("Baud Rate:", self.baudrate_combo)
        
        # Bağlantı tipi
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["COM Port", "AUX (Sadece Ses)"])
        layout.addRow("Bağlantı Tipi:", self.connection_type_combo)
        
        widget.setLayout(layout)
        return widget
    
    def create_audio_tab(self) -> QWidget:
        """Ses ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Giriş cihazı
        input_group = QGroupBox("Giriş (Mikrofon)")
        input_layout = QFormLayout()
        
        self.input_device_combo = QComboBox()
        input_devices, _ = AudioManager.get_audio_devices()
        self.input_device_combo.addItem("Varsayılan", None)
        for device in input_devices:
            self.input_device_combo.addItem(device['name'], device['id'])
        input_layout.addRow("Cihaz:", self.input_device_combo)
        
        self.mic_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.mic_level_slider.setRange(0, 100)
        self.mic_level_slider.setValue(50)
        self.mic_level_label = QLabel("50%")
        self.mic_level_slider.valueChanged.connect(
            lambda v: self.mic_level_label.setText(f"{v}%")
        )
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(self.mic_level_slider)
        mic_layout.addWidget(self.mic_level_label)
        input_layout.addRow("Seviye:", mic_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Çıkış cihazı
        output_group = QGroupBox("Çıkış (Hoparlör)")
        output_layout = QFormLayout()
        
        self.output_device_combo = QComboBox()
        _, output_devices = AudioManager.get_audio_devices()
        self.output_device_combo.addItem("Varsayılan", None)
        for device in output_devices:
            self.output_device_combo.addItem(device['name'], device['id'])
        output_layout.addRow("Cihaz:", self.output_device_combo)
        
        self.speaker_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.speaker_level_slider.setRange(0, 100)
        self.speaker_level_slider.setValue(75)
        self.speaker_level_label = QLabel("75%")
        self.speaker_level_slider.valueChanged.connect(
            lambda v: self.speaker_level_label.setText(f"{v}%")
        )
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(self.speaker_level_slider)
        speaker_layout.addWidget(self.speaker_level_label)
        output_layout.addRow("Seviye:", speaker_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        widget.setLayout(layout)
        return widget

    def create_notification_tab(self) -> QWidget:
        """Bildirim ayarları sekmesi (Gelişmiş)"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Sağlayıcı Seçimi
        self.provider_combo = QComboBox()
        if self.notification_manager:
            providers = self.notification_manager.get_providers_list()
            self.provider_combo.addItems(providers)
            
            # Mevcut seçimi bul
            current = self.notification_manager.current_provider.get_name()
            idx = self.provider_combo.findText(current)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)
                
            self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        
        layout.addRow("TTS Motoru:", self.provider_combo)
        
        # Ses Seçimi
        self.voice_combo = QComboBox()
        self._refresh_voices() # Sesleri doldur
        layout.addRow("Konuşmacı:", self.voice_combo)
        
        # Test Metni
        self.test_message_input = QTextEdit()
        self.test_message_input.setPlaceholderText("Test bildirimi metnini buraya girin...")
        self.test_message_input.setMaximumHeight(80)
        self.test_message_input.setText("TB2ASJ telsiz sistemi ses testi. Bir, iki, üç. Ses kontrol.")
        layout.addRow("Test Mesajı:", self.test_message_input)
        
        # Test Butonu (Burada da olsun)
        test_now_btn = QPushButton("🔊 Sesi Test Et")
        test_now_btn.clicked.connect(self._test_voice_now)
        layout.addRow("", test_now_btn)
        
        widget.setLayout(layout)
        return widget

    def create_weather_tab(self) -> QWidget:
        """Hava durumu ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout() # Ana layout
        
        # Hava Durumu Grubu
        weather_group = QGroupBox("Hava Durumu Servisi")
        weather_layout = QFormLayout() # Form layout'u burada tanımla
        
        self.weather_api_key = QLineEdit()
        self.weather_api_key.setPlaceholderText("OpenWeatherMap API anahtarı")
        weather_layout.addRow("API Anahtarı:", self.weather_api_key)
        
        self.weather_city = QLineEdit("Istanbul") # Varsayılan şehir
        weather_layout.addRow("Şehir:", self.weather_city)
        
        self.weather_auto_announce = QCheckBox("Otomatik Duyuru")
        self.weather_auto_announce.setChecked(True)
        weather_layout.addRow("", self.weather_auto_announce)
        
        # Test Butonu
        test_weather_btn = QPushButton("🔊 Test Duyurusu")
        test_weather_btn.clicked.connect(self._test_weather_voice)
        weather_layout.addRow("", test_weather_btn)
        
        weather_group.setLayout(weather_layout)
        layout.addWidget(weather_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_earthquake_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Deprem Ayarları
        earthquake_group = QGroupBox("Deprem Uyarı Sistemi")
        earthquake_layout = QFormLayout()
        
        self.earthquake_enabled = QCheckBox("Deprem uyarılarını etkinleştir")
        self.earthquake_enabled.setChecked(True)
        
        self.earthquake_min_mag = QDoubleSpinBox()
        self.earthquake_min_mag.setRange(0.0, 9.0)
        self.earthquake_min_mag.setValue(4.0)
        self.earthquake_min_mag.setSingleStep(0.1)
        
        self.eq_city_filter = QLineEdit()
        self.eq_city_filter.setPlaceholderText("Örn: Istanbul (Boş bırakırsanız tüm Türkiye)")
        
        earthquake_layout.addRow(self.earthquake_enabled)
        earthquake_layout.addRow("Minimum Büyüklük:", self.earthquake_min_mag)
        earthquake_layout.addRow("Bölge Filtresi (Opsiyonel):", self.eq_city_filter)
        
        # Test Butonu
        test_eq_btn = QPushButton("🔊 Test Uyarısı")
        test_eq_btn.clicked.connect(self._test_earthquake_voice)
        earthquake_layout.addRow("", test_eq_btn)
        
        earthquake_group.setLayout(earthquake_layout)
        layout.addWidget(earthquake_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout()
        
        self.auto_start = QCheckBox("Windows ile Birlikte Başlat")
        layout.addRow("", self.auto_start)
        
        self.minimize_to_tray = QCheckBox("System Tray'e Küçült")
        self.minimize_to_tray.setChecked(True)
        layout.addRow("", self.minimize_to_tray)
        
        # Yeni: Saat Başı Anons
        self.hourly_announce = QCheckBox("Saat ve yarım saatlerde sesli anons yap")
        layout.addRow("", self.hourly_announce)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Koyu Tema", "Açık Tema"])
        layout.addRow("Tema:", self.theme_combo)
        
        widget.setLayout(layout)
        return widget
    
    def _on_provider_changed(self, text):
        """Sağlayıcı değişince sesleri güncelle"""
        if self.notification_manager:
            self.notification_manager.set_provider(text)
            self._refresh_voices()

    def _refresh_voices(self):
        """Ses listesini yenile"""
        self.voice_combo.clear()
        self.voice_map = {}
        
        if self.notification_manager:
            voices = self.notification_manager.get_available_voices()
            for i, voice in enumerate(voices):
                display_name = f"{voice['name']}"
                if 'lang' in voice:
                    display_name += f" ({voice['lang']})"
                
                self.voice_combo.addItem(display_name)
                self.voice_map[i] = voice['id']

    def _test_voice_now(self):
        """Ayarlar menüsünde anlık ses testi"""
        if self.notification_manager:
            # Seçili sesi geçici olarak ayarla
            idx = self.voice_combo.currentIndex()
            voice_id = self.voice_map.get(idx)
            if voice_id:
                self.notification_manager.set_voice(voice_id)
            
            # Mesajı gönder
            msg = self.test_message_input.toPlainText()
            self.notification_manager.send_notification(msg, use_radio=False) # Sadece hoparlör

    def _test_weather_voice(self):
        """Hava durumu test anonsu"""
        if self.notification_manager:
            fake_data = {
                'city': self.weather_city.text() or 'Test Şehri',
                'description': 'parçalı bulutlu',
                'temperature': 23,
                'humidity': 45,
                'wind_speed': 12
            }
            # Sadece hoparlöre ver (Test amaçlı)
            # NotificationManager.send_weather_notification normalde radyoya da basar
            # Şimdilik direkt metin oluşturup okutalım veya metodu modifiye edelim
            # Basit olması için send_notification kullanalım
            
            text = (f"Hava durumu raporu. {fake_data['city']} için hava şu an "
                    f"{fake_data['description']}. Sıcaklık {fake_data['temperature']} derece. "
                    f"Nem oranı yüzde {fake_data['humidity']}. "
                    f"Rüzgar hızı saatte {fake_data['wind_speed']} kilometre.")
            
            self.notification_manager.send_notification(text, use_radio=False)

    def _test_earthquake_voice(self):
        """Deprem test anonsu"""
        if self.notification_manager:
            city = self.eq_city_filter.text() or "Istanbul - PENDIK"
            
            text = (f"Deprem uyarısı! Deprem uyarısı! {city} bölgesinde "
                    f"5.2 büyüklüğünde deprem oldu. Derinlik 10 kilometre.")
            
            self.notification_manager.send_notification(text, use_radio=False)
            
    def load_settings(self):
        """Ayarları yükle"""
        # ... (Telsiz ve Ses kısmı değişmedi) ...
        # Telsiz
        port = settings.get('radio.port', '')
        if port:
            index = self.port_combo.findText(port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
        
        # Ses
        self.mic_level_slider.setValue(settings.get('audio.mic_level', 50))
        self.speaker_level_slider.setValue(settings.get('audio.speaker_level', 75))
        
        # Bildirimler
        saved_provider = settings.get('notification.provider')
        if saved_provider:
            idx = self.provider_combo.findText(saved_provider)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)
                # Provider değiştiği için sesleri güncellememiz lazım olabilir
                # ama setCurrentIndex sinyal tetikler mi? Genellikle evet.
                # Yine de manuel refresh yapalım
                self._on_provider_changed(saved_provider)
                
        saved_voice = settings.get('notification.voice_id')
        if saved_voice and hasattr(self, 'voice_map'):
            for idx, vid in self.voice_map.items():
                if vid == saved_voice:
                    self.voice_combo.setCurrentIndex(idx)
                    break
        
        saved_msg = settings.get('notification.test_message')
        if saved_msg:
            self.test_message_input.setText(saved_msg)
        
        # Deprem
        self.earthquake_enabled.setChecked(settings.get('earthquake.enabled', True))
        self.earthquake_min_mag.setValue(float(settings.get('earthquake.min_magnitude', 4.0)))
        self.eq_city_filter.setText(settings.get('earthquake.city_filter', ''))
        
        self.auto_start.setChecked(settings.get('general.auto_start', False))
    
    def save_settings(self):
        """Ayarları kaydet"""
        # Telsiz
        if self.port_combo.currentText() != "Otomatik":
            settings.set('radio.port', self.port_combo.currentText())
        
        # Ses
        settings.set('audio.mic_level', self.mic_level_slider.value())
        settings.set('audio.speaker_level', self.speaker_level_slider.value())
        settings.set('audio.input_device', self.input_device_combo.currentData())
        settings.set('audio.output_device', self.output_device_combo.currentData())
        
        # Bildirimler
        settings.set('notification.provider', self.provider_combo.currentText())
        
        idx = self.voice_combo.currentIndex()
        if hasattr(self, 'voice_map'):
             voice_id = self.voice_map.get(idx)
             settings.set('notification.voice_id', voice_id)
        
        msg = self.test_message_input.toPlainText()
        settings.set('notification.test_message', msg)
        
        # Diğer
        settings.set('weather.api_key', self.weather_api_key.text())
        settings.set('weather.city', self.weather_city.text())
        
        settings.set('earthquake.enabled', self.earthquake_enabled.isChecked())
        settings.set('earthquake.min_magnitude', self.earthquake_min_mag.value())
        settings.set('earthquake.city_filter', self.eq_city_filter.text())
        
        settings.set('general.auto_start', self.auto_start.isChecked())
        settings.set('general.theme', 'dark' if self.theme_combo.currentText() == "Koyu Tema" else 'light')
        
        self.accept()
