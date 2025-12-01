#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - EXE Sürüm Oluşturucu
PyInstaller ile tek dosya EXE oluşturur
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_exe_version():
    """PyInstaller ile EXE sürümü oluşturur"""
    print("🎯 YouTube Mezat Yardımcısı - EXE Sürüm Oluşturucu")
    print("=" * 60)
    
    # PyInstaller kontrolü
    try:
        import PyInstaller
        print("✅ PyInstaller bulundu")
    except ImportError:
        print("📦 PyInstaller yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller yüklendi")
    
    # EXE klasörü oluştur
    exe_dir = "YouTube_Mezat_Yardimcisi_EXE_v2.0"
    if os.path.exists(exe_dir):
        shutil.rmtree(exe_dir)
    os.makedirs(exe_dir)
    
    print(f"📁 EXE klasörü oluşturuluyor: {exe_dir}")
    
    # PyInstaller komutu
    cmd = [
        "pyinstaller",
        "--onefile",                    # Tek dosya
        "--windowed",                   # Konsol penceresi yok
        "--name=YouTube_Mezat_Yardimcisi",
        "--icon=LOGO.png",              # İkon
        "--add-data=sound;sound",       # Ses dosyaları
        "--add-data=LOGO.png;.",        # Logo
        "--add-data=LICENSE.txt;.",     # Lisans
        "--hidden-import=chat_downloader",
        "--hidden-import=customtkinter",
        "--hidden-import=pygame",
        "--hidden-import=PIL",
        "--hidden-import=requests",
        "--hidden-import=beautifulsoup4",
        "--hidden-import=websocket",
        "mezaxx.py"
    ]
    
    print("🔨 EXE dosyası oluşturuluyor...")
    print("⏳ Bu işlem birkaç dakika sürebilir...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE dosyası başarıyla oluşturuldu!")
            
            # EXE dosyasını hedef klasöre kopyala
            exe_source = "dist/YouTube_Mezat_Yardimcisi.exe"
            exe_dest = f"{exe_dir}/YouTube_Mezat_Yardimcisi.exe"
            
            if os.path.exists(exe_source):
                shutil.copy2(exe_source, exe_dest)
                print(f"📁 EXE kopyalandı: {exe_dest}")
                
                # Dosya boyutunu kontrol et
                file_size = os.path.getsize(exe_dest) / (1024 * 1024)  # MB
                print(f"📊 EXE boyutu: {file_size:.1f} MB")
            else:
                print("❌ EXE dosyası bulunamadı!")
                return False
                
        else:
            print("❌ EXE oluşturma hatası!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False
    
    # Gerekli dosyaları kopyala
    print("\n📋 Ek dosyalar kopyalanıyor...")
    
    files_to_copy = [
        "auto_installer.py",
        "requirements.txt", 
        "license_codes.json",
        "auth_data.json",
        "KURULUM_KILAVUZU.txt",
        "LICENSE.txt",
        "LOGO.png"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, exe_dir)
            print(f"  ✅ {file}")
    
    # Ses klasörünü kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", f"{exe_dir}/sound", dirs_exist_ok=True)
        print("  ✅ sound klasörü")
    
    # EXE için özel kurulum scripti
    create_exe_installer(exe_dir)
    
    # EXE için başlatma scripti
    create_exe_launcher(exe_dir)
    
    # Temizlik
    cleanup_build_files()
    
    return exe_dir

def create_exe_installer(exe_dir):
    """EXE için kurulum scripti"""
    print("\n🛠️ EXE kurulum scripti oluşturuluyor...")
    
    installer_content = '''@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı - EXE Kurulum
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║            YouTube Mezat Yardımcısı - EXE Kurulum            ║
echo ║                        Versiyon 2.0                          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 📋 EXE kurulumu başlatılıyor...
echo.

REM Klasör oluştur
if not exist "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı" (
    mkdir "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı"
    echo ✅ Masaüstü klasörü oluşturuldu
)

REM Dosyaları kopyala
echo 📁 Dosyalar kopyalanıyor...
copy "YouTube_Mezat_Yardimcisi.exe" "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\"
copy "license_codes.json" "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\"
copy "LOGO.png" "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\"
copy "KURULUM_KILAVUZU.txt" "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\"
xcopy "sound" "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\sound\\" /E /I /Q

REM Masaüstü kısayolu oluştur
echo 🔗 Masaüstü kısayolu oluşturuluyor...
powershell -Command "\\
$WshShell = New-Object -comObject WScript.Shell; \\
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); \\
$Shortcut.TargetPath = '%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\YouTube_Mezat_Yardimcisi.exe'; \\
$Shortcut.WorkingDirectory = '%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı'; \\
$Shortcut.IconLocation = '%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı\\LOGO.png'; \\
$Shortcut.Save()"

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                    ✅ KURULUM TAMAMLANDI!                     ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Program masaüstündeki kısayoldan çalıştırılabilir
echo 📁 Dosyalar: %USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı
echo.
pause
'''
    
    with open(f"{exe_dir}/EXE_KURULUM.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    print("  ✅ EXE_KURULUM.bat oluşturuldu")

def create_exe_launcher(exe_dir):
    """EXE için başlatma scripti"""
    print("\n🚀 EXE başlatma scripti oluşturuluyor...")
    
    launcher_content = '''@echo off
title YouTube Mezat Yardımcısı
echo 🚀 YouTube Mezat Yardımcısı başlatılıyor...
start "" "YouTube_Mezat_Yardimcisi.exe"
'''
    
    with open(f"{exe_dir}/BASLAT.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    print("  ✅ BASLAT.bat oluşturuldu")

def cleanup_build_files():
    """Geçici dosyaları temizle"""
    print("\n🧹 Geçici dosyalar temizleniyor...")
    
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["YouTube_Mezat_Yardimcisi.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  🗑️ {dir_name} silindi")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"  🗑️ {file_name} silindi")

def create_exe_zip(exe_dir):
    """EXE paketi için ZIP oluştur"""
    print(f"\n📦 EXE ZIP paketi oluşturuluyor...")
    
    import zipfile
    
    zip_name = f"{exe_dir}.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(exe_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, os.path.dirname(exe_dir))
                zipf.write(file_path, arc_name)
    
    file_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"  ✅ {zip_name} oluşturuldu ({file_size:.1f} MB)")
    
    return zip_name

def main():
    """Ana fonksiyon"""
    try:
        print("🎯 YouTube Mezat Yardımcısı - EXE Sürüm Oluşturucu Başlatılıyor...")
        print("=" * 70)
        
        # EXE sürümü oluştur
        exe_dir = create_exe_version()
        
        if exe_dir:
            # ZIP paketi oluştur
            zip_file = create_exe_zip(exe_dir)
            
            print("\n" + "=" * 70)
            print("🎉 EXE SÜRÜMÜ TAMAMLANDI!")
            print("=" * 70)
            print(f"📁 Klasör: {exe_dir}")
            print(f"📦 ZIP: {zip_file}")
            print("\n📋 Müşterilerinize göndermek için:")
            print(f"  1. {zip_file} dosyasını gönderin")
            print("  2. Açtıktan sonra EXE_KURULUM.bat çalıştırmalarını söyleyin")
            print("  3. Masaüstündeki kısayoldan programı başlatacaklar")
            print("\n✅ EXE sürümü hazır! Müşterilerinize gönderebilirsiniz.")
        else:
            print("❌ EXE oluşturma başarısız!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter tuşuna basın...")

