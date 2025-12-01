@echo off
setlocal

echo YouTube Mezat Yardimcisi - Dagitim Paketi Olusturucu
echo =====================================================

REM Dagitim klasoru olustur
set DIST_FOLDER=SETUP_YouTube_Mezat_Yardimcisi
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
echo ### SORUN GIDERME
echo.
echo Program acilmiyorsa:
echo - Antivirusunuz engelliyor olabilir, istisna ekleyin
echo - Program kaynaklari bloke edilmis olabilir, dosyalarin ozelliklerinden "Engellemeyi kaldir" secenegini isaretleyin
echo.
echo ### DESTEK
echo.
echo Sorun yasarsaniz:
echo - Programin icindeki iletisim ve destek seceneklerini kullanabilirsiniz
echo - WhatsApp veya E-posta araciligila destek alabilirsiniz
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
echo echo Program calistirmak icin masaustundeki kisayola tiklayabilirsiniz.
echo pause
) > "%DIST_FOLDER%\create_shortcut.bat"

REM Readme olustur
echo README.txt olusturuluyor...
(
echo ## YOUTUBE MEZAT YARDIMCISI
echo.
echo Kurulum icin:
echo 1. Tum dosyalari bilgisayarinizda bir klasore kopyalayin
echo 2. create_shortcut.bat dosyasini calistirarak masaustunde kisayol olusturun
echo 3. KURULUM_KILAVUZU.txt dosyasini okuyarak programi kullanmaya baslayabilirsiniz
) > "%DIST_FOLDER%\README.txt"

REM Zip dosyasi olustur
if exist powershell (
    echo Dagitim paketi zip olarak olusturuluyor...
    powershell -Command "Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%DIST_FOLDER%.zip' -Force"
    echo.
    echo Dagitim paketi olusturuldu: %DIST_FOLDER%.zip
) else (
    echo Dagitim klasoru olusturuldu: %DIST_FOLDER%
    echo Not: Zip dosyasi olusturulamadi. Lutfen klasor icerigini manuel olarak zip'leyin.
)

echo.
echo Islem tamamlandi!
echo =====================================================

pause
