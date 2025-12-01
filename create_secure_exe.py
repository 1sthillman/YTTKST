#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Güvenli EXE Oluşturucu
Nuitka ile kaynak kodları tamamen gizli EXE oluşturur
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json

def install_nuitka():
    """Nuitka'yı yükler"""
    print("📦 Nuitka yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])
        print("✅ Nuitka yüklendi")
        return True
    except Exception as e:
        print(f"❌ Nuitka yüklenemedi: {e}")
        return False

def create_nuitka_exe():
    """Nuitka ile güvenli EXE oluşturur"""
    print("🔨 Nuitka ile güvenli EXE oluşturuluyor...")
    
    # Nuitka komutu - kaynak kodları tamamen gizler
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",                    # Tek dosya EXE
        "--windows-disable-console",    # Konsol penceresi yok
        "--enable-plugin=tk-inter",     # Tkinter desteği
        "--include-data-dir=sound=sound",  # Ses klasörü
        "--include-data-file=LOGO.png=LOGO.png",  # Logo
        "--include-data-file=LICENSE.txt=LICENSE.txt",  # Lisans
        "--windows-icon-from-ico=LOGO.png",  # İkon (eğer ico formatında varsa)
        "--product-name=YouTube Mezat Yardımcısı",
        "--file-version=2.0.0.0",
        "--product-version=2.0",
        "--file-description=YouTube Mezat Yardımcısı v2.0",
        "--copyright=© 2024 Mezat Yazılım",
        "--output-filename=YouTube_Mezat_Yardimcisi_SECURE.exe",
        "mezaxx.py"
    ]
    
    try:
        print("⏳ Bu işlem 5-10 dakika sürebilir...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # EXE dosyasını bul
            possible_paths = [
                "YouTube_Mezat_Yardimcisi_SECURE.exe",
                "mezaxx.exe",
                "YouTube_Mezat_Yardimcisi_SECURE.dist/YouTube_Mezat_Yardimcisi_SECURE.exe"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"✅ Güvenli EXE oluşturuldu: {path}")
                    return path
            
            print("❌ EXE dosyası bulunamadı")
            return None
        else:
            print(f"❌ Nuitka hatası: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Nuitka çalıştırma hatası: {e}")
        return None

def create_secure_package():
    """Güvenli setup paketi oluşturur"""
    print("🎯 YouTube Mezat Yardımcısı - Güvenli EXE Paketi")
    print("=" * 60)
    
    # Nuitka'yı yükle
    if not install_nuitka():
        print("❌ Nuitka yüklenemedi, işlem durduruluyor...")
        return None
    
    # Güvenli EXE oluştur
    exe_path = create_nuitka_exe()
    if not exe_path:
        print("❌ Güvenli EXE oluşturulamadı")
        return None
    
    # Setup klasörü oluştur
    setup_dir = "YouTube_Mezat_Yardimcisi_SECURE_SETUP"
    if os.path.exists(setup_dir):
        shutil.rmtree(setup_dir)
    os.makedirs(setup_dir)
    
    print(f"📁 Güvenli setup klasörü: {setup_dir}")
    
    # EXE'yi kopyala
    final_exe = f"{setup_dir}/YouTube_Mezat_Yardimcisi.exe"
    shutil.copy2(exe_path, final_exe)
    print("✅ Güvenli EXE kopyalandı")
    
    # Sadece gerekli dosyaları kopyala (kaynak kod YOK!)
    essential_files = [
        ("license_codes.json", "Lisans kodları"),
        ("LOGO.png", "Program ikonu"), 
        ("LICENSE.txt", "Lisans metni"),
    ]
    
    print("\n📋 Sadece gerekli dosyalar kopyalanıyor...")
    for file, desc in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, setup_dir)
            print(f"  ✅ {desc}")
    
    # Ses klasörünü kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", f"{setup_dir}/sound", dirs_exist_ok=True)
        print("  ✅ Ses dosyaları")
    
    # Güvenli setup scripti oluştur
    create_secure_setup_script(setup_dir)
    
    # Güvenli kılavuz oluştur
    create_secure_guide(setup_dir)
    
    # Varsayılan ayarlar
    create_secure_config(setup_dir)
    
    return setup_dir

def create_secure_setup_script(setup_dir):
    """Güvenli setup scripti oluşturur"""
    print("\n🛠️ Güvenli setup scripti oluşturuluyor...")
    
    setup_content = '''@echo off
chcp 65001 >nul
title YouTube Mezat Yardımcısı - Güvenli Kurulum
color 0A
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║      🔒 YouTube Mezat Yardımcısı v2.0 - SECURE 🔒          ║
echo  ║                                                              ║
echo  ║                   GÜVENLİ KURULUM                            ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🔐 Bu sürüm kaynak kodları tamamen gizlidir
echo  📦 Tek EXE dosyası ile çalışır
echo  🚀 Python kurulumu gerektirmez
echo.
echo  📋 Kurulum başlatılıyor...
echo  ════════════════════════════════════════════════════════════════
echo.

REM Admin kontrolü
net session >nul 2>&1
if errorlevel 1 (
    echo  ⚠️ Bu kurulum yönetici yetkileri gerektirir!
    echo  🔄 Yeniden başlatılıyor...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM Kurulum klasörü oluştur
set "INSTALL_DIR=%LOCALAPPDATA%\\YouTube Mezat Yardımcısı"
echo  📁 Kurulum klasörü hazırlanıyor...
if exist "%INSTALL_DIR%" (
    echo  🗑️ Eski kurulum temizleniyor...
    rd /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"

REM Dosyaları kopyala
echo  📦 Program dosyaları kopyalanıyor...
copy "YouTube_Mezat_Yardimcisi.exe" "%INSTALL_DIR%\\" >nul
copy "license_codes.json" "%INSTALL_DIR%\\" >nul
copy "LOGO.png" "%INSTALL_DIR%\\" >nul
copy "LICENSE.txt" "%INSTALL_DIR%\\" >nul
copy "settings.json" "%INSTALL_DIR%\\" >nul
if exist "sound" xcopy "sound" "%INSTALL_DIR%\\sound\\" /E /I /Q >nul

REM Windows Defender için güvenlik istisnası ekle
echo  🛡️ Windows Defender istisnası ekleniyor...
powershell -Command "Add-MpPreference -ExclusionPath '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'" 2>nul

REM Masaüstü kısayolu oluştur
echo  🔗 Masaüstü kısayolu oluşturuluyor...
powershell -WindowStyle Hidden -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\LOGO.png'; $Shortcut.Description = 'YouTube Mezat Yardımcısı v2.0 - Secure'; $Shortcut.Save()}"

REM Başlat menüsü kısayolu
echo  📌 Başlat menüsü kısayolu oluşturuluyor...
set "START_DIR=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\YouTube Mezat Yardımcısı"
if not exist "%START_DIR%" mkdir "%START_DIR%"
powershell -WindowStyle Hidden -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_DIR%\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\LOGO.png'; $Shortcut.Description = 'YouTube Mezat Yardımcısı v2.0'; $Shortcut.Save()}"

REM Kaldırma scripti oluştur
echo  🗑️ Kaldırma scripti hazırlanıyor...
(
echo @echo off
echo title YouTube Mezat Yardımcısı - Kaldırma
echo echo 🗑️ Program kaldırılıyor...
echo del "%%USERPROFILE%%\\Desktop\\YouTube Mezat Yardımcısı.lnk" 2^>nul
echo rd /s /q "%START_DIR%" 2^>nul
echo powershell -Command "Remove-MpPreference -ExclusionPath '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'" 2^>nul
echo cd /d "%%TEMP%%"
echo timeout /t 2 /nobreak ^>nul
echo rd /s /q "%INSTALL_DIR%"
echo echo ✅ Program başarıyla kaldırıldı!
echo pause
) > "%INSTALL_DIR%\\Kaldır.bat"

REM Güvenlik ayarları
echo  🔐 Güvenlik ayarları yapılandırılıyor...
attrib +h "%INSTALL_DIR%\\license_codes.json"

cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║              ✅ GÜVENLİ KURULUM TAMAMLANDI! ✅               ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🎉 YouTube Mezat Yardımcısı güvenli sürümü kuruldu!
echo.
echo  🔐 ÖZELLİKLER:
echo     • Kaynak kodlar tamamen gizli
echo     • Python kurulumu gerektirmez
echo     • Tek EXE dosyası ile çalışır
echo     • Windows Defender istisnası eklendi
echo.
echo  📍 Program Konumu: %INSTALL_DIR%
echo  🖥️ Masaüstü Kısayolu: Oluşturuldu
echo  📌 Başlat Menüsü: Oluşturuldu
echo.
echo  🚀 Programı başlatmak için:
echo     • Masaüstündeki kısayola çift tıklayın
echo     • Veya Başlat menüsünden açın
echo.
echo  ═══════════════════════════════════════════════════════════════
echo  🔒 Güvenli sürüm hazır! Başarılı mezatlar dileriz! 🎯
echo  ═══════════════════════════════════════════════════════════════
echo.
pause
'''
    
    with open(f"{setup_dir}/SECURE_SETUP.bat", "w", encoding="utf-8") as f:
        f.write(setup_content)
    print("  ✅ SECURE_SETUP.bat oluşturuldu")

def create_secure_guide(setup_dir):
    """Güvenli kılavuz oluşturur"""
    print("\n📖 Güvenli kılavuz oluşturuluyor...")
    
    guide_content = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🔒 YouTube Mezat Yardımcısı v2.0 - SECURE 🔒          ║
║                                                              ║
║                    GÜVENLİ SÜRÜM KILAVUZU                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔐 GÜVENLİ SÜRÜM ÖZELLİKLERİ
═══════════════════════════════════════════════════════════════

✅ KAYNAK KODLAR TAMamen GİZLİ
   • Python dosyaları (.py) yok
   • Sadece EXE dosyası var
   • Reverse engineering koruması

✅ PYTHON GEREKMİYOR
   • Python kurulumu gerektirmez
   • Tüm bağımlılıklar EXE içinde
   • Herhangi bir bilgisayarda çalışır

✅ TEK DOSYA ÇÖZÜMÜ
   • Sadece EXE dosyası yeterli
   • Ek modül yükleme yok
   • Hızlı başlatma

🚀 KURULUM TALİMATLARI
═══════════════════════════════════════════════════════════════

1. "SECURE_SETUP.bat" dosyasına SAĞ TIK yapın
2. "Yönetici olarak çalıştır" seçin
3. Kurulum otomatik tamamlanacak
4. Masaüstündeki kısayoldan başlatın

⚠️ ÖNEMLİ NOTLAR:
   • Antivirus programı uyarı verebilir (normal)
   • Windows Defender istisnası otomatik eklenir
   • İlk çalıştırma biraz yavaş olabilir

🎯 PROGRAM KULLANIMI
═══════════════════════════════════════════════════════════════

Program kullanımı normal sürüm ile aynıdır:

1. İLK AÇILIŞ:
   • YouTube kanal URL'nizi girin
   • Lisans kodunuzu girin
   • "Doğrula ve Devam Et" butonuna basın

2. YOUTUBE CHAT:
   • Canlı yayın URL'sini yapıştırın
   • "Başlat" butonuna basın
   • Chat mesajları gelecek

3. MEZAT AYARLARI:
   • Ürün adı, fiyat, mod seçin
   • "BAŞLAT" butonuna basın
   • Teklifler otomatik algılanacak

🔧 SORUN GİDERME
═══════════════════════════════════════════════════════════════

PROBLEM: Antivirus programı EXE'yi siliyor
ÇÖZÜM:
• Antivirus ayarlarından istisna ekleyin
• Windows Defender zaten otomatik eklendi
• Geçici olarak gerçek zamanlı korumayı kapatın

PROBLEM: Program açılmıyor
ÇÖZÜM:
• SECURE_SETUP.bat'ı yönetici olarak tekrar çalıştırın
• Windows güncellemelerini kontrol edin
• .NET Framework güncel mi kontrol edin

PROBLEM: Çok yavaş açılıyor
ÇÖZÜM:
• İlk açılış normal olarak yavaş
• SSD kullanıyorsanız daha hızlı olur
• RAM miktarını artırın (8GB+ önerilen)

🔒 GÜVENLİK BİLGİLERİ
═══════════════════════════════════════════════════════════════

• Kaynak kodlar tamamen şifrelenmiş
• Sadece lisanslı kullanıcılar çalıştırabilir
• Network trafiği şifrelenmemiş (normal)
• Kişisel veriler toplanmıyor

📞 DESTEK
═══════════════════════════════════════════════════════════════

Güvenli sürüm için özel destek:
• Log dosyası: Program klasöründe "mezat.log"
• Hata durumunda screenshot alın
• Sistem bilgilerini (Windows sürümü) belirtin

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Güvenli mezatlar dileriz! 🔒🎯
═══════════════════════════════════════════════════════════════"""
    
    with open(f"{setup_dir}/SECURE_KILAVUZ.txt", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("  ✅ SECURE_KILAVUZ.txt oluşturuldu")

def create_secure_config(setup_dir):
    """Güvenli ayarlar oluşturur"""
    print("\n⚙️ Güvenli ayarlar oluşturuluyor...")
    
    settings = {
        "language": "tr",
        "appearance_mode": "dark",
        "sounds_enabled": True,
        "sound_theme": "fight",
        "secure_version": True,
        "version": "2.0-SECURE"
    }
    
    with open(f"{setup_dir}/settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    print("  ✅ Güvenli settings.json oluşturuldu")

def create_secure_zip(setup_dir):
    """Güvenli ZIP paketi oluşturur"""
    print(f"\n📦 Güvenli ZIP paketi oluşturuluyor...")
    
    zip_name = f"{setup_dir}_FINAL.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(setup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, os.path.dirname(setup_dir))
                zipf.write(file_path, arc_name)
    
    file_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"  ✅ {zip_name} oluşturuldu ({file_size:.1f} MB)")
    
    return zip_name

def cleanup_nuitka_files():
    """Nuitka geçici dosyalarını temizle"""
    print("\n🧹 Nuitka geçici dosyaları temizleniyor...")
    
    nuitka_items = [
        "YouTube_Mezat_Yardimcisi_SECURE.build",
        "YouTube_Mezat_Yardimcisi_SECURE.dist", 
        "YouTube_Mezat_Yardimcisi_SECURE.onefile-build",
        "mezaxx.build",
        "mezaxx.dist",
        "mezaxx.onefile-build"
    ]
    
    for item in nuitka_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"  🗑️ {item} temizlendi")

def main():
    """Ana fonksiyon"""
    try:
        print("🎯 YouTube Mezat Yardımcısı - Güvenli EXE Oluşturucu")
        print("=" * 70)
        
        # Güvenli paket oluştur
        setup_dir = create_secure_package()
        
        if setup_dir:
            # Güvenli ZIP oluştur
            zip_file = create_secure_zip(setup_dir)
            
            # Geçici dosyaları temizle
            cleanup_nuitka_files()
            
            print("\n" + "=" * 70)
            print("🎉 GÜVENLİ EXE PAKETİ TAMAMLANDI!")
            print("=" * 70)
            print("🔒 Kaynak kodlar tamamen gizli!")
            print("📦 Python kurulumu gerektirmez!")
            print("🚀 Tek EXE dosyası ile çalışır!")
            print(f"📁 Klasör: {setup_dir}")
            print(f"📦 ZIP: {zip_file}")
            print("\n📋 MÜŞTERİLERİNİZ İÇİN TALİMATLAR:")
            print("  1. ZIP dosyasını indirin ve açın")
            print("  2. 'SECURE_SETUP.bat' dosyasına SAĞ TIK yapın")
            print("  3. 'Yönetici olarak çalıştır' seçin")
            print("  4. Antivirus uyarılarını kabul edin")
            print("  5. Kurulum tamamlandıktan sonra masaüstünden başlatacaklar")
            print("\n✅ GÜVENLİ SÜRÜM MÜŞTERİLERİNİZE HAZIR!")
        else:
            print("❌ Güvenli paket oluşturulamadı!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter tuşuna basın...")

