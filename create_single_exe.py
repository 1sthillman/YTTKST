#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - TEK EXE OLUŞTURUCU
Müşteriler için tek tıkla çalışan EXE dosyası
"""

import os
import sys
import shutil
import subprocess
import zipfile
import requests
import time

def download_file(url, filename):
    """Dosya indir"""
    print(f"📥 {filename} indiriliyor...")
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        progress = 0
        
        with open(filename, 'wb') as f:
            for data in response.iter_content(block_size):
                progress += len(data)
                f.write(data)
                done = int(50 * progress / total_size) if total_size > 0 else 50
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50 - done)}] {progress/1024/1024:.1f}/{total_size/1024/1024:.1f} MB")
                sys.stdout.flush()
        print("\n✅ İndirme tamamlandı")
        return True
    except Exception as e:
        print(f"\n❌ İndirme hatası: {e}")
        return False

def download_nsis():
    """NSIS indir"""
    nsis_url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.08/nsis-3.08-setup.exe/download"
    nsis_installer = "nsis-setup.exe"
    
    if os.path.exists(nsis_installer):
        print("✅ NSIS yükleyicisi zaten mevcut")
        return nsis_installer
        
    return download_file(nsis_url, nsis_installer)

def download_python_embeddable():
    """Gömülebilir Python indir"""
    python_url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
    python_zip = "python-3.10.11-embed-amd64.zip"
    
    if os.path.exists(python_zip):
        print("✅ Gömülebilir Python zaten mevcut")
        return python_zip
        
    return download_file(python_url, python_zip)

def install_nsis(installer_path):
    """NSIS yükle"""
    print("🛠️ NSIS yükleniyor...")
    try:
        subprocess.run([installer_path, "/S"], check=True)
        print("✅ NSIS yüklendi")
        return True
    except Exception as e:
        print(f"❌ NSIS yüklenemedi: {e}")
        return False

def find_nsis_compiler():
    """NSIS derleyicisini bul"""
    possible_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def extract_python_embeddable(zip_path):
    """Gömülebilir Python'u çıkart"""
    print("📦 Gömülebilir Python çıkartılıyor...")
    
    python_dir = "python-embed"
    if os.path.exists(python_dir):
        shutil.rmtree(python_dir)
    os.makedirs(python_dir)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(python_dir)
        print("✅ Python çıkartıldı")
        return python_dir
    except Exception as e:
        print(f"❌ Python çıkartma hatası: {e}")
        return None

def prepare_python_modules(python_dir):
    """Python modüllerini hazırla"""
    print("📦 Python modülleri hazırlanıyor...")
    
    # pip ve setuptools indir
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    pip_script = os.path.join(python_dir, "get-pip.py")
    
    download_file(get_pip_url, pip_script)
    
    # python310._pth dosyasını düzenle (import site için)
    pth_file = os.path.join(python_dir, "python310._pth")
    if os.path.exists(pth_file):
        with open(pth_file, "r") as f:
            content = f.read()
        
        if "#import site" in content:
            content = content.replace("#import site", "import site")
            with open(pth_file, "w") as f:
                f.write(content)
    
    # pip yükle
    python_exe = os.path.join(python_dir, "python.exe")
    try:
        subprocess.run([python_exe, pip_script], check=True)
        print("✅ pip yüklendi")
        
        # Gerekli modülleri yükle
        subprocess.run([
            os.path.join(python_dir, "Scripts", "pip.exe"),
            "install",
            "customtkinter",
            "requests",
            "pygame",
            "pillow",
            "beautifulsoup4",
            "chat-downloader",
            "websocket-client"
        ], check=True)
        print("✅ Modüller yüklendi")
        return True
    except Exception as e:
        print(f"❌ Modül yükleme hatası: {e}")
        return False

def modify_mezaxx_for_embedded():
    """mezaxx.py dosyasını gömülü Python için düzenle"""
    print("🔧 mezaxx.py dosyası düzenleniyor...")
    
    # Önce yedek al
    if os.path.exists("mezaxx.py") and not os.path.exists("mezaxx_original.py"):
        shutil.copy2("mezaxx.py", "mezaxx_original.py")
        print("✅ Orijinal mezaxx.py yedeklendi: mezaxx_original.py")
    
    try:
        # Dosyayı oku
        with open("mezaxx.py", "r", encoding="utf-8") as f:
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
            
            # Dosyayı kaydet
            with open("mezaxx.py", "w", encoding="utf-8") as f:
                f.write(content)
                
            print("✅ mezaxx.py dosyası düzenlendi")
            return True
        else:
            print("⚠️ mezaxx.py dosyasında gerekli bölümler bulunamadı")
            return False
    except Exception as e:
        print(f"❌ mezaxx.py düzenleme hatası: {e}")
        return False

def create_nsis_script():
    """NSIS script oluştur"""
    print("📝 NSIS script oluşturuluyor...")
    
    script_content = r'''
; YouTube Mezat Yardımcısı Kurulum Scripti
Unicode True

; Tanımlamalar
!define APPNAME "YouTube Mezat Yardımcısı"
!define COMPANYNAME "Mezat Yazılım"
!define DESCRIPTION "YouTube Mezat Yardımcısı"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define ABOUTURL "https://mezatyazilim.com"

; Kurulum ayarları
Name "${APPNAME}"
OutFile "YouTube_Mezat_Yardimcisi_TEK_TIKLA_KURULUM.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "Install_Dir"
RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "LOGO.ico"
!define MUI_UNICON "LOGO.ico"

; Sayfalar
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Diller
!insertmacro MUI_LANGUAGE "Turkish"

; Kurulum bölümü
Section "YouTube Mezat Yardımcısı" SecMain
  SetOutPath "$INSTDIR"
  
  ; Gömülü Python
  File /r "python-embed\*.*"
  
  ; Program dosyaları
  File "mezaxx.py"
  File "license_codes.json"
  File "LOGO.ico"
  File "LICENSE.txt"
  File "settings.json"
  
  ; Ses dosyaları
  SetOutPath "$INSTDIR\sound"
  File /r "sound\*.*"
  
  ; Başlatıcı oluştur
  FileOpen $0 "$INSTDIR\YouTube_Mezat_Yardimcisi.bat" w
  FileWrite $0 "@echo off$\r$\n"
  FileWrite $0 "cd /d $\"%~dp0$\"$\r$\n"
  FileWrite $0 "start pythonw.exe mezaxx.py$\r$\n"
  FileClose $0
  
  ; Kısayollar
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\YouTube_Mezat_Yardimcisi.bat" "" "$INSTDIR\LOGO.ico" 0
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\YouTube_Mezat_Yardimcisi.bat" "" "$INSTDIR\LOGO.ico" 0
  
  ; Kaldırma bilgisi
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\LOGO.ico"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" "${VERSIONMAJOR}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" "${VERSIONMINOR}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
  
  ; Kaldırma programını yaz
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Kaldırma bölümü
Section "Uninstall"
  ; Program dosyalarını kaldır
  RMDir /r "$INSTDIR"
  
  ; Kısayolları kaldır
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME}.lnk"
  
  ; Registry kayıtlarını kaldır
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  DeleteRegKey HKLM "Software\${APPNAME}"
SectionEnd

; Kurulum sonrası
Function .onInstSuccess
  ExecShell "" "$DESKTOP\${APPNAME}.lnk"
FunctionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ NSIS script oluşturuldu: installer.nsi")
    return "installer.nsi"

def convert_png_to_ico():
    """PNG'yi ICO'ya dönüştür"""
    print("🔄 LOGO.png dosyası ICO'ya dönüştürülüyor...")
    
    try:
        from PIL import Image
        
        if not os.path.exists("LOGO.png"):
            print("❌ LOGO.png bulunamadı")
            return False
        
        img = Image.open("LOGO.png")
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save("LOGO.ico", format="ICO", sizes=icon_sizes)
        
        print("✅ LOGO.ico oluşturuldu")
        return True
    except Exception as e:
        print(f"❌ ICO dönüştürme hatası: {e}")
        
        # PIL yüklü değilse yükle
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True)
            print("✅ Pillow yüklendi, tekrar deneniyor...")
            return convert_png_to_ico()
        except:
            print("❌ Pillow yüklenemedi")
            return False

def build_installer(nsis_compiler, script_path):
    """NSIS ile kurulum dosyası oluştur"""
    print("🔨 Kurulum dosyası oluşturuluyor...")
    print("⏳ Bu işlem birkaç dakika sürebilir...")
    
    try:
        result = subprocess.run([nsis_compiler, script_path], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists("YouTube_Mezat_Yardimcisi_TEK_TIKLA_KURULUM.exe"):
            print("✅ Kurulum dosyası başarıyla oluşturuldu!")
            print("📦 Dosya: YouTube_Mezat_Yardimcisi_TEK_TIKLA_KURULUM.exe")
            return True
        else:
            print(f"❌ Kurulum dosyası oluşturma hatası: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ NSIS çalıştırma hatası: {e}")
        return False

def create_single_exe():
    """Tek tıkla çalışan EXE oluştur"""
    print("🎯 YouTube Mezat Yardımcısı - TEK TIKLA KURULUM OLUŞTURUCU")
    print("=" * 70)
    
    # Gerekli dosyaları kontrol et
    required_files = ["mezaxx.py", "license_codes.json", "LOGO.png", "settings.json"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Bazı dosyalar eksik: {', '.join(missing_files)}")
        return False
    
    # LOGO.png'yi ICO'ya dönüştür
    convert_png_to_ico()
    
    # NSIS indir ve yükle
    nsis_installer = download_nsis()
    if nsis_installer:
        install_nsis(nsis_installer)
    
    # NSIS derleyicisini bul
    nsis_compiler = find_nsis_compiler()
    if not nsis_compiler:
        print("❌ NSIS derleyicisi bulunamadı")
        print("🔗 https://nsis.sourceforge.io/Download adresinden manuel olarak yükleyin")
        return False
    
    print(f"✅ NSIS derleyicisi bulundu: {nsis_compiler}")
    
    # Gömülebilir Python indir
    python_zip = download_python_embeddable()
    if not python_zip:
        print("❌ Gömülebilir Python indirilemedi")
        return False
    
    # Python'u çıkart
    python_dir = extract_python_embeddable(python_zip)
    if not python_dir:
        print("❌ Python çıkartılamadı")
        return False
    
    # Python modüllerini hazırla
    prepare_python_modules(python_dir)
    
    # mezaxx.py dosyasını düzenle
    modify_mezaxx_for_embedded()
    
    # NSIS script oluştur
    nsis_script = create_nsis_script()
    
    # Kurulum dosyası oluştur
    success = build_installer(nsis_compiler, nsis_script)
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 TEK TIKLA KURULUM DOSYASI TAMAMLANDI!")
        print("=" * 70)
        print("\n✅ MÜŞTERİLERİNİZ İÇİN TEK YAPMANIZ GEREKEN:")
        print("  1. YouTube_Mezat_Yardimcisi_TEK_TIKLA_KURULUM.exe dosyasını gönderin")
        print("  2. Müşterilerinize şu talimatı verin:")
        print("     \"Dosyaya çift tıklayın ve İleri > İleri > Kur butonlarına basın\"")
        print("\n✅ KURULUM SONRASI:")
        print("  • Program otomatik olarak başlayacak")
        print("  • Masaüstünde kısayol oluşturulacak")
        print("  • Başlat menüsünde kısayol oluşturulacak")
        print("\n✅ AVANTAJLARI:")
        print("  • Tek tıkla kurulum")
        print("  • Python gerektirmez (içinde gömülü)")
        print("  • CMD penceresi göstermez")
        print("  • Tüm modüller içinde")
        print("  • Profesyonel görünüm")
        print("\n🚀 MÜŞTERİLERİNİZE GÖNDERMEYE HAZIR!")
    else:
        print("\n❌ Kurulum dosyası oluşturulamadı!")
    
    return success

if __name__ == "__main__":
    create_single_exe()
    input("\nDevam etmek için Enter tuşuna basın...")


