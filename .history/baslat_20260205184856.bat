@echo off
title TB2ASJ Telsiz Sistemi Baslatici
color 0A

echo TB2ASJ Telsiz Yonetim Sistemi Baslatiliyor...
echo --------------------------------------------
echo.

:: Scriptin bulundugu dizine git
cd /d "%~dp0"

:: Sanal ortam kontrolu (venv varsa kullan)
if exist venv\Scripts\activate.bat (
    echo Sanal ortam aktif ediliyor...
    call venv\Scripts\activate.bat
)

:: Uygulamayi baslat
echo Python uygulamasi calistiriliyor...
python main.py

:: Eger uygulama hata ile kapanirsa pencereyi acik tut
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo --------------------------------------------
    echo Bir hata olustu! Pencere kapanmadan once hata mesajini okuyabilirsiniz.
    pause
)
