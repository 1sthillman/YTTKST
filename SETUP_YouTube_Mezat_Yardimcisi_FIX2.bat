@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - Gelismis Paketleme
echo =====================================================

REM Dagitim klasoru olustur
set DIST_FOLDER=SETUP_YouTube_Mezat_Yardimcisi_V2
if exist %DIST_FOLDER% (
    rd /s /q %DIST_FOLDER%
)
mkdir %DIST_FOLDER%

REM Gerekli dosyalari kopyala
echo Dosyalar kopyalaniyor...
copy "dist\YouTube Mezat Yardimcisi.exe" "%DIST_FOLDER%\"
copy "LOGO.png" "%DIST_FOLDER%\"
copy "LICENSE.txt" "%DIST_FOLDER%\"
copy "license_codes.json" "%DIST_FOLDER%\"
copy "settings.json" "%DIST_FOLDER%\"

REM Kurulum kilavuzu olustur
echo KURULUM_KILAVUZU.txt olusturuluyor...
(
echo ## YOUTUBE MEZAT YARDIMCISI - KURULUM KILAVUZU
echo.
echo Bu yazilim, YouTube canli yayinlarinda mezat duzenlemek icin gelistirilmis bir yardimci programdir.
echo.
echo ### KURULUM ADIMLARI
echo.
echo 1. YouTube Mezat Yardimcisi.exe dosyasina cift tiklayin.
echo 2. Ilk calistirmada kimlik dogrulama ekrani gorunecektir
echo 3. YouTube kanal URL'nizi ve size verilen lisans kodunu girin
echo.
echo ### YENILIKLER VE IYILESTIRMELER
echo.
echo Bu guncelleme ile chat mesajlari ve teklifler hakkinda onemli iyilestirmeler yapildi:
echo - Chat mesajlari artik daha hizli yuklenecek
echo - Fiyat x Adet formatlari icin iyilestirmeler yapildi (200x2, 200 x 2, 200*2, 200 * 2, 200X2)
echo - Chat mesajlari ekrandan kaybolma sorunu cozuldu
echo - Mezat durdurulduktan sonra eski chat mesajlarinin tekrar teklif olarak alinmasi engellendi
echo.
echo ### CHAT IPUCLARI
echo.
echo - Standart teklif formati: 200 TL (tek urun)
echo - Coklu urun formatlari: 
echo   * 200x2 (200 TL'den 2 adet)
echo   * 200 x 3 (200 TL'den 3 adet)
echo   * 200*5 (200 TL'den 5 adet)
echo   * 200 * 4 (200 TL'den 4 adet)
echo   * 200X10 (200 TL'den 10 adet)
echo.
echo ### SORUN GIDERME
echo.
echo Chat baglanma sorunu yasiyorsaniz:
echo - Programi Yonetici Olarak Calistir secenegiyle acin
echo - Windows Guvenlik Duvarinda uygulamaya izin verin
echo - Internete baglantiginizi kontrol edin
echo - Anti-virus yaziliminizi gecici olarak devre disi birakin
echo.
echo ### DESTEK
echo.
echo Sorun yasarsaniz:
echo - Programin icindeki iletisim ve destek seceneklerini kullanabilirsiniz
echo - WhatsApp veya E-posta araciligiyla destek alabilirsiniz
) > "%DIST_FOLDER%\KURULUM_KILAVUZU.txt"

REM Masaustu kisayol olusturucu
echo create_shortcut.bat olusturuluyor...
(
echo @echo off
echo echo YouTube Mezat Yardimcisi - Kisayol Olusturucu
echo echo =====================================================
echo.
echo set SCRIPT="%%TEMP%%\shortcut.vbs"
echo.
echo echo Set oWS = WScript.CreateObject^("WScript.Shell"^) ^> %%SCRIPT%%
echo echo sLinkFile = "%%USERPROFILE%%\Desktop\YouTube Mezat Yardimcisi.lnk" ^>^> %%SCRIPT%%
echo echo Set oLink = oWS.CreateShortcut^(sLinkFile^) ^>^> %%SCRIPT%%
echo echo oLink.TargetPath = "%%~dp0YouTube Mezat Yardimcisi.exe" ^>^> %%SCRIPT%%
echo echo oLink.WorkingDirectory = "%%~dp0" ^>^> %%SCRIPT%%
echo echo oLink.IconLocation = "%%~dp0LOGO.png" ^>^> %%SCRIPT%%
echo echo oLink.Save ^>^> %%SCRIPT%%
echo.
echo cscript //nologo %%SCRIPT%%
echo del %%SCRIPT%%
echo.
echo echo Masaustunde kisayol olusturuldu.
echo echo Program calistirmak icin masaustundeki kisayola sag tiklayip "Yonetici olarak calistir" secin.
echo pause
) > "%DIST_FOLDER%\create_shortcut.bat"

REM Admin olarak çalıştır
echo run_as_admin.bat olusturuluyor...
(
echo @echo off
echo echo YouTube Mezat Yardimcisi - Yonetici olarak calistir
echo echo =====================================================
echo.
echo set SCRIPT="%%TEMP%%\runadmin.vbs"
echo.
echo echo Set UAC = CreateObject^("Shell.Application"^) ^> %%SCRIPT%%
echo echo UAC.ShellExecute "%%~dp0YouTube Mezat Yardimcisi.exe", "", "", "runas", 1 ^>^> %%SCRIPT%%
echo.
echo cscript //nologo %%SCRIPT%%
echo del %%SCRIPT%%
) > "%DIST_FOLDER%\run_as_admin.bat"

REM Readme olustur
echo README.txt olusturuluyor...
(
echo ## YOUTUBE MEZAT YARDIMCISI V2
echo.
echo Bu yeni guncellemede chat mesajlari ve teklifler hakkinda onemli iyilestirmeler yapildi:
echo.
echo - Chat mesajlari artik daha hizli yuklenecek
echo - Fiyat x Adet formatlari icin iyilestirmeler yapildi: 200x2, 200 x 2, 200*2, 200 * 2, 200X2
echo - Chat mesajlari ekrandan kaybolma sorunu cozuldu
echo - Mezat durdurulduktan sonra eski chat mesajlarinin tekrar teklif olarak alinmasi engellendi
echo.
echo Kurulum icin:
echo 1. Tum dosyalari bilgisayarinizda bir klasore kopyalayin
echo 2. create_shortcut.bat dosyasini calistirarak masaustunde kisayol olusturun
echo 3. Uygulamayi Yonetici olarak calistirin (run_as_admin.bat ile)
echo.
echo Baglanti sorunu yasarsaniz:
echo - Antivirusu gecici olarak devre disi birakin
echo - Programi Yonetici olarak calistirin
echo - Windows Guvenlik Duvari'ndan programa izin verin
echo.
echo KURULUM_KILAVUZU.txt dosyasini okuyarak programi kullanmaya baslayabilirsiniz
) > "%DIST_FOLDER%\README.txt"

REM Zip dosyasi olustur
powershell -Command "Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%DIST_FOLDER%.zip' -Force"
echo.
echo Dagitim paketi olusturuldu: %DIST_FOLDER%.zip

echo.
echo Islem tamamlandi!
echo =====================================================

pause
