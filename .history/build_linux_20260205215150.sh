#!/bin/bash

# TB2ASJ Telsiz Sistemi - Linux Build Scripti

echo "TB2ASJ Linux Build Başlatılıyor..."

# 1. Gerekli paketlerin kontrolü
echo "[1/4] Bağımlılıklar kontrol ediliyor..."
pip install -r requirements.txt
pip install pyinstaller

# 2. Eski build dosyalarını temizle
echo "[2/4] Temizlik yapılıyor..."
rm -rf build dist *.spec

# 3. PyInstaller ile derle
# Not: Linux'ta path ayracı ':' olduğu için --add-data formatı farklıdır.
echo "[3/4] Derleme işlemi başlatılıyor..."
pyinstaller --noconsole --onefile --name="TB2ASJ_Telsiz" --clean --add-data "config/settings_default.json:config" main.py

# 4. Sonuç
if [ -f "dist/TB2ASJ_Telsiz" ]; then
    echo ""
    echo "✅ İŞLEM BAŞARILI!"
    echo "Çıktı dosyası: dist/TB2ASJ_Telsiz"
    echo "Çalıştırmak için: ./dist/TB2ASJ_Telsiz"
else
    echo ""
    echo "❌ HATA: Build işlemi başarısız oldu."
fi
