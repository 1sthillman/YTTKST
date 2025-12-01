#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Bağımsız Başlatıcı Oluşturucu
CMD açılıp kapanma sorununu çözer
"""

import os
import sys
import shutil
import subprocess

def create_vbs_launcher():
    """VBS başlatıcı oluştur (CMD penceresi göstermez)"""
    print("🔧 VBS başlatıcı oluşturuluyor...")
    
    vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = CurrentDirectory
WshShell.Run "pythonw mezaxx.py", 0, False
'''
    
    with open("YouTube_Mezat_Yardimcisi_Baslat.vbs", "w", encoding="utf-8") as f:
        f.write(vbs_content)
    
    print("✅ VBS başlatıcı oluşturuldu: YouTube_Mezat_Yardimcisi_Baslat.vbs")
    return "YouTube_Mezat_Yardimcisi_Baslat.vbs"

def create_pythonw_bat():
    """Pythonw kullanarak görünmez başlatıcı oluştur"""
    print("🔧 Pythonw BAT başlatıcı oluşturuluyor...")
    
    bat_content = '''@echo off
cd /d "%~dp0"
start "" pythonw mezaxx.py
'''
    
    with open("YouTube_Mezat_Yardimcisi_Baslat_Pythonw.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    print("✅ Pythonw BAT başlatıcı oluşturuldu: YouTube_Mezat_Yardimcisi_Baslat_Pythonw.bat")
    return "YouTube_Mezat_Yardimcisi_Baslat_Pythonw.bat"

def create_direct_shortcut():
    """Doğrudan Python'a işaret eden kısayol oluştur"""
    print("🔧 Doğrudan kısayol oluşturuluyor...")
    
    try:
        import win32com.client
        
        # Python yolu bul
        python_path = sys.executable
        pythonw_path = python_path.replace("python.exe", "pythonw.exe")
        
        if not os.path.exists(pythonw_path):
            print(f"⚠️ Pythonw bulunamadı: {pythonw_path}")
            pythonw_path = python_path
        
        # Kısayol oluştur
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut("YouTube_Mezat_Yardimcisi.lnk")
        shortcut.TargetPath = pythonw_path
        shortcut.Arguments = "mezaxx.py"
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = os.path.join(os.getcwd(), "LOGO.png")
        shortcut.Save()
        
        print("✅ Doğrudan kısayol oluşturuldu: YouTube_Mezat_Yardimcisi.lnk")
        return "YouTube_Mezat_Yardimcisi.lnk"
    except Exception as e:
        print(f"❌ Kısayol oluşturulamadı: {e}")
        return None

def create_modified_mezaxx():
    """Mezaxx.py dosyasını CMD'siz çalışacak şekilde modifiye et"""
    print("🔧 Mezaxx.py dosyası modifiye ediliyor...")
    
    # Önce yedek al
    if os.path.exists("mezaxx.py") and not os.path.exists("mezaxx_original.py"):
        shutil.copy2("mezaxx.py", "mezaxx_original.py")
        print("✅ Orijinal mezaxx.py yedeklendi: mezaxx_original.py")
    
    try:
        # Dosyayı oku
        with open("mezaxx.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Başlangıca no_console kodu ekle
        if "import sys" in content and "if __name__ == \"__main__\":" in content:
            # Başlangıç kodu
            no_console_code = '''
# CMD penceresini gizle
import ctypes
import sys

if sys.platform == "win32":
    try:
        # Windows'ta konsol penceresini gizle
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
'''
            
            # İlk import sys'den sonra ekle
            content = content.replace("import sys", "import sys" + no_console_code, 1)
            
            # Dosyayı kaydet
            with open("mezaxx.py", "w", encoding="utf-8") as f:
                f.write(content)
                
            print("✅ mezaxx.py dosyası CMD'siz çalışacak şekilde modifiye edildi")
            return True
        else:
            print("⚠️ mezaxx.py dosyasında gerekli bölümler bulunamadı")
            return False
    except Exception as e:
        print(f"❌ mezaxx.py modifikasyon hatası: {e}")
        return False

def create_standalone_exe():
    """PyInstaller ile bağımsız EXE oluştur"""
    print("🔧 Bağımsız EXE oluşturma denenecek...")
    
    try:
        # PyInstaller kontrolü
        try:
            import PyInstaller
        except ImportError:
            print("📦 PyInstaller yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # EXE oluştur
        print("⏳ EXE oluşturuluyor (bu işlem birkaç dakika sürebilir)...")
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=YouTube_Mezat_Yardimcisi",
            "--icon=LOGO.png",
            "--add-data=sound;sound",
            "--add-data=LOGO.png;.",
            "--add-data=LICENSE.txt;.",
            "--add-data=license_codes.json;.",
            "mezaxx.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists("dist/YouTube_Mezat_Yardimcisi.exe"):
            shutil.copy2("dist/YouTube_Mezat_Yardimcisi.exe", "YouTube_Mezat_Yardimcisi.exe")
            print("✅ Bağımsız EXE oluşturuldu: YouTube_Mezat_Yardimcisi.exe")
            return "YouTube_Mezat_Yardimcisi.exe"
        else:
            print(f"❌ EXE oluşturulamadı: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ EXE oluşturma hatası: {e}")
        return None

def create_all_launchers():
    """Tüm başlatıcıları oluştur"""
    print("🎯 YouTube Mezat Yardımcısı - Bağımsız Başlatıcı Oluşturucu")
    print("=" * 60)
    
    # Mezaxx.py dosyasını modifiye et
    modified = create_modified_mezaxx()
    
    # VBS başlatıcı oluştur
    vbs_launcher = create_vbs_launcher()
    
    # Pythonw BAT başlatıcı oluştur
    pythonw_bat = create_pythonw_bat()
    
    # Doğrudan kısayol oluştur
    try:
        shortcut = create_direct_shortcut()
    except:
        shortcut = None
    
    # Bağımsız EXE oluştur (opsiyonel)
    try:
        standalone_exe = create_standalone_exe()
    except:
        standalone_exe = None
    
    # Kullanım talimatları oluştur
    create_launcher_instructions()
    
    print("\n" + "=" * 60)
    print("🎉 BAŞLATICILAR OLUŞTURULDU!")
    print("=" * 60)
    
    print("\n📋 KULLANIM TALİMATLARI:")
    print("  1. Müşterilerinize şu dosyaları gönderin:")
    if vbs_launcher:
        print(f"     - {vbs_launcher} (EN İYİ SEÇENEK - CMD göstermez)")
    if pythonw_bat:
        print(f"     - {pythonw_bat} (Alternatif - CMD göstermez)")
    if shortcut:
        print(f"     - {shortcut} (Alternatif - Kısayol)")
    if standalone_exe:
        print(f"     - {standalone_exe} (Alternatif - Bağımsız EXE)")
    print("  2. BASLATICI_TALIMATLARI.txt dosyasını da ekleyin")
    
    print("\n✅ SORUN ÇÖZÜLDÜ! Artık program CMD penceresi göstermeden çalışacak")

def create_launcher_instructions():
    """Başlatıcı kullanım talimatları oluştur"""
    print("📝 Başlatıcı talimatları oluşturuluyor...")
    
    instructions = """╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                 BAŞLATICI TALİMATLARI                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📌 CMD PENCERE SORUNU ÇÖZÜLDÜ!
═══════════════════════════════════════════════════════════════

Programı başlatmak için aşağıdaki dosyalardan BİRİNE çift tıklayın:

1️⃣ "YouTube_Mezat_Yardimcisi_Baslat.vbs"
   • EN İYİ SEÇENEK
   • CMD penceresi göstermez
   • Doğrudan program açılır

2️⃣ "YouTube_Mezat_Yardimcisi_Baslat_Pythonw.bat"
   • Alternatif çözüm
   • CMD penceresi göstermez
   • Doğrudan program açılır

3️⃣ "YouTube_Mezat_Yardimcisi.lnk"
   • Kısayol dosyası
   • Bazı sistemlerde çalışmayabilir
   • Masaüstüne kopyalayabilirsiniz

4️⃣ "YouTube_Mezat_Yardimcisi.exe" (varsa)
   • Bağımsız çalıştırılabilir dosya
   • Python gerektirmez
   • Doğrudan çift tıklayarak çalıştırın

⚠️ ESKİ DOSYALARI KULLANMAYIN:
   • "mezaxx.py" dosyasını doğrudan çalıştırmayın
   • "YouTube_Mezat_Yardimcisi_BASLAT.bat" dosyasını kullanmayın

🔧 SORUN YAŞARSANIZ:
   • Tüm başlatıcıları deneyin
   • Python'un kurulu olduğundan emin olun
   • Dosyaların aynı klasörde olduğunu kontrol edin

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════"""
    
    with open("BASLATICI_TALIMATLARI.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("✅ Başlatıcı talimatları oluşturuldu: BASLATICI_TALIMATLARI.txt")

if __name__ == "__main__":
    create_all_launchers()
    input("\nDevam etmek için Enter tuşuna basın...")


