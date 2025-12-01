@echo off
echo YouTube Mezat Yardimcisi - Dagitim Paketi Olusturucu (Ses Tema Destekli Surum)
echo =====================================================
echo Gerekli dosyalar kopyalaniyor...

:: Sound klasörünü kopyala
xcopy /E /I /Y sound dist\sound

:: ZIP dosyası oluştur
echo Zip dosyasi olusturuluyor...
powershell -Command "Compress-Archive -Path 'dist\*' -DestinationPath 'SETUP_YouTube_Mezat_Yardimcisi_SOUND_THEME.zip' -Force"

echo Islem tamamlandi
echo Dagitim paketi: SETUP_YouTube_Mezat_Yardimcisi_SOUND_THEME.zip
echo =====================================================
pause
