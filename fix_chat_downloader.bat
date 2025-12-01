@echo off
setlocal

echo YouTube Mezat Yardimcisi - Chat Downloader Duzeltmesi
echo =====================================================

REM Python kurulum ve derleme
echo Gerekli modulleri yukluyor...
pip install pyinstaller chat-downloader websockets requests customtkinter pillow

echo PyInstaller ile paketleme islemi basliyor...

REM Ozellikle chat_downloader ile ilgili tum modulleri ekleyerek paketleme
python -m PyInstaller --clean --name "YouTube Mezat Yardimcisi" ^
            --onefile ^
            --windowed ^
            --icon=LOGO.png ^
            --add-data "LOGO.png;." ^
            --add-data "license_codes.json;." ^
            --add-data "license_usage.json;." ^
            --add-data "settings.json;." ^
            --add-data "auth_data.json;." ^
            --collect-all chat_downloader ^
            --hidden-import websockets ^
            --hidden-import websocket ^
            --hidden-import websocket-client ^
            --hidden-import requests ^
            --hidden-import customtkinter ^
            --hidden-import PIL ^
            --hidden-import chat_downloader ^
            --hidden-import chat_downloader.sites ^
            --hidden-import chat_downloader.sites.youtube ^
            --hidden-import chat_downloader.sites.common ^
            --hidden-import chat_downloader.utils ^
            --hidden-import chat_downloader.debugging ^
            mezaxx.py

echo.
echo Paketleme tamamlandi!
echo Programiniz "dist" klasorunde bulunuyor.
echo =====================================================

REM Derleme sonrası dosyaların tamamının kopyalanması
set DIST_FOLDER=SETUP_YouTube_Mezat_Yardimcisi_FIX
if exist %DIST_FOLDER% (
    rd /s /q %DIST_FOLDER%
)
mkdir %DIST_FOLDER%

REM Gerekli dosyaları kopyala
echo.
echo Dagitim dosyalari olusturuluyor...
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
echo ### YOUTUBE BAGLANTI SORUNU COZUMU
echo.
echo Chat'e baglanma sorunu yasiyorsaniz:
echo 1. Antivirusunuz uygulamanin internet erisimini engelliyor olabilir
echo 2. Windows guvenlik duvari YouTube Mezat Yardimcisi icin izin vermeniz gerekebilir
echo 3. Programi Yonetici olarak calistirmayi deneyin
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
echo ## YOUTUBE MEZAT YARDIMCISI
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
