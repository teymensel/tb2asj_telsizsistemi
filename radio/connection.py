"""
Telsiz bağlantı yöneticisi - COM port ve AUX bağlantı
"""
import serial
import serial.tools.list_ports
from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal


class RadioConnection(QObject):
    """Telsiz bağlantı sınıfı"""
    
    # Sinyaller
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)
    data_received = pyqtSignal(bytes)
    
    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.connection_type = "COM"  # COM veya AUX
    
    @staticmethod
    def get_available_ports() -> List[str]:
        """
        Mevcut COM portlarını listele
        
        Returns:
            Port isimlerinin listesi
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = 9600, 
                databits: int = 8, parity: str = 'N', 
                stopbits: int = 1, timeout: float = 1.0) -> bool:
        """
        Telsiz ile bağlantı kur
        
        Args:
            port: COM port adı (örn: "COM3")
            baudrate: İletişim hızı
            databits: Veri biti sayısı
            parity: Parite kontrolü (N=None, E=Even, O=Odd)
            stopbits: Dur biti sayısı
            timeout: Okuma zaman aşımı
        
        Returns:
            Bağlantı başarılı ise True
        """
        try:
            # Parity çevirisi
            parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 
                         'O': serial.PARITY_ODD}
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=databits,
                parity=parity_map.get(parity, serial.PARITY_NONE),
                stopbits=stopbits,
                timeout=timeout
            )
            
            self.is_connected = True
            self.connection_type = "COM"
            self.connected.emit()
            return True
            
        except serial.SerialException as e:
            self.error.emit(f"Bağlantı hatası: {str(e)}")
            return False
        except Exception as e:
            self.error.emit(f"Beklenmeyen hata: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Bağlantıyı kes"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.is_connected = False
        self.disconnected.emit()
    
    def send_data(self, data: bytes) -> bool:
        """
        Telsiz ile veri gönder
        
        Args:
            data: Gönderilecek byte verisi
        
        Returns:
            Gönderim başarılı ise True
        """
        if not self.is_connected or not self.serial_port:
            self.error.emit("Bağlantı yok")
            return False
        
        try:
            self.serial_port.write(data)
            return True
        except Exception as e:
            self.error.emit(f"Veri gönderilemedi: {str(e)}")
            return False
    
    def read_data(self, size: int = 1024) -> Optional[bytes]:
        """
        Telsizdeki veriyi oku
        
        Args:
            size: Okunacak maksimum byte sayısı
        
        Returns:
            Okunan veri veya None
        """
        if not self.is_connected or not self.serial_port:
            return None
        
        try:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(min(size, self.serial_port.in_waiting))
                self.data_received.emit(data)
                return data
            return None
        except Exception as e:
            self.error.emit(f"Veri okunamadı: {str(e)}")
            return None
    
    def ptt_on(self) -> bool:
        """
        PTT (Push-to-Talk) aktif et - İletim başlat
        
        Returns:
            Başarılı ise True
        """
        # DTR veya RTS pinini kullanarak PTT kontrolü
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.dtr = True
            return True
        except Exception as e:
            self.error.emit(f"PTT açılamadı: {str(e)}")
            return False
    
    def ptt_off(self) -> bool:
        """
        PTT kapat - İletimi durdur
        
        Returns:
            Başarılı ise True
        """
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.dtr = False
            return True
        except Exception as e:
            self.error.emit(f"PTT kapatılamadı: {str(e)}")
            return False
