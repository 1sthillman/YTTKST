@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - Gelismis Baglanti Surumu
echo =====================================================

REM Dagitim klasoru olustur
set DIST_FOLDER=SETUP_YouTube_Mezat_Yardimcisi_V3
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
echo 1. YouTube Mezat Yardimcisi.exe dosyasina SAG TIK yapip "Yonetici olarak calistir" secenegini secin.
echo 2. Ilk calistirmada kimlik dogrulama ekrani gorunecektir
echo 3. YouTube kanal URL'nizi ve size verilen lisans kodunu girin
echo.
echo ### BAGLANTI SORUNU COZULDU
echo.
echo Bu guncelleme ile YouTube canli yayin baglanti sorunlari tamamen cozuldu:
echo - YouTube API'ya daha dogru bir sekilde baglanma
echo - 10 farkli baglanti denemesi ve otomatik yeniden baglanti
echo - Video ID formatini otomatik duzeltme
echo - Fiyat x Adet formatlari icin destekler (200x2, 200*2, 200X2)
echo - Chat mesajlari ekrandan kaybolma sorunu cozuldu
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
echo ### ONEMLI UYARILAR
echo.
echo 1. MUTLAKA YONETICI OLARAK CALISTIRIN!
echo    - Programi SAG TIK yapip "Yonetici olarak calistir" secenegini secin veya
echo    - run_as_admin.bat dosyasini kullanin
echo.  
echo 2. BAGLANTI HALA OLMAZSA:
echo    - Windows Guvenlik Duvarini gecici olarak kapatin veya uygulamaya izin verin
echo    - Anti-virus yaziliminizi gecici olarak devre disi birakin
echo    - Internete baglantiginizi kontrol edin
echo    - Farkli bir internet baglantisi deneyin (Wi-Fi yerine mobil baglantiyi deneyin)
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
echo echo ONEMLI: Program calistirmak icin masaustundeki kisayola sag tiklayip "Yonetici olarak calistir" secin.
echo pause
) > "%DIST_FOLDER%\create_shortcut.bat"

REM Admin olarak çalıştır
echo run_as_admin.bat olusturuluyor...
(
echo @echo off
echo echo YouTube Mezat Yardimcisi - Yonetici olarak calistir
echo echo =====================================================
echo.
echo echo ONEMLI: Program Yonetici olarak baslatiliyor...
echo echo Internet baglantisi icin bu gereklidir.
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
echo ## YOUTUBE MEZAT YARDIMCISI V3 - GELISMIS BAGLANTI SURUMU
echo.
echo Bu yeni guncellemede YouTube canli yayin baglanti sorunlari tamamen cozuldu:
echo.
echo - YouTube API'ya daha dogru bir sekilde baglanma
echo - 10 farkli baglanti denemesi ve otomatik yeniden baglanti
echo - Video ID formatini otomatik duzeltme
echo - Teklif formatlari iyilestirildi: 200x2, 200*2, 200X2
echo - Chat mesajlari ekrandan kaybolma sorunu cozuldu
echo.
echo ONEMLI KULLANIM BILGILERI:
echo.
echo 1. MUTLAKA YONETICI OLARAK CALISTIRIN!
echo    - Programi SAG TIK yapip "Yonetici olarak calistir" secenegini secin veya
echo    - run_as_admin.bat dosyasini kullanin
echo.
echo 2. Kurulum icin:
echo    - Tum dosyalari bilgisayarinizda bir klasore kopyalayin
echo    - create_shortcut.bat dosyasini calistirarak masaustunde kisayol olusturun
echo    - run_as_admin.bat ile programi yonetici olarak calistirin
echo.
echo 3. Baglanti sorunu yasarsaniz:
echo    - Windows Guvenlik Duvarini gecici olarak kapatin
echo    - Anti-virus yaziliminizi gecici olarak devre disi birakin
echo    - Farkli bir internet baglantisi deneyin
echo.
echo KURULUM_KILAVUZU.txt dosyasinda daha fazla bilgi bulabilirsiniz.
) > "%DIST_FOLDER%\README.txt"

REM Zip dosyasi olustur
powershell -Command "Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%DIST_FOLDER%.zip' -Force"
echo.
echo Dagitim paketi olusturuldu: %DIST_FOLDER%.zip

echo.
echo Islem tamamlandi!
echo =====================================================

pause
