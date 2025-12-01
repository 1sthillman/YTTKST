@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - Kurulum ve Paketleme Yardimcisi
echo =====================================================

REM Python kurulumunu kontrol et
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python bulunamadi! Lutfen Python 3.8 veya daha yeni bir surum yukleyin.
    echo https://www.python.org/downloads/ adresinden indirebilirsiniz.
    goto SON
)

REM Python versiyonunu kontrol et
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo Python Versiyonu: !python_version! tespit edildi.

REM Gerekli modullerin durumunu kontrol et
echo Gerekli moduller kontrol ediliyor...

python -c "import sys; exit(0 if int(sys.version_info[0]) >= 3 and int(sys.version_info[1]) >= 8 else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo Uyari: Python surumunuz 3.8'den dusuk. Bazi moduller calismayabilir.
)

echo 1/5: customtkinter kontrol ediliyor...
python -c "import customtkinter" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo customtkinter modulu bulunamadi. Yukleniyor...
    pip install customtkinter==5.2.0
)

echo 2/5: Pillow kontrol ediliyor...
python -c "from PIL import Image" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pillow modulu bulunamadi. Yukleniyor...
    pip install pillow==10.0.0
)

echo 3/5: requests kontrol ediliyor...
python -c "import requests" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo requests modulu bulunamadi. Yukleniyor...
    pip install requests==2.31.0
)

echo 4/5: chat_downloader kontrol ediliyor...
python -c "import chat_downloader" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo chat_downloader modulu bulunamadi. Yukleniyor...
    pip install chat-downloader==0.2.7
)

echo 5/5: PyInstaller kontrol ediliyor...
python -c "import PyInstaller" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller modulu bulunamadi. Yukleniyor...
    pip install pyinstaller==6.0.0
)

REM Windows için pywin32 kontrolü
if "%OS%"=="Windows_NT" (
    echo Windows için pywin32 kontrol ediliyor...
    python -c "import win32api" > nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo pywin32 modulu bulunamadi. Yukleniyor...
        pip install pywin32==306
    )
)

echo.
echo Tüm gerekli modüller kuruldu. Paketleme işlemine başlanabilir.
echo.

REM Farklı Python sürümleri için Script dizinlerini PATH'e ekle
FOR /D %%G IN ("%USERPROFILE%\AppData\Roaming\Python\Python*\Scripts") DO SET PATH=!PATH!;%%G
FOR /D %%G IN ("%LOCALAPPDATA%\Programs\Python\Python*\Scripts") DO SET PATH=!PATH!;%%G
set PATH=%PATH%;%USERPROFILE%\AppData\Roaming\Python\Scripts

:MENU
echo Ne yapmak istersiniz?
echo 1) PyInstaller ile paketleme işlemini başlat
echo 2) Çıkış
set /p secim="Seçiminizi yapın (1-2): "

if "%secim%"=="1" goto PAKETLEME
if "%secim%"=="2" goto SON
echo Geçersiz seçim. Lütfen tekrar deneyin.
goto MENU

:PAKETLEME
echo.
echo PyInstaller ile paketleme işlemi başlıyor...

REM PyInstaller'ın farklı çalıştırma yöntemlerini dene
echo 1. PyInstaller modülünü direkt çağırarak deniyorum...
python -m PyInstaller --clean mezatyardimcisi.spec
if %ERRORLEVEL% EQU 0 goto PAKET_BASARILI

echo 2. PyInstaller komutunu direkt deniyorum...
pyinstaller --clean mezatyardimcisi.spec
if %ERRORLEVEL% EQU 0 goto PAKET_BASARILI

echo 3. Python script dosyası olarak deniyorum...
for /f %%i in ('where pyinstaller') do set pyinstaller_path=%%i
if defined pyinstaller_path (
    python "!pyinstaller_path!" --clean mezatyardimcisi.spec
    if %ERRORLEVEL% EQU 0 goto PAKET_BASARILI
)

echo PyInstaller çalıştırılamadı. Lütfen manuel olarak yükleyin.
echo pip install pyinstaller komutunu çalıştırabilir ve tekrar deneyebilirsiniz.
goto PAKET_HATA

:PAKET_BASARILI
echo Paketleme tamamlandi!
echo Programiniz "dist" klasorunde bulunuyor.
echo =====================================================
goto SON

:PAKET_HATA
echo =====================================================
echo Hata: Paketleme işlemi tamamlanamadı!
echo Lütfen yukarıdaki hata mesajlarını kontrol edin.
echo =====================================================

:SON
pause
endlocal
