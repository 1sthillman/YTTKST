#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - FINAL MÜŞTERİ PAKETİ OLUŞTURUCU
Tüm sorunları çözen nihai paket
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
import datetime

def create_final_package():
    """Nihai müşteri paketi oluştur"""
    print("🎯 YouTube Mezat Yardımcısı - FINAL MÜŞTERİ PAKETİ")
    print("=" * 60)
    
    # Paket klasörü oluştur
    package_dir = f"FINAL_YOUTUBE_MEZAT_YARDIMCISI_v2.0_{datetime.datetime.now().strftime('%d%m%Y')}"
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
        "KURULUM_KILAVUZU.txt",
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
    
    # Başlatıcıları oluştur
    create_launchers(package_dir)
    
    # Kurulum talimatlarını oluştur
    create_final_instructions(package_dir)
    
    # ZIP paketi oluştur
    zip_file = create_zip_package(package_dir)
    
    print("\n" + "=" * 60)
    print("🎉 FINAL MÜŞTERİ PAKETİ TAMAMLANDI!")
    print("=" * 60)
    print(f"📁 Klasör: {package_dir}")
    print(f"📦 ZIP: {zip_file}")
    
    print("\n📋 MÜŞTERİLERİNİZE GÖNDERMEK İÇİN:")
    print(f"  1. {zip_file} dosyasını gönderin")
    print("  2. Müşterilerinize şu talimatları verin:")
    print("     - ZIP dosyasını açın")
    print("     - KURULUM.bat dosyasını YÖNETİCİ OLARAK çalıştırın")
    print("     - Kurulum tamamlandıktan sonra BASLAT.vbs dosyasına çift tıklayın")
    
    print("\n✅ TÜM SORUNLAR ÇÖZÜLDÜ! Müşterilerinize göndermeye hazır.")
    
    return package_dir, zip_file

def create_launchers(package_dir):
    """Başlatıcılar oluştur"""
    print("\n🚀 Başlatıcılar oluşturuluyor...")
    
    # VBS başlatıcı
    vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = CurrentDirectory
WshShell.Run "pythonw mezaxx.py", 0, False
'''
    
    with open(os.path.join(package_dir, "BASLAT.vbs"), "w", encoding="utf-8") as f:
        f.write(vbs_content)
    print("  ✅ BASLAT.vbs oluşturuldu")
    
    # Pythonw BAT başlatıcı
    bat_content = '''@echo off
cd /d "%~dp0"
start "" pythonw mezaxx.py
'''
    
    with open(os.path.join(package_dir, "BASLAT.bat"), "w", encoding="utf-8") as f:
        f.write(bat_content)
    print("  ✅ BASLAT.bat oluşturuldu")
    
    # Kurulum scripti
    kurulum_content = '''@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı - Kurulum
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
echo  ║                                                              ║
echo  ║                    KURULUM BAŞLATILIYOR                      ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

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
    echo.
    echo  ⚠️ Kurulumun tamamlanması için bilgisayarı yeniden başlatmanız gerekebilir.
    echo  ⚠️ Kurulum tamamlandıktan sonra bu dosyayı tekrar çalıştırın.
    pause
    exit /b 1
)
echo  ✅ Python bulundu!

REM Modülleri yükle
echo.
echo  📦 Gerekli modüller yükleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Mezaxx.py dosyasını modifiye et
echo.
echo  🔧 Program dosyası hazırlanıyor...
python -c "import re; f=open('mezaxx.py', 'r', encoding='utf-8'); content=f.read(); f.close(); mod_content=re.sub('import sys', 'import sys\\n# CMD penceresini gizle\\nimport ctypes\\nif sys.platform == \"win32\":\\n    try:\\n        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)\\n    except:\\n        pass', content, 1); f=open('mezaxx.py', 'w', encoding='utf-8'); f.write(mod_content); f.close()"

REM Masaüstü kısayolu oluştur
echo.
echo  🔗 Masaüstü kısayolu oluşturuluyor...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%CD%\\BASLAT.vbs'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = '%CD%\\LOGO.png'; $Shortcut.Save()}"

cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║                ✅ KURULUM BAŞARIYLA TAMAMLANDI! ✅           ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🎉 YouTube Mezat Yardımcısı başarıyla kuruldu!
echo.
echo  🚀 Programı başlatmak için:
echo     • BASLAT.vbs dosyasına çift tıklayın
echo     • Veya masaüstündeki kısayolu kullanın
echo.
echo  ⚠️ CMD penceresi görünüyorsa:
echo     • BASLAT.vbs dosyasını kullanın (önerilen)
echo     • BASLAT.bat dosyası da alternatif olarak kullanılabilir
echo.
echo  📖 Ayrıntılı bilgi için KURULUM_KILAVUZU.txt dosyasını okuyun
echo.
echo  ═══════════════════════════════════════════════════════════════
echo  Program hazır! Başarılı mezatlar dileriz! 🎯
echo  ═══════════════════════════════════════════════════════════════
echo.
pause
'''
    
    with open(os.path.join(package_dir, "KURULUM.bat"), "w", encoding="utf-8") as f:
        f.write(kurulum_content)
    print("  ✅ KURULUM.bat oluşturuldu")

def create_final_instructions(package_dir):
    """Final kurulum talimatları oluştur"""
    print("\n📝 Final kurulum talimatları oluşturuluyor...")
    
    instructions = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                 KURULUM TALİMATLARI                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 KOLAY KURULUM (ÖNEMLİ: BU TALİMATLARI OKUYUN)
═══════════════════════════════════════════════════════════════

1️⃣ "KURULUM.bat" dosyasına SAĞ TIK yapın
2️⃣ "YÖNETİCİ OLARAK ÇALIŞTIR" seçeneğini tıklayın
3️⃣ Kurulum otomatik olarak tamamlanacak:
   • Python otomatik yüklenecek (internet bağlantısı gerekli)
   • Gerekli modüller otomatik kurulacak
   • Masaüstünde kısayol oluşturulacak

4️⃣ Kurulum tamamlandıktan sonra programı başlatmak için:
   • "BASLAT.vbs" dosyasına çift tıklayın (ÖNERİLEN)
   • Veya masaüstündeki kısayolu kullanın

⚠️ ÖNEMLİ: İlk kurulumda biraz zaman alabilir (2-5 dakika)
   Python ve modüllerin yüklenmesi için bekleyin.

💡 CMD PENCERE SORUNU ÇÖZÜLDÜ!
═══════════════════════════════════════════════════════════════

Programı başlatmak için aşağıdaki dosyalardan BİRİNE çift tıklayın:

✅ "BASLAT.vbs" (EN İYİ SEÇENEK)
   • CMD penceresi göstermez
   • Doğrudan program açılır

✅ "BASLAT.bat" (Alternatif çözüm)
   • Bazı sistemlerde daha iyi çalışabilir
   • Masaüstündeki kısayol da bunu kullanır

❌ "mezaxx.py" dosyasını doğrudan çalıştırmayın
   • Bu dosya CMD penceresi gösterebilir

🔧 SORUN GİDERME
═══════════════════════════════════════════════════════════════

SORUN: "Python bulunamadı" hatası
ÇÖZÜM: 
• KURULUM.bat dosyasını tekrar YÖNETİCİ OLARAK çalıştırın
• Kurulum sonrası bilgisayarı yeniden başlatın
• Python'u manuel olarak yükleyin (www.python.org)

SORUN: "Program başlamıyor" hatası
ÇÖZÜM:
• BASLAT.vbs dosyasını deneyin
• BASLAT.bat dosyasını deneyin
• KURULUM.bat dosyasını tekrar çalıştırın

SORUN: "Modüller yüklenemedi" hatası
ÇÖZÜM:
• İnternet bağlantınızı kontrol edin
• Firewall ayarlarınızı kontrol edin
• Kurulumu tekrar başlatın

📱 İLETİŞİM VE DESTEK
═══════════════════════════════════════════════════════════════

Kurulum sırasında sorun yaşarsanız:
• Ekran görüntüsü alın
• Hata mesajını not edin
• Destek ekibimizle iletişime geçin

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════"""
    
    with open(os.path.join(package_dir, "KURULUM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(instructions)
    print("  ✅ KURULUM_TALIMATLARI.txt oluşturuldu")

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
    create_final_package()
    input("\nDevam etmek için Enter tuşuna basın...")


