@echo off
echo YouTube Mezat Yardimcisi - Kurulum Sihirbazi Olusturma
echo =====================================================

REM NSIS kontrolü
where /q makensis.exe
if %ERRORLEVEL% NEQ 0 (
    echo NSIS (Nullsoft Scriptable Install System) bulunamadi!
    echo Lutfen NSIS'i indirin ve kurun: https://nsis.sourceforge.io/Download
    echo Kurduktan sonra makensis.exe'yi PATH'e ekleyin veya tam yolunu belirtin.
    goto ASK_PATH
) else (
    echo NSIS bulundu.
    goto CREATE_INSTALLER
)

:ASK_PATH
echo.
set /p nsis_path="NSIS kurulum dizinini girin (ornek: C:\Program Files (x86)\NSIS): "
if not exist "%nsis_path%\makensis.exe" (
    echo makensis.exe belirtilen dizinde bulunamadi!
    goto ASK_PATH
)
set PATH=%PATH%;%nsis_path%

:CREATE_INSTALLER
echo.
echo Kurulum sihirbazi olusturuluyor...
makensis installer.nsi

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Kurulum sihirbazi basariyla olusturuldu!
    echo YouTube_Mezat_Yardimcisi_Setup.exe dosyasi hazir.
    echo.
) else (
    echo.
    echo Kurulum sihirbazi olusturulurken hata olustu!
    echo Lutfen installer.nsi dosyasini ve hata mesajlarini kontrol edin.
    echo.
)

pause
