#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Profesyonel Paketleme Scripti
Müşteriler için hazır kurulum paketi oluşturur
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from pathlib import Path

# Paket bilgileri
PACKAGE_NAME = "YouTube_Mezat_Yardimcisi"
VERSION = "2.0"
AUTHOR = "Mezat Yazılım"

# Gerekli dosyalar
REQUIRED_FILES = [
    "mezaxx.py",
    "auto_installer.py", 
    "requirements.txt",
    "license_codes.json",
    "auth_data.json",
    "LOGO.png",
    "LICENSE.txt",
    "KURULUM_KILAVUZU.txt"
]

# Gerekli klasörler
REQUIRED_FOLDERS = [
    "sound",
    "sound/t_sound"
]

def create_clean_package():
    """Temiz bir kurulum paketi oluşturur"""
    print("🎯 YouTube Mezat Yardımcısı - Profesyonel Paketleme")
    print("=" * 60)
    
    # Paket klasörünü oluştur
    package_dir = f"{PACKAGE_NAME}_v{VERSION}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    print(f"📁 Paket klasörü oluşturuluyor: {package_dir}")
    
    # Ana dosyaları kopyala
    print("\n📋 Ana dosyalar kopyalanıyor...")
    for file in REQUIRED_FILES:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} bulunamadı!")
    
    # Ses klasörlerini kopyala
    print("\n🔊 Ses dosyaları kopyalanıyor...")
    for folder in REQUIRED_FOLDERS:
        if os.path.exists(folder):
            dest_folder = os.path.join(package_dir, folder)
            shutil.copytree(folder, dest_folder, dirs_exist_ok=True)
            print(f"  ✅ {folder}")
        else:
            print(f"  ⚠️ {folder} bulunamadı!")
    
    # Kurulum scripti oluştur
    create_installer_script(package_dir)
    
    # Ayarlar dosyası oluştur
    create_default_settings(package_dir)
    
    # README oluştur
    create_readme(package_dir)
    
    # Admin olarak çalıştırma scripti
    create_admin_runner(package_dir)
    
    return package_dir

def create_installer_script(package_dir):
    """Otomatik kurulum scripti oluşturur"""
    print("\n🛠️ Kurulum scripti oluşturuluyor...")
    
    installer_content = '''@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı - Kurulum
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║              YouTube Mezat Yardımcısı - Kurulum              ║
echo ║                        Versiyon 2.0                          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 📋 Kurulum başlatılıyor...
echo.

REM Python kontrolü
echo ⚙️ Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı! Lütfen önce Python yükleyin.
    echo 🔗 https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python bulundu!

REM Pip güncellemesi
echo.
echo 🔄 Pip güncelleniyor...
python -m pip install --upgrade pip --quiet

REM Modül yüklemesi
echo.
echo 📦 Gerekli modüller yükleniyor...
python auto_installer.py

REM Başarılı kurulum
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                    ✅ KURULUM TAMAMLANDI!                     ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Program çalıştırmak için: "YouTube_Mezat_Yardimcisi_BASLAT.bat"
echo.
pause
'''
    
    with open(os.path.join(package_dir, "KURULUM.bat"), "w", encoding="utf-8") as f:
        f.write(installer_content)
    print("  ✅ KURULUM.bat oluşturuldu")

def create_admin_runner(package_dir):
    """Admin olarak çalıştırma scripti oluşturur"""
    print("\n👑 Admin çalıştırma scripti oluşturuluyor...")
    
    runner_content = '''@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║              YouTube Mezat Yardımcısı Başlatılıyor           ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Admin kontrolü
net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Admin yetkileri gerekli! Yeniden başlatılıyor...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo 🚀 Program başlatılıyor...
echo.
python mezaxx.py

if errorlevel 1 (
    echo.
    echo ❌ Program hata ile kapandı!
    echo 💡 Sorun yaşıyorsanız KURULUM.bat dosyasını tekrar çalıştırın.
    echo.
    pause
)
'''
    
    with open(os.path.join(package_dir, "YouTube_Mezat_Yardimcisi_BASLAT.bat"), "w", encoding="utf-8") as f:
        f.write(runner_content)
    print("  ✅ YouTube_Mezat_Yardimcisi_BASLAT.bat oluşturuldu")

def create_default_settings(package_dir):
    """Varsayılan ayarlar dosyası oluşturur"""
    print("\n⚙️ Varsayılan ayarlar oluşturuluyor...")
    
    settings = {
        "language": "tr",
        "appearance_mode": "dark",
        "sounds_enabled": True,
        "sound_theme": "fight"
    }
    
    with open(os.path.join(package_dir, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    print("  ✅ settings.json oluşturuldu")

def create_readme(package_dir):
    """README dosyası oluşturur"""
    print("\n📄 README dosyası oluşturuluyor...")
    
    readme_content = """# YouTube Mezat Yardımcısı v2.0

## 🎯 Kurulum Talimatları

### 1. Gereksinimler
- Windows 10/11 (64-bit önerilen)
- Python 3.8 veya üzeri
- İnternet bağlantısı

### 2. Hızlı Kurulum
1. `KURULUM.bat` dosyasını **sağ tık → Yönetici olarak çalıştır**
2. Kurulum tamamlandığında `YouTube_Mezat_Yardimcisi_BASLAT.bat` ile programı başlatın

### 3. Manuel Kurulum
```bash
pip install -r requirements.txt
python mezaxx.py
```

## 🚀 Kullanım

1. **Program Başlatma**: `YouTube_Mezat_Yardimcisi_BASLAT.bat`
2. **YouTube URL Girme**: Canlı yayın URL'sini yapıştırın
3. **Chat Başlatma**: "Başlat" butonuna basın
4. **Mezat Kontrolü**: Ürün bilgilerini girin ve mezatı başlatın

## 🔧 Sorun Giderme

### Program açılmıyor?
- `KURULUM.bat` dosyasını yeniden çalıştırın
- Python'un doğru yüklendiğinden emin olun

### Chat bağlanmıyor?
- YouTube URL'sinin doğru olduğundan emin olun
- İnternet bağlantınızı kontrol edin
- Firewall/Antivirus ayarlarını kontrol edin

### Ses çalmıyor?
- Ses ayarlarından "Ses Efektleri" açık olduğundan emin olun
- `sound` klasörünün mevcut olduğunu kontrol edin

## 📞 Destek

Sorunlarınız için:
- Log dosyasını kontrol edin: `mezat.log`
- Hata mesajlarını not alın
- Destek ekibiyle iletişime geçin

## 📝 Sürüm Notları

### v2.0
- ✅ Basitleştirilmiş YouTube chat bağlantısı
- ✅ Geliştirilmiş hata yönetimi
- ✅ Daha hızlı bağlantı
- ✅ Otomatik kurulum sistemi

---
© 2024 Mezat Yazılım - Tüm hakları saklıdır.
"""
    
    with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("  ✅ README.md oluşturuldu")

def create_zip_package(package_dir):
    """ZIP paketi oluşturur"""
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

def main():
    """Ana fonksiyon"""
    try:
        print("🎯 YouTube Mezat Yardımcısı - Profesyonel Paketleme Başlatılıyor...")
        print("=" * 70)
        
        # Temiz paket oluştur
        package_dir = create_clean_package()
        
        # ZIP paketi oluştur
        zip_file = create_zip_package(package_dir)
        
        print("\n" + "=" * 70)
        print("🎉 PAKETLEME TAMAMLANDI!")
        print("=" * 70)
        print(f"📁 Klasör: {package_dir}")
        print(f"📦 ZIP: {zip_file}")
        print("\n📋 Müşterilerinize göndermek için:")
        print(f"  1. {zip_file} dosyasını gönderin")
        print("  2. Açtıktan sonra KURULUM.bat çalıştırmalarını söyleyin")
        print("  3. YouTube_Mezat_Yardimcisi_BASLAT.bat ile programı başlatacaklar")
        print("\n✅ Hazır! Müşterilerinize gönderebilirsiniz.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter tuşuna basın...")

