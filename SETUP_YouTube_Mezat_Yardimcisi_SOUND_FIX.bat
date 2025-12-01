@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - Dagitim Paketi Olusturucu (Ses Destekli Sürüm)
echo =====================================================

:: Temiz baslangic
if exist "SETUP_YouTube_Mezat_Yardimcisi_SOUND.zip" (
    del "SETUP_YouTube_Mezat_Yardimcisi_SOUND.zip"
)

:: Dagitim klasorunu kontrol et
if not exist "dist" (
    echo Hata: dist klasoru bulunamadi!
    goto :end
)

:: Gerekli dosyalarin varligini kontrol et
if not exist "dist\YouTube Mezat Yardimcisi.exe" (
    echo Hata: Executable dosya bulunamadi!
    goto :end
)

:: Gerekli dosyalari kopyala
echo Gerekli dosyalar kopyalaniyor...
if not exist "dist\LOGO.png" copy "LOGO.png" "dist\"
if not exist "dist\settings.json" copy "settings.json" "dist\"
if not exist "dist\license_codes.json" copy "license_codes.json" "dist\"
if not exist "dist\auth_data.json" copy "auth_data.json" "dist\"
if not exist "dist\license_usage.json" copy "license_usage.json" "dist\"

:: Ses dosyalarını kopyala
if not exist "dist\sound\" mkdir "dist\sound" 
xcopy /E /I /Y sound dist\sound

:: Yonetici olarak calistirma batch dosyasini olustur
echo @echo off > "dist\run_as_admin.bat"
echo echo YouTube Mezat Yardimcisi (Yonetici Modunda) >> "dist\run_as_admin.bat"
echo echo ===================================================== >> "dist\run_as_admin.bat"
echo powershell -Command "Start-Process 'YouTube Mezat Yardimcisi.exe' -Verb RunAs" >> "dist\run_as_admin.bat"
echo echo Program baslatildi! Bu pencereyi kapatabilirsiniz. >> "dist\run_as_admin.bat"
echo timeout /t 3 >> "dist\run_as_admin.bat"

:: Kurulum kilavuzu olustur
echo YOUTUBE MEZAT YARDIMCISI KURULUM KILAVUZU > "dist\KURULUM_KILAVUZU.txt"
echo ========================================= >> "dist\KURULUM_KILAVUZU.txt"
echo. >> "dist\KURULUM_KILAVUZU.txt"
echo BU PROGRAMI YONETICI OLARAK CALISTIRMALISINIZ! >> "dist\KURULUM_KILAVUZU.txt"
echo ----------------------------------------- >> "dist\KURULUM_KILAVUZU.txt"
echo. >> "dist\KURULUM_KILAVUZU.txt"
echo 1. Programi run_as_admin.bat dosyasina cift tiklayarak baslatiniz. >> "dist\KURULUM_KILAVUZU.txt"
echo 2. YouTube canli yayin URL'sini kopyalayin ve programda ilgili alana yapistirin. >> "dist\KURULUM_KILAVUZU.txt"
echo 3. Chat'i Baslat dugmesine tiklayin ve baglanti kurulmasini bekleyin. >> "dist\KURULUM_KILAVUZU.txt"
echo 4. Odeme yapan kullanicilari listeye eklemek icin chat mesajlarinin yanindaki + dugmesine tiklayin. >> "dist\KURULUM_KILAVUZU.txt"
echo 5. Ses efektleri icin ses klasoru programla ayni konumda olmalidir. >> "dist\KURULUM_KILAVUZU.txt"
echo. >> "dist\KURULUM_KILAVUZU.txt"
echo HATA GIDERME: >> "dist\KURULUM_KILAVUZU.txt"
echo - Programi MUTLAKA run_as_admin.bat ile yonetici olarak calistirin. >> "dist\KURULUM_KILAVUZU.txt"
echo - Firewall izni isterse IZIN VERIN. >> "dist\KURULUM_KILAVUZU.txt"
echo - Ses efektlerini ayarlar menusunden acip kapatabilirsiniz. >> "dist\KURULUM_KILAVUZU.txt"
echo - Canli yayin baglantisinda sorun yasarsaniz, programi yeniden baslatip tekrar deneyin. >> "dist\KURULUM_KILAVUZU.txt"

:: ZIP dosyasi olustur
echo Zip dosyasi olusturuluyor...
powershell -Command "Compress-Archive -Path 'dist\*' -DestinationPath 'SETUP_YouTube_Mezat_Yardimcisi_SOUND.zip' -Force"

if not exist "SETUP_YouTube_Mezat_Yardimcisi_SOUND.zip" (
    echo Hata: Zip dosyasi olusturulamadi!
    goto :end
)

echo Islem tamamlandi!
echo Dagitim paketi: SETUP_YouTube_Mezat_Yardimcisi_SOUND.zip

:end
echo =====================================================
pause
