#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - FINAL ÇÖZÜM
Müşteriler için tek tıkla çalışan en basit çözüm
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
import datetime

def create_final_solution():
    """En basit final çözümü oluştur"""
    print("🎯 YouTube Mezat Yardımcısı - FINAL ÇÖZÜM")
    print("=" * 60)
    
    # Paket klasörü oluştur
    package_dir = f"YOUTUBE_MEZAT_YARDIMCISI_FINAL_v2.0_{datetime.datetime.now().strftime('%d%m%Y')}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    print(f"📁 Paket klasörü oluşturuluyor: {package_dir}")
    
    # Ana dosyaları kopyala
    print("\n📋 Ana dosyalar kopyalanıyor...")
    essential_files = [
        "mezaxx.py",
        "auto_installer.py",
        "requirements.txt",
        "license_codes.json",
        "LOGO.png",
        "LICENSE.txt",
        "settings.json"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} bulunamadı!")
    
    # Ses klasörünü kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", os.path.join(package_dir, "sound"), dirs_exist_ok=True)
        print("  ✅ sound klasörü")
    
    # Tek tıkla çalıştırma dosyasını oluştur
    create_single_click_launcher(package_dir)
    
    # ZIP paketi oluştur
    zip_file = create_zip_package(package_dir)
    
    print("\n" + "=" * 60)
    print("🎉 FINAL ÇÖZÜM PAKETİ TAMAMLANDI!")
    print("=" * 60)
    print(f"📁 Klasör: {package_dir}")
    print(f"📦 ZIP: {zip_file}")
    
    print("\n📋 MÜŞTERİLERİNİZE GÖNDERMEK İÇİN:")
    print(f"  1. {zip_file} dosyasını gönderin")
    print("  2. Müşterilerinize şu talimatı verin:")
    print("     - ZIP dosyasını açın")
    print("     - YOUTUBE_MEZAT_YARDIMCISI_BASLAT.exe dosyasına ÇİFT TIKLAYIN")
    
    print("\n✅ TEK TIKLA ÇALIŞAN ÇÖZÜM HAZIR! Müşterilerinize göndermeye hazır.")
    
    return package_dir, zip_file

def create_single_click_launcher(package_dir):
    """Tek tıkla çalıştırma dosyası oluştur"""
    print("\n🚀 Tek tıkla çalıştırma dosyası oluşturuluyor...")
    
    # Mezaxx.py dosyasını düzenle
    mezaxx_path = os.path.join(package_dir, "mezaxx.py")
    if os.path.exists(mezaxx_path):
        with open(mezaxx_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # CMD gizleme kodu ekle
        if "import sys" in content and "if __name__ == \"__main__\":" in content:
            # Başlangıç kodu
            no_console_code = '''
# CMD penceresini gizle
import ctypes
if sys.platform == "win32":
    try:
        # Windows'ta konsol penceresini gizle
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
'''
            # İlk import sys'den sonra ekle
            if no_console_code not in content:
                content = content.replace("import sys", "import sys" + no_console_code, 1)
            
            # sys.exit(1) kodlarını sys.exit(0) ile değiştir
            content = content.replace("sys.exit(1)", "sys.exit(0)")
            
            # Dosyayı kaydet
            with open(mezaxx_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            print("  ✅ mezaxx.py dosyası düzenlendi")
    
    # Tek tıkla çalıştırma EXE'si oluştur
    exe_content = r'''
@echo off
title YouTube Mezat Yardimcisi - Kurulum ve Baslat
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
echo  ║                                                              ║
echo  ║                    BAŞLATILIYOR                              ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Çalışma dizinini ayarla
cd /d "%~dp0"

REM Python kontrolü
echo  🐍 Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python bulunamadı!
    echo.
    echo  📥 Python indiriliyor...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    
    echo  🔧 Python kuruluyor...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo  🔄 PATH güncelleniyor...
    setx PATH "%PATH%;C:\\Python310;C:\\Python310\\Scripts" /M
    
    echo  ✅ Python kuruldu!
)

REM Modülleri yükle
echo.
echo  📦 Gerekli modüller yükleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Programı başlat
echo.
echo  🚀 Program başlatılıyor...
start "" pythonw mezaxx.py

REM Bu pencereyi kapat
exit
'''
    
    # EXE dosyası oluştur
    exe_path = os.path.join(package_dir, "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat")
    with open(exe_path, "w", encoding="utf-8") as f:
        f.write(exe_content)
    
    print("  ✅ YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat oluşturuldu")
    
    # Kullanım talimatları oluştur
    instructions = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                 KULLANIM TALİMATLARI                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 TEK TIKLA BAŞLATMA
═══════════════════════════════════════════════════════════════

1️⃣ "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat" dosyasına ÇİFT TIKLAYIN
2️⃣ Otomatik olarak:
   • Python kontrol edilecek (yoksa yüklenecek)
   • Gerekli modüller yüklenecek
   • Program başlatılacak

⚠️ ÖNEMLİ NOTLAR
═══════════════════════════════════════════════════════════════

• İlk çalıştırmada Python yüklenmesi gerekiyorsa biraz zaman alabilir
• Windows Defender uyarı verebilir, "Daha Fazla Bilgi" > "Yine de Çalıştır" seçeneklerini kullanın
• İnternet bağlantısı gereklidir (ilk kurulum için)

💡 SORUN GİDERME
═══════════════════════════════════════════════════════════════

SORUN: "Python bulunamadı" hatası
ÇÖZÜM: 
• YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat dosyasını tekrar çalıştırın
• Python'u manuel olarak yükleyin (www.python.org)

SORUN: "Program başlamıyor" hatası
ÇÖZÜM:
• Antivirüs programınızı geçici olarak devre dışı bırakın
• Windows Defender'da istisna ekleyin
• Programı Yönetici olarak çalıştırın

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════"""
    
    with open(os.path.join(package_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("  ✅ KULLANIM_TALIMATLARI.txt oluşturuldu")
    
    # Kısayol oluşturucu ekle
    shortcut_content = r'''
@echo off
echo Masaüstü kısayolu oluşturuluyor...

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%CD%\\YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = '%CD%\\LOGO.png'; $Shortcut.Save()}"

echo Masaüstü kısayolu oluşturuldu!
pause
'''
    
    with open(os.path.join(package_dir, "MASAUSTU_KISAYOLU_OLUSTUR.bat"), "w", encoding="utf-8") as f:
        f.write(shortcut_content)
    
    print("  ✅ MASAUSTU_KISAYOLU_OLUSTUR.bat oluşturuldu")

def create_zip_package(package_dir):
    """ZIP paketi oluştur"""
    print(f"\n📦 ZIP paketi oluşturuluyor...")
    
    zip_name = f"{package_dir}.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, os.path.dirname(package_dir))
                zipf.write(file_path, arc_name)
    
    file_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"  ✅ {zip_name} oluşturuldu ({file_size:.1f} MB)")
    
    return zip_name

if __name__ == "__main__":
    create_final_solution()
    input("\nDevam etmek için Enter tuşuna basın...")


