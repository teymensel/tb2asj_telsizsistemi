"""
Ayarlar penceresi
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QComboBox, QSpinBox,
                             QCheckBox, QSlider, QPushButton, QGroupBox, QFormLayout, QTextEdit)
from PyQt6.QtCore import Qt
from config import settings
from radio.connection import RadioConnection
from radio.audio_manager import AudioManager
from services.notification_manager import NotificationManager


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
        """Bildirim ayarları sekmesi (YENİ)"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Ses Seçimi
        self.voice_combo = QComboBox()
        if self.notification_manager:
            voices = self.notification_manager.get_available_voices()
            self.voice_map = {} # Combo index -> Voice ID
            for i, voice in enumerate(voices):
                display_name = f"{voice['name']} ({voice['lang']})"
                self.voice_combo.addItem(display_name)
                self.voice_map[i] = voice['id']
        else:
            self.voice_combo.addItem("Ses motoru bulunamadı")
        
        layout.addRow("Konuşma Sesi:", self.voice_combo)
        
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
        widget = QWidget()
        layout = QFormLayout()
        self.weather_api_key = QLineEdit()
        self.weather_api_key.setPlaceholderText("OpenWeatherMap API anahtarı")
        layout.addRow("API Anahtarı:", self.weather_api_key)
        self.weather_city = QLineEdit()
        self.weather_city.setText("Istanbul")
        layout.addRow("Şehir:", self.weather_city)
        self.weather_auto_announce = QCheckBox("Otomatik Duyuru")
        self.weather_auto_announce.setChecked(True)
        layout.addRow("", self.weather_auto_announce)
        widget.setLayout(layout)
        return widget
    
    def create_earthquake_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout()
        self.earthquake_enabled = QCheckBox("Deprem Bildirimleri Aktif")
        self.earthquake_enabled.setChecked(True)
        layout.addRow("", self.earthquake_enabled)
        self.earthquake_min_mag = QSpinBox()
        self.earthquake_min_mag.setRange(0, 10)
        self.earthquake_min_mag.setValue(4)
        layout.addRow("Minimum Büyüklük:", self.earthquake_min_mag)
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
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Koyu Tema", "Açık Tema"])
        layout.addRow("Tema:", self.theme_combo)
        widget.setLayout(layout)
        return widget
    
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
            
    def load_settings(self):
        """Ayarları yükle"""
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
        saved_voice = settings.get('notification.voice_id')
        if saved_voice and hasattr(self, 'voice_map'):
            for idx, vid in self.voice_map.items():
                if vid == saved_voice:
                    self.voice_combo.setCurrentIndex(idx)
                    break
        
        saved_msg = settings.get('notification.test_message')
        if saved_msg:
            self.test_message_input.setText(saved_msg)
        
        # Diğer
        self.weather_api_key.setText(settings.get('weather.api_key', ''))
        self.earthquake_enabled.setChecked(settings.get('earthquake.enabled', True))
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
        idx = self.voice_combo.currentIndex()
        if hasattr(self, 'voice_map'):
             voice_id = self.voice_map.get(idx)
             settings.set('notification.voice_id', voice_id)
        
        msg = self.test_message_input.toPlainText()
        settings.set('notification.test_message', msg)
        
        # Diğer
        settings.set('weather.api_key', self.weather_api_key.text())
        settings.set('general.auto_start', self.auto_start.isChecked())
        settings.set('general.theme', 'dark' if self.theme_combo.currentText() == "Koyu Tema" else 'light')
        
        self.accept()
