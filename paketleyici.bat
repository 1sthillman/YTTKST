@echo off
setlocal enabledelayedexpansion
echo YouTube Mezat Yardimcisi - Dağıtılabilir Paket Oluşturucu
echo =====================================================

echo Gerekli modulleri yukluyor...
pip install -r requirements.txt

echo PyInstaller'i yüklüyor ve PATH'e ekliyor...
pip install pyinstaller==6.0.0

REM Farklı Python sürümleri için Script dizinlerini PATH'e ekle
FOR /D %%G IN ("%USERPROFILE%\AppData\Roaming\Python\Python*\Scripts") DO SET PATH=!PATH!;%%G
FOR /D %%G IN ("%LOCALAPPDATA%\Programs\Python\Python*\Scripts") DO SET PATH=!PATH!;%%G
set PATH=%PATH%;%USERPROFILE%\AppData\Roaming\Python\Scripts

echo PyInstaller ile paketleme islemi basliyor...

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
