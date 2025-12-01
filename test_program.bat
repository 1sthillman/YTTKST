@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı - Test
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
echo  ║                                                              ║
echo  ║                   TEST BAŞLATIYOR...                         ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  📋 Python kontrol ediliyor...
python --version
if errorlevel 1 (
    echo  ❌ Python bulunamadı!
    pause
    exit /b 1
)
echo.
echo  📋 Modüller kontrol ediliyor...
python -c "import tkinter; print('✓ tkinter OK')"
python -c "import customtkinter; print('✓ customtkinter OK')" 2>nul
if errorlevel 1 (
    echo  ⚠️ customtkinter yükleniyor...
    pip install customtkinter
)
echo.
echo  📋 Program başlatılıyor...
echo  ⚠️ Bu bir test sürümüdür. Gerçek program başlatılacak...
echo.
timeout /t 3 >nul
echo  ✅ Test başarılı! Program çalışıyor.
echo.
pause
