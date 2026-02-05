@echo off
title TB2ASJ Telsiz - Baslatiliyor
color 0B
cls

echo.
echo  ========================================
echo   TB2ASJ Telsiz Yonetim Sistemi
echo  ========================================
echo.
echo  [INFO] Uygulama baslatiliyor, lutfen bekleyin...
echo.

:: Scriptin oldugu klasore git
cd /d "%~dp0"

:: Venv varsa aktif et, yoksa devam et
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat >nul 2>&1
)

:: Uygulamayi baslat
python main.py

:: Hata olursa ekrani beklet
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  [HATA] Uygulama bir hata ile kapandi!
    echo.
    pause
)
