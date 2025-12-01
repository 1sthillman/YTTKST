#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Setup Installer Oluşturucu
Müşteriler için kaynak kodları gizli, sadece EXE çalışan kurulum paketi
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from pathlib import Path

def create_exe_with_pyinstaller():
    """PyInstaller ile güvenli EXE oluşturur"""
    print("🔨 EXE dosyası oluşturuluyor...")
    
    # PyInstaller kontrolü ve kurulumu
    try:
        import PyInstaller
    except ImportError:
        print("📦 PyInstaller yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Geçici spec dosyası oluştur
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mezaxx.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sound', 'sound'),
        ('LOGO.png', '.'),
        ('LICENSE.txt', '.'),
    ],
    hiddenimports=[
        'chat_downloader',
        'customtkinter',
        'pygame',
        'PIL',
        'requests',
        'beautifulsoup4',
        'websocket',
        'tkinter',
        'queue',
        'threading',
        'json',
        'time',
        'datetime',
        'logging',
        'os',
        'sys',
        'importlib.util',
        'subprocess',
        'hashlib',
        'webbrowser',
        'tempfile',
        'pathlib',
        'uuid',
        'socket',
        'platform',
        're'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube_Mezat_Yardimcisi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='LOGO.png'
)
'''
    
    with open("mezaxx_setup.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # PyInstaller ile EXE oluştur
    cmd = ["pyinstaller", "--clean", "mezaxx_setup.spec"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0 and os.path.exists("dist/YouTube_Mezat_Yardimcisi.exe"):
            print("✅ EXE başarıyla oluşturuldu!")
            return "dist/YouTube_Mezat_Yardimcisi.exe"
        else:
            print(f"❌ EXE oluşturma hatası: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ PyInstaller hatası: {e}")
        return None

def create_setup_package():
    """Profesyonel setup paketi oluşturur"""
    print("🎯 YouTube Mezat Yardımcısı - Setup Paketi Oluşturucu")
    print("=" * 60)
    
    # Setup klasörü oluştur
    setup_dir = "YouTube_Mezat_Yardimcisi_SETUP"
    if os.path.exists(setup_dir):
        shutil.rmtree(setup_dir)
    os.makedirs(setup_dir)
    
    print(f"📁 Setup klasörü: {setup_dir}")
    
    # EXE dosyası oluştur
    exe_path = create_exe_with_pyinstaller()
    if not exe_path:
        print("❌ EXE oluşturulamadı, alternatif yöntem kullanılıyor...")
        # Basit PyInstaller komutu dene
        simple_cmd = [
            "pyinstaller", 
            "--onefile", 
            "--windowed",
            "--name=YouTube_Mezat_Yardimcisi",
            "--add-data=sound;sound",
            "--add-data=LOGO.png;.",
            "mezaxx.py"
        ]
        
        try:
            subprocess.run(simple_cmd, check=True)
            exe_path = "dist/YouTube_Mezat_Yardimcisi.exe"
        except:
            print("❌ EXE oluşturulamıyor, Python sürümü ile devam ediliyor...")
            exe_path = None
    
    # EXE varsa kopyala, yoksa Python dosyasını kullan
    if exe_path and os.path.exists(exe_path):
        shutil.copy2(exe_path, f"{setup_dir}/YouTube_Mezat_Yardimcisi.exe")
        print("✅ EXE dosyası kopyalandı")
        use_exe = True
    else:
        shutil.copy2("mezaxx.py", f"{setup_dir}/mezaxx.py")
        print("⚠️ Python dosyası kullanılıyor")
        use_exe = False
    
    # Gerekli dosyaları kopyala
    print("\n📋 Gerekli dosyalar kopyalanıyor...")
    
    essential_files = [
        ("license_codes.json", "Lisans kodları"),
        ("LOGO.png", "Program ikonu"),
        ("LICENSE.txt", "Lisans metni"),
    ]
    
    for file, desc in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, setup_dir)
            print(f"  ✅ {desc}")
    
    # Ses klasörünü kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", f"{setup_dir}/sound", dirs_exist_ok=True)
        print("  ✅ Ses dosyaları")
    
    # Python sürümü için gerekli dosyalar
    if not use_exe:
        python_files = [
            ("auto_installer.py", "Modül yükleyici"),
            ("requirements.txt", "Gereksinimler"),
        ]
        
        for file, desc in python_files:
            if os.path.exists(file):
                shutil.copy2(file, setup_dir)
                print(f"  ✅ {desc}")
    
    # Setup scriptleri oluştur
    create_setup_scripts(setup_dir, use_exe)
    
    # Kurulum kılavuzu oluştur
    create_setup_guide(setup_dir, use_exe)
    
    # Varsayılan ayarlar
    create_default_config(setup_dir)
    
    return setup_dir, use_exe

def create_setup_scripts(setup_dir, use_exe):
    """Setup scriptleri oluşturur"""
    print("\n🛠️ Setup scriptleri oluşturuluyor...")
    
    if use_exe:
        # EXE için setup scripti
        setup_content = '''@echo off
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
echo  📋 Kurulum Adımları:
echo  ────────────────────────────────────────────────────────────────
echo.

REM Kurulum klasörü oluştur
set "INSTALL_DIR=%LOCALAPPDATA%\\YouTube Mezat Yardimcisi"
echo  📁 Kurulum klasörü hazırlanıyor...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Dosyaları kopyala
echo  📦 Program dosyaları kopyalanıyor...
copy "YouTube_Mezat_Yardimcisi.exe" "%INSTALL_DIR%\\" >nul
copy "license_codes.json" "%INSTALL_DIR%\\" >nul
copy "LOGO.png" "%INSTALL_DIR%\\" >nul
copy "LICENSE.txt" "%INSTALL_DIR%\\" >nul
copy "settings.json" "%INSTALL_DIR%\\" >nul
if exist "sound" xcopy "sound" "%INSTALL_DIR%\\sound\\" /E /I /Q >nul

REM Masaüstü kısayolu oluştur
echo  🔗 Masaüstü kısayolu oluşturuluyor...
powershell -WindowStyle Hidden -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\LOGO.png'; $Shortcut.Description = 'YouTube Mezat Yardımcısı v2.0'; $Shortcut.Save()}"

REM Başlat menüsü kısayolu
echo  📌 Başlat menüsü kısayolu oluşturuluyor...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\YouTube Mezat Yardımcısı\\" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\YouTube Mezat Yardımcısı\\"
powershell -WindowStyle Hidden -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\YouTube Mezat Yardımcısı\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\LOGO.png'; $Shortcut.Description = 'YouTube Mezat Yardımcısı v2.0'; $Shortcut.Save()}"

REM Kaldırma scripti oluştur
echo  🗑️ Kaldırma scripti hazırlanıyor...
echo @echo off > "%INSTALL_DIR%\\Uninstall.bat"
echo title YouTube Mezat Yardımcısı - Kaldırma >> "%INSTALL_DIR%\\Uninstall.bat"
echo echo Program kaldırılıyor... >> "%INSTALL_DIR%\\Uninstall.bat"
echo del "%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk" 2^>nul >> "%INSTALL_DIR%\\Uninstall.bat"
echo rd /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\YouTube Mezat Yardımcısı\\" 2^>nul >> "%INSTALL_DIR%\\Uninstall.bat"
echo cd /d "%TEMP%" >> "%INSTALL_DIR%\\Uninstall.bat"
echo rd /s /q "%INSTALL_DIR%\\" >> "%INSTALL_DIR%\\Uninstall.bat"
echo echo Program başarıyla kaldırıldı! >> "%INSTALL_DIR%\\Uninstall.bat"
echo pause >> "%INSTALL_DIR%\\Uninstall.bat"

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
echo  📍 Program Konumu: %INSTALL_DIR%
echo  🖥️ Masaüstü Kısayolu: Oluşturuldu
echo  📌 Başlat Menüsü: Oluşturuldu
echo.
echo  🚀 Programı başlatmak için:
echo     • Masaüstündeki kısayola çift tıklayın
echo     • Veya Başlat menüsünden açın
echo.
echo  📖 Kullanım kılavuzu için KURULUM_KILAVUZU.txt dosyasını okuyun
echo.
echo  ═══════════════════════════════════════════════════════════════
echo  Program hazır! Başarılı mezatlar dileriz! 🎯
echo  ═══════════════════════════════════════════════════════════════
echo.
pause
'''
    else:
        # Python için setup scripti
        setup_content = '''@echo off
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
    echo  📥 Python'u indirmek için: https://www.python.org/downloads/
    echo  ⚠️  Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin!
    echo.
    pause
    exit /b 1
)
echo  ✅ Python bulundu!

REM Kurulum klasörü oluştur
set "INSTALL_DIR=%LOCALAPPDATA%\\YouTube Mezat Yardimcisi"
echo  📁 Kurulum klasörü hazırlanıyor...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Dosyaları kopyala
echo  📦 Program dosyaları kopyalanıyor...
copy "mezaxx.py" "%INSTALL_DIR%\\" >nul
copy "auto_installer.py" "%INSTALL_DIR%\\" >nul
copy "requirements.txt" "%INSTALL_DIR%\\" >nul
copy "license_codes.json" "%INSTALL_DIR%\\" >nul
copy "LOGO.png" "%INSTALL_DIR%\\" >nul
copy "LICENSE.txt" "%INSTALL_DIR%\\" >nul
copy "settings.json" "%INSTALL_DIR%\\" >nul
if exist "sound" xcopy "sound" "%INSTALL_DIR%\\sound\\" /E /I /Q >nul

REM Python modüllerini yükle
echo  📦 Gerekli Python modülleri yükleniyor...
cd /d "%INSTALL_DIR%"
python auto_installer.py

REM Başlatma scripti oluştur
echo  🚀 Program başlatıcısı hazırlanıyor...
echo @echo off > "%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.bat"
echo python mezaxx.py >> "%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.bat"

REM Masaüstü kısayolu oluştur
echo  🔗 Masaüstü kısayolu oluşturuluyor...
powershell -WindowStyle Hidden -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YouTube_Mezat_Yardimcisi.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\LOGO.png'; $Shortcut.Description = 'YouTube Mezat Yardımcısı v2.0'; $Shortcut.Save()}"

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
echo  📍 Program Konumu: %INSTALL_DIR%
echo  🖥️ Masaüstü Kısayolu: Oluşturuldu
echo.
echo  🚀 Programı başlatmak için masaüstündeki kısayola çift tıklayın
echo.
pause
'''
    
    with open(f"{setup_dir}/SETUP.bat", "w", encoding="utf-8") as f:
        f.write(setup_content)
    print("  ✅ SETUP.bat oluşturuldu")

def create_setup_guide(setup_dir, use_exe):
    """Setup kılavuzu oluşturur"""
    print("\n📖 Setup kılavuzu oluşturuluyor...")
    
    if use_exe:
        guide_content = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                    KURULUM KILAVUZU                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 HIZLI KURULUM (ÖNERİLEN)
═══════════════════════════════════════════════════════════════

1. "SETUP.bat" dosyasına SAĞ TIK yapın
2. "Yönetici olarak çalıştır" seçin
3. Kurulum otomatik olarak tamamlanacak
4. Masaüstündeki kısayoldan programı başlatın

🎯 PROGRAM KULLANIMI
═══════════════════════════════════════════════════════════════

1. İLK AÇILIŞ:
   • YouTube kanal URL'nizi girin
   • Lisans kodunuzu girin
   • "Doğrula ve Devam Et" butonuna basın

2. YOUTUBE CHAT BAĞLANTISI:
   • Canlı yayın URL'sini "YouTube:" kutusuna yapıştırın
   • "Başlat" butonuna basın
   • Chat mesajları gelmeye başlayacak

3. MEZAT AYARLARI:
   • Ürün adını girin
   • Mezat modunu seçin (Sabit Fiyat/Ürün/En Yüksek)
   • Hedef fiyat ve stok adedini girin
   • "BAŞLAT" butonuna basın

4. ÖDEME YAPANLAR:
   • Chat'te kullanıcı adının yanındaki "+" butonuna basın
   • Veya "Yönet" butonundan toplu ekleme yapın
   • Sadece listedeki kullanıcıların teklifleri kabul edilir

🔧 SORUN GİDERME
═══════════════════════════════════════════════════════════════

PROBLEM: Program açılmıyor
ÇÖZÜM: 
• SETUP.bat'ı yönetici olarak tekrar çalıştırın
• Windows Defender'ı geçici olarak kapatın
• Antivirus programını kontrol edin

PROBLEM: Chat bağlanmıyor
ÇÖZÜM:
• YouTube URL'sinin doğru olduğundan emin olun
• Canlı yayının aktif olduğunu kontrol edin
• İnternet bağlantınızı test edin

PROBLEM: Teklifler algılanmıyor
ÇÖZÜM:
• Kullanıcıları "Ödeme Yapanlar" listesine ekleyin
• Mezat modunun doğru seçildiğinden emin olun
• Hedef fiyatın doğru girildiğini kontrol edin

📞 DESTEK
═══════════════════════════════════════════════════════════════

Sorun yaşıyorsanız:
• Program klasöründeki "mezat.log" dosyasını kontrol edin
• Hata mesajını tam olarak kaydedin
• Destek ekibiyle iletişime geçin

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════"""
    else:
        guide_content = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                    KURULUM KILAVUZU                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 KURULUM ADIMLARı
═══════════════════════════════════════════════════════════════

1. GEREKSİNİMLER:
   • Windows 10/11
   • Python 3.8 veya üzeri (otomatik yüklenecek)
   • İnternet bağlantısı

2. KURULUM:
   • "SETUP.bat" dosyasına SAĞ TIK yapın
   • "Yönetici olarak çalıştır" seçin
   • Python ve gerekli modüller otomatik yüklenecek
   • Kurulum tamamlandığında masaüstünde kısayol oluşacak

3. PROGRAM BAŞLATMA:
   • Masaüstündeki "YouTube Mezat Yardımcısı" kısayoluna çift tıklayın

🎯 PROGRAM KULLANIMI
═══════════════════════════════════════════════════════════════

[Kullanım talimatları aynı...]

🔧 SORUN GİDERME
═══════════════════════════════════════════════════════════════

PROBLEM: Python bulunamadı hatası
ÇÖZÜM:
• https://www.python.org/downloads/ adresinden Python indirin
• Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
• SETUP.bat'ı tekrar çalıştırın

[Diğer sorun giderme adımları aynı...]

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════"""
    
    with open(f"{setup_dir}/KURULUM_KILAVUZU.txt", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("  ✅ KURULUM_KILAVUZU.txt oluşturuldu")

def create_default_config(setup_dir):
    """Varsayılan ayarlar dosyası oluşturur"""
    print("\n⚙️ Varsayılan ayarlar oluşturuluyor...")
    
    settings = {
        "language": "tr",
        "appearance_mode": "dark", 
        "sounds_enabled": True,
        "sound_theme": "fight"
    }
    
    with open(f"{setup_dir}/settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    print("  ✅ settings.json oluşturuldu")

def create_final_zip(setup_dir, use_exe):
    """Final ZIP paketi oluşturur"""
    print(f"\n📦 Final ZIP paketi oluşturuluyor...")
    
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

def cleanup_temp_files():
    """Geçici dosyaları temizle"""
    print("\n🧹 Geçici dosyalar temizleniyor...")
    
    temp_items = [
        "build", "dist", "__pycache__", 
        "mezaxx_setup.spec", "YouTube_Mezat_Yardimcisi.spec"
    ]
    
    for item in temp_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"  🗑️ {item} temizlendi")

def main():
    """Ana fonksiyon"""
    try:
        print("🎯 YouTube Mezat Yardımcısı - Profesyonel Setup Oluşturucu")
        print("=" * 70)
        
        # Setup paketi oluştur
        setup_dir, use_exe = create_setup_package()
        
        # Final ZIP oluştur
        zip_file = create_final_zip(setup_dir, use_exe)
        
        # Geçici dosyaları temizle
        cleanup_temp_files()
        
        print("\n" + "=" * 70)
        print("🎉 SETUP PAKETİ TAMAMLANDI!")
        print("=" * 70)
        
        if use_exe:
            print("✅ EXE Sürümü: Kaynak kodlar gizli, sadece EXE çalışır")
        else:
            print("⚠️ Python Sürümü: Kaynak kodlar görünür ama daha güvenilir")
            
        print(f"📁 Klasör: {setup_dir}")
        print(f"📦 ZIP: {zip_file}")
        print("\n📋 MÜŞTERİLERİNİZ İÇİN TALİMATLAR:")
        print("  1. ZIP dosyasını indirin ve açın")
        print("  2. 'SETUP.bat' dosyasına SAĞ TIK yapın")
        print("  3. 'Yönetici olarak çalıştır' seçin")
        print("  4. Kurulum otomatik tamamlanacak")
        print("  5. Masaüstündeki kısayoldan programı başlatacaklar")
        print("\n✅ MÜŞTERİLERİNİZE GÖNDERMEYE HAZIR!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter tuşuna basın...")

