"""
VOX kontrol widget'ı
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSlider, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal


class VOXControlWidget(QWidget):
    """VOX kontrol paneli widget'ı"""
    
    # Sinyaller
    vox_enabled_changed = pyqtSignal(bool)
    threshold_changed = pyqtSignal(int)
    test_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI'ı başlat"""
        self.setObjectName("card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("🎙️ VOX Kontrolü")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # VOX aktif/pasif
        vox_layout = QHBoxLayout()
        self.vox_checkbox = QCheckBox("VOX Aktif")
        self.vox_checkbox.setChecked(False)
        self.vox_checkbox.stateChanged.connect(self._on_vox_toggled)
        vox_layout.addWidget(self.vox_checkbox)
        vox_layout.addStretch()
        layout.addLayout(vox_layout)
        
        # Hassasiyet ayarı
        threshold_label = QLabel("Hassasiyet:")
        layout.addWidget(threshold_label)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Düşük"))
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(30)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        slider_layout.addWidget(self.threshold_slider)
        
        slider_layout.addWidget(QLabel("Yüksek"))
        layout.addLayout(slider_layout)
        
        # Değer göstergesi
        self.value_label = QLabel("Eşik: 30%")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-weight: bold; color: #3282b8;")
        layout.addWidget(self.value_label)
        
        # Test butonu
        test_btn = QPushButton("Manuel Test (PTT)")
        test_btn.clicked.connect(self._on_test_clicked)
        layout.addWidget(test_btn)
        
        # Durum
        self.status_label = QLabel("● VOX Pasif")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _on_vox_toggled(self, state):
        """VOX checkbox değiştiğinde"""
        enabled = state == Qt.CheckState.Checked.value
        self.vox_enabled_changed.emit(enabled)
        
        if enabled:
            self.status_label.setText("✓ VOX Aktif")
            self.status_label.setStyleSheet("color: #06d6a0;")
        else:
            self.status_label.setText("● VOX Pasif")
            self.status_label.setStyleSheet("color: #888;")
    
    def _on_threshold_changed(self, value):
        """Hassasiyet slider'ı değiştiğinde"""
        self.value_label.setText(f"Eşik: {value}%")
        self.threshold_changed.emit(value)
    
    def _on_test_clicked(self):
        """Test butonuna tıklandığında"""
        self.test_requested.emit()
    
    def set_vox_enabled(self, enabled: bool):
        """VOX durumunu ayarla"""
        self.vox_checkbox.setChecked(enabled)
    
    def set_threshold(self, value: int):
        """Eşik değerini ayarla"""
        self.threshold_slider.setValue(value)
    
    def get_vox_enabled(self) -> bool:
        """VOX durumunu al"""
        return self.vox_checkbox.isChecked()
    
    def get_threshold(self) -> int:
        """Eşik değerini al"""
        return self.threshold_slider.value()
