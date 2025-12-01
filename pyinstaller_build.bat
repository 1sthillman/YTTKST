@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - PyInstaller Derleme
echo =====================================================

echo Gerekli modulleri yukluyor...
pip install pyinstaller customtkinter pillow requests chat-downloader

echo PyInstaller ile paketleme islemi basliyor...

REM Farklı Python sürümleri için Script dizinlerini PATH'e ekle
set PATH=%PATH%;%USERPROFILE%\AppData\Roaming\Python\Python313\Scripts
set PATH=%PATH%;%USERPROFILE%\AppData\Roaming\Python\Scripts
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python313\Scripts
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\Scripts
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311\Scripts
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python310\Scripts

python -m PyInstaller --clean --name "YouTube Mezat Yardimcisi" ^
            --onefile ^
            --windowed ^
            --icon=LOGO.png ^
            --add-data "LOGO.png;." ^
            --add-data "license_codes.json;." ^
            --add-data "settings.json;." ^
            --hidden-import customtkinter ^
            --hidden-import chat_downloader ^
            --hidden-import PIL ^
            mezaxx.py

echo Paketleme tamamlandi!
echo Programiniz "dist" klasorunde bulunuyor.
echo =====================================================

pause
