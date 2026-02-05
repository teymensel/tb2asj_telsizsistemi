"""
Ayarlar penceresi
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QComboBox, QSpinBox,
                             QCheckBox, QSlider, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from config import settings
from radio.connection import RadioConnection
from radio.audio_manager import AudioManager


class SettingsDialog(QDialog):
    """Ayarlar penceresi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar - TB2ASJ")
        self.setMinimumSize(600, 500)
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
        
        # Data bits
        self.databits_spin = QSpinBox()
        self.databits_spin.setRange(5, 8)
        self.databits_spin.setValue(8)
        layout.addRow("Data Bits:", self.databits_spin)
        
        # Parity
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd"])
        layout.addRow("Parity:", self.parity_combo)
        
        # Stop bits
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "2"])
        layout.addRow("Stop Bits:", self.stopbits_combo)
        
        # Bağlantı tipi
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["COM Port", "AUX"])
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
        
        # VOX
        vox_group = QGroupBox("VOX Ayarları")
        vox_layout = QFormLayout()
        
        self.vox_enabled_check = QCheckBox("VOX Aktif")
        vox_layout.addRow("", self.vox_enabled_check)
        
        self.vox_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.vox_threshold_slider.setRange(0, 100)
        self.vox_threshold_slider.setValue(30)
        self.vox_threshold_label = QLabel("30%")
        self.vox_threshold_slider.valueChanged.connect(
            lambda v: self.vox_threshold_label.setText(f"{v}%")
        )
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(self.vox_threshold_slider)
        threshold_layout.addWidget(self.vox_threshold_label)
        vox_layout.addRow("Hassasiyet:", threshold_layout)
        
        vox_group.setLayout(vox_layout)
        layout.addWidget(vox_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_weather_tab(self) -> QWidget:
        """Hava durumu ayarları sekmesi"""
        widget = QWidget()
        layout = QFormLayout()
        
        # API key
        self.weather_api_key = QLineEdit()
        self.weather_api_key.setPlaceholderText("OpenWeatherMap API anahtarı")
        layout.addRow("API Anahtarı:", self.weather_api_key)
        
        # Şehir
        self.weather_city = QLineEdit()
        self.weather_city.setText("Istanbul")
        layout.addRow("Şehir:", self.weather_city)
        
        # Ülke
        self.weather_country = QLineEdit()
        self.weather_country.setText("TR")
        layout.addRow("Ülke Kodu:", self.weather_country)
        
        # Güncelleme aralığı
        self.weather_interval = QSpinBox()
        self.weather_interval.setRange(5, 1440)  # 5 dk - 24 saat
        self.weather_interval.setValue(60)
        self.weather_interval.setSuffix(" dakika")
        layout.addRow("Güncelleme Aralığı:", self.weather_interval)
        
        # Otomatik duyuru
        self.weather_auto_announce = QCheckBox("Otomatik Duyuru")
        self.weather_auto_announce.setChecked(True)
        layout.addRow("", self.weather_auto_announce)
        
        widget.setLayout(layout)
        return widget
    
    def create_earthquake_tab(self) -> QWidget:
        """Deprem ayarları sekmesi"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Etkin
        self.earthquake_enabled = QCheckBox("Deprem Bildirimleri Aktif")
        self.earthquake_enabled.setChecked(True)
        layout.addRow("", self.earthquake_enabled)
        
        # Minimum büyüklük
        self.earthquake_min_mag = QSpinBox()
        self.earthquake_min_mag.setRange(0, 10)
        self.earthquake_min_mag.setValue(4)
        self.earthquake_min_mag.setSingleStep(1)
        self.earthquake_min_mag.setSuffix(" büyüklük")
        layout.addRow("Minimum Büyüklük:", self.earthquake_min_mag)
        
        # Kontrol aralığı
        self.earthquake_interval = QSpinBox()
        self.earthquake_interval.setRange(30, 600)
        self.earthquake_interval.setValue(60)
        self.earthquake_interval.setSuffix(" saniye")
        layout.addRow("Kontrol Aralığı:", self.earthquake_interval)
        
        widget.setLayout(layout)
        return widget
    
    def create_general_tab(self) -> QWidget:
        """Genel ayarlar sekmesi"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Otomatik başlat
        self.auto_start = QCheckBox("Windows ile Birlikte Başlat")
        layout.addRow("", self.auto_start)
        
        # System tray'e küçült
        self.minimize_to_tray = QCheckBox("System Tray'e Küçült")
        self.minimize_to_tray.setChecked(True)
        layout.addRow("", self.minimize_to_tray)
        
        # Tema
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Koyu Tema", "Açık Tema"])
        layout.addRow("Tema:", self.theme_combo)
        
        # Dil
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English"])
        layout.addRow("Dil:", self.language_combo)
        
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """Ayarları yükle"""
        # Telsiz
        port = settings.get('radio.port', '')
        if port:
            index = self.port_combo.findText(port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
        
        baudrate = str(settings.get('radio.baudrate', 9600))
        self.baudrate_combo.setCurrentText(baudrate)
        self.databits_spin.setValue(settings.get('radio.databits', 8))
        
        parity_map = {'N': 'None', 'E': 'Even', 'O': 'Odd'}
        parity = parity_map.get(settings.get('radio.parity', 'N'), 'None')
        self.parity_combo.setCurrentText(parity)
        
        # Ses
        self.mic_level_slider.setValue(settings.get('audio.mic_level', 50))
        self.speaker_level_slider.setValue(settings.get('audio.speaker_level', 75))
        self.vox_enabled_check.setChecked(settings.get('audio.vox_enabled', True))
        self.vox_threshold_slider.setValue(settings.get('audio.vox_threshold', 30))
        
        # Hava durumu
        self.weather_api_key.setText(settings.get('weather.api_key', ''))
        self.weather_city.setText(settings.get('weather.city', 'Istanbul'))
        self.weather_country.setText(settings.get('weather.country', 'TR'))
        self.weather_interval.setValue(settings.get('weather.update_interval', 3600) // 60)
        self.weather_auto_announce.setChecked(settings.get('weather.auto_announce', True))
        
        # Deprem
        self.earthquake_enabled.setChecked(settings.get('earthquake.enabled', True))
        self.earthquake_min_mag.setValue(int(settings.get('earthquake.min_magnitude', 4.0)))
        self.earthquake_interval.setValue(settings.get('earthquake.check_interval', 60))
        
        # Genel
        self.auto_start.setChecked(settings.get('general.auto_start', False))
        self.minimize_to_tray.setChecked(settings.get('general.minimize_to_tray', True))
        
        theme = "Koyu Tema" if settings.get('general.theme', 'dark') == 'dark' else "Açık Tema"
        self.theme_combo.setCurrentText(theme)
    
    def save_settings(self):
        """Ayarları kaydet"""
        # Telsiz
        port = self.port_combo.currentText()
        if port != "Otomatik":
            settings.set('radio.port', port)
        
        settings.set('radio.baudrate', int(self.baudrate_combo.currentText()))
        settings.set('radio.databits', self.databits_spin.value())
        
        parity_map = {'None': 'N', 'Even': 'E', 'Odd': 'O'}
        settings.set('radio.parity', parity_map[self.parity_combo.currentText()])
        
        settings.set('radio.stopbits', int(self.stopbits_combo.currentText()))
        
        # Ses
        settings.set('audio.mic_level', self.mic_level_slider.value())
        settings.set('audio.speaker_level', self.speaker_level_slider.value())
        settings.set('audio.vox_enabled', self.vox_enabled_check.isChecked())
        settings.set('audio.vox_threshold', self.vox_threshold_slider.value())
        
        # Hava durumu
        settings.set('weather.api_key', self.weather_api_key.text())
        settings.set('weather.city', self.weather_city.text())
        settings.set('weather.country', self.weather_country.text())
        settings.set('weather.update_interval', self.weather_interval.value() * 60)
        settings.set('weather.auto_announce', self.weather_auto_announce.isChecked())
        
        # Deprem
        settings.set('earthquake.enabled', self.earthquake_enabled.isChecked())
        settings.set('earthquake.min_magnitude', float(self.earthquake_min_mag.value()))
        settings.set('earthquake.check_interval', self.earthquake_interval.value())
        
        # Genel
        settings.set('general.auto_start', self.auto_start.isChecked())
        settings.set('general.minimize_to_tray', self.minimize_to_tray.isChecked())
        
        theme = 'dark' if self.theme_combo.currentText() == "Koyu Tema" else 'light'
        settings.set('general.theme', theme)
        
        self.accept()
