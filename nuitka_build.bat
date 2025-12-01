@echo off
setlocal enabledelayedexpansion

echo YouTube Mezat Yardimcisi - Nuitka Derleme Baslatiyor
echo =====================================================

REM Python kontrolü
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python bulunamadi! Lutfen Python 3.8 veya daha yeni bir surum yukleyin.
    echo https://www.python.org/downloads/ adresinden indirebilirsiniz.
    goto SON
)

REM Nuitka build scriptini çalıştır
echo Python ile derleme betigini calistiriyorum...
python nuitka_build.py

if %ERRORLEVEL% EQU 0 (
    echo =====================================================
    echo Derleme islemi tamamlandi.
    echo YouTube Mezat Yardimcisi.exe dosyasi olusturuldu.
    echo =====================================================
) else (
    echo =====================================================
    echo Derleme islemi sirasinda hata olustu!
    echo Yukaridaki hata mesajlarini kontrol ediniz.
    echo =====================================================
)

:SON
pause
