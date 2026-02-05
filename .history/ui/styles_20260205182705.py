"""
Modern UI stilleri - QSS (Qt Style Sheets)
"""

# Koyu tema
DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    background-color: #1a1a2e;
    color: #eee;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* Header */
QLabel#header {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0f4c75, stop:1 #3282b8);
    color: white;
    font-size: 20pt;
    font-weight: bold;
    padding: 20px;
    border-radius: 10px;
    margin: 10px;
}

/* Kartlar */
QFrame#card {
    background-color: #16213e;
    border-radius: 10px;
    padding: 15px;
    margin: 5px;
}

QFrame#card:hover {
    background-color: #1f2e4d;
}

/* Butonlar */
QPushButton {
    background-color: #3282b8;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4a9fd8;
}

QPushButton:pressed {
    background-color: #2a6b99;
}

QPushButton:disabled {
    background-color: #2a3f5f;
    color: #888;
}

QPushButton#dangerButton {
    background-color: #e63946;
}

QPushButton#dangerButton:hover {
    background-color: #f15a5a;
}

QPushButton#successButton {
    background-color: #06d6a0;
}

QPushButton#successButton:hover {
    background-color: #20e6b3;
}

/* Input alanları */
QLineEdit, QComboBox, QSpinBox {
    background-color: #0f1724;
    color: #eee;
    border: 2px solid #3282b8;
    border-radius: 6px;
    padding: 8px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #4a9fd8;
}

/* ComboBox dropdown */
QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-style: solid;
    border-width: 5px;
    border-color: #3282b8 transparent transparent transparent;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eee;
    selection-background-color: #3282b8;
    border: 1px solid #3282b8;
}

/* Slider */
QSlider::groove:horizontal {
    background: #0f1724;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3282b8;
    width: 18px;
    height: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #4a9fd8;
}

QSlider::add-page:horizontal {
    background: #0f1724;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3282b8, stop:1 #4a9fd8);
    border-radius: 4px;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #3282b8;
    background-color: #0f1724;
}

QCheckBox::indicator:checked {
    background-color: #3282b8;
    image: none;
    border: 2px solid #3282b8;
}

/* GroupBox */
QGroupBox {
    background-color: #16213e;
    border: 2px solid #3282b8;
    border-radius: 10px;
    margin-top: 12px;
    padding: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    background-color: #3282b8;
    color: white;
    border-radius: 5px;
}

/* Progress Bar */
QProgressBar {
    background-color: #0f1724;
    border: 2px solid #3282b8;
    border-radius: 8px;
    text-align: center;
    color: white;
    font-weight: bold;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3282b8, stop:1 #06d6a0);
    border-radius: 6px;
}

/* Status widget'ları */
QLabel#statusLabel {
    background-color: rgba(50, 130, 184, 0.2);
    border-left: 4px solid #3282b8;
    padding: 10px;
    border-radius: 5px;
}

QLabel#statusLabel[status="connected"] {
    background-color: rgba(6, 214, 160, 0.2);
    border-left- 4px solid #06d6a0;
}

QLabel#statusLabel[status="error"] {
    background-color: rgba(230, 57, 70, 0.2);
    border-left: 4px solid #e63946;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #0f1724;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #3282b8;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4a9fd8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Açık tema
LIGHT_THEME = """
QMainWindow {
    background-color: #f8f9fa;
}

QWidget {
    background-color: #f8f9fa;
    color: #212529;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QLabel#header {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0f4c75, stop:1 #3282b8);
    color: white;
    font-size: 20pt;
    font-weight: bold;
    padding: 20px;
    border-radius: 10px;
    margin: 10px;
}

QFrame#card {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 15px;
    margin: 5px;
}

QPushButton {
    background-color: #3282b8;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4a9fd8;
}

QPushButton:pressed {
    background-color: #2a6b99;
}

QPushButton#dangerButton {
    background-color: #e63946;
}

QPushButton#dangerButton:hover {
    background-color: #f15a5a;
}

QPushButton#successButton {
    background-color: #06d6a0;
}

QPushButton#successButton:hover {
    background-color: #20e6b3;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: white;
    color: #212529;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #3282b8;
}
"""


def get_theme(theme_name: str = "dark") -> str:
    """
    Tema stilini al
    
    Args:
        theme_name: Tema adı ("dark" veya "light")
    
    Returns:
        QSS stil string'i
    """
    return DARK_THEME if theme_name == "dark" else LIGHT_THEME
