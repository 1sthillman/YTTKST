@echo off
echo YouTube Mezat Yardimcisi - Kurulum Sihirbazi
echo =====================================================

echo Kurulum baslıyor...

echo Gereken dosyalari kontrol ediyorum...

if not exist "dist\YouTube Mezat Yardimcisi.exe" (
    echo Hata: Uygulama bulunamadı!
    echo Lutfen once paketleyici.bat dosyasini calistirarak uygulamayı paketleyin.
    pause
    exit
)

echo Uygulamanizi kurulum dizinine kopyalıyorum...

set /p hedef="Lutfen kurulum dizinini belirtin (Ornek: C:\YouTube Mezat Yardimcisi): "

if not exist "%hedef%" (
    echo Dizin olusturuluyor: %hedef%
    mkdir "%hedef%"
)

echo Dosyalar kopyalaniyor...
xcopy "dist\YouTube Mezat Yardimcisi.exe" "%hedef%\" /Y
xcopy "LOGO.png" "%hedef%\" /Y
xcopy "LICENSE.txt" "%hedef%\" /Y
xcopy "license_codes.json" "%hedef%\" /Y
xcopy "settings.json" "%hedef%\" /Y
if exist "license_usage.json" xcopy "license_usage.json" "%hedef%\" /Y
if exist "auth_data.json" xcopy "auth_data.json" "%hedef%\" /Y
if exist "paid_users.json" xcopy "paid_users.json" "%hedef%\" /Y

echo Masaüstü kısayolu oluşturuluyor...
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\YouTube Mezat Yardimcisi.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%hedef%\YouTube Mezat Yardimcisi.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "%hedef%" >> %SCRIPT%
echo oLink.IconLocation = "%hedef%\LOGO.png" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo Kurulum tamamlandi!
echo =====================================================
echo Program basariyla "%hedef%" dizinine kuruldu.
echo Masaustunde kisayol oluşturuldu.
echo Programi calistirmak icin masaustundeki kisayola tiklayabilirsiniz.
echo =====================================================

pause
