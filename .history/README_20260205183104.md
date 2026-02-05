# TB2ASJ - Telsiz Yönetim Sistemi

Modern, hafif ve profesyonel telsiz yönetim masaüstü uygulaması.

## 🎯 Özellikler

### 📡 Telsiz Bağlantısı
- **COM Port Desteği**: Seri port ile telsiz bağlantısı
- **AUX Alternatifi**: COM port çalışmazsa ses kartı üzerinden bağlantı
- **PTT Kontrolü**: Push-to-Talk yönetimi
- **Sinyal Göstergesi**: RX/TX sinyal seviyeleri

### 🎙️ VOX (Voice Operated Switch)
- Ses tetiklemeli otomatik PTT
- Ayarlanabilir hassasiyet
- Mikrofon seviye kontrolü
- Manuel test modu

### 🌤️ Hava Durumu
- OpenWeatherMap API entegrasyonu
- Otomatik saatlik güncelleme
- Telsiz üzerinden sesli bildirim
- Sıcaklık, nem, rüzgar bilgileri

### 🌍 Deprem Bildirimleri
- Kandilli Rasathanesi API ile anlık takip
- Ayarlanabilir minimum büyüklük filtresi
- Acil sesli bildirim
- Desktop ve tray bildirimleri

### 🎨 Modern Arayüz
- Koyu ve açık tema desteği
- Profesyonel tasarım
- System tray entegrasyonu
- Türkçe dil desteği

## 📋 Gereksinimler

- Python 3.10 veya üzeri
- Windows 10/11
- COM port veya ses kartı

## 🚀 Kurulum

1. **Projeyi klonlayın**:
   ```bash
   git clone <repo-url>
   cd tb2asj_telsizsistemi
   ```

2. **Sanal ortam oluşturun** (önerilen):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Bağımlılıkları yükleyin**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Konfigürasyon

### Hava Durumu API
1. [OpenWeatherMap](https://openweathermap.org/api) üzerinden ücretsiz API anahtarı alın
2. Uygulamayı açın
3. Ayarlar → Hava Durumu sekmesinde API anahtarınızı girin

### COM Port Ayarları
1. Telsizinizi bilgisayara bağlayın
2. Ayarlar → Telsiz sekmesinden COM portunu seçin
3. Baud rate ve diğer ayarları yapın (genellikle varsayılan değerler işe yarar)

### Ses Cihazları
1. Ayarlar → Ses sekmesinden mikrofon ve hoparlörü seçin
2. Ses seviyelerini ayarlayın
3. VOX hassasiyetini test ederek optimize edin

## 🎮 Kullanım

### İlk Başlatma
```bash
python main.py
```

### Bağlantı Kurma
1. Ana ekranda "🔌 Bağlan" butonuna tıklayın
2. Telsiz bağlantısı kurulacak ve VOX aktif olacak
3. Sinyal göstergesinde bağlantı durumunu görebilirsiniz

### VOX Kullanımı
- VOX aktifken mikrofona konuştuğunuzda otomatik PTT devreye girer
- Hassasiyeti "VOX Kontrolü" panelinden ayarlayın
- "Manuel Test" ile PTT'yi test edebilirsiniz

### Bildirimler
- **Hava Durumu**: Ayarlarda belirlenen aralıklarla otomatik duyuru
- **Deprem**: Minimum büyüklüğün üzerindeki depremler anında bildirilir
- **Test**: "Test Bildirimi" butonu ile sistemi test edin

### System Tray
- Pencereyi kapatınca uygulama arka planda çalışmaya devam eder
- Tray icon'a çift tıklayarak pencereyi tekrar açabilirsiniz
- Sağ tık ile menüye erişebilirsiniz

## 📁 Proje Yapısı

```
tb2asj_telsizsistemi/
├── main.py                 # Ana uygulama giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── config/                 # Konfigürasyon modülü
│   ├── settings.py        # Ayarlar yöneticisi
│   └── settings_default.json
├── radio/                  # Telsiz modülleri
│   ├── connection.py      # COM port yönetimi
│   ├── audio_manager.py   # Ses kontrolü
│   └── vox_controller.py  # VOX mantığı
├── services/               # Servisler
│   ├── weather_service.py       # Hava durumu
│   ├── earthquake_service.py    # Deprem
│   └── notification_manager.py  # Bildirimler
└── ui/                     # Kullanıcı arayüzü
    ├── main_window.py     # Ana pencere
    ├── settings_dialog.py # Ayarlar dialogu
    ├── styles.py          # Temalar
    └── widgets/           # Özel widget'lar
        ├── clock_widget.py
        ├── weather_widget.py
        ├── signal_meter.py
        └── vox_control.py
```

## 🔧 Sorun Giderme

### COM Port Bulunamıyor
- Telsiz bağlantısını kontrol edin
- Driver'ların güncel olduğundan emin olun
- Windows Cihaz Yöneticisi'nden portu doğrulayın

### Ses Cihazı Çalışmıyor
- Ayarlarda doğru cihazı seçtiğinizden emin olun
- Mikrofon izinlerini kontrol edin
- Ses seviyelerini test edin

### Hava Durumu Gelmiyor
- API anahtarınızın geçerli olduğunu kontrol edin
- İnternet bağlantınızı kontrol edin
- Şehir adını doğru girdiğinizden emin olun

### VOX Çok Hassas/Duyarsız
- VOX kontrolü panelinden hassasiyeti ayarlayın
- Mikrofon seviyesini düzenleyin
- Ortam gürültüsünü azaltmaya çalışın

## 📝 Lisans

Bu proje açık kaynak olarak paylaşılmıştır.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

## 📞 Destek

Sorun bildirmek veya öneride bulunmak için: TB2ASJ

---

**TB2ASJ Telsiz Yönetim Sistemi** - Gelişmiş, Modern, Güvenilir
