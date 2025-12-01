#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - PORTABLE EXE OLUŞTURUCU
Müşteriler için tek tıkla çalışan portable EXE dosyası
"""

import os
import sys
import shutil
import subprocess
import zipfile
import time
from pathlib import Path

def check_pyinstaller():
    """PyInstaller kontrolü yap"""
    print("🔍 PyInstaller kontrol ediliyor...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], check=True, capture_output=True)
        print("✅ PyInstaller zaten yüklü")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ PyInstaller yüklü değil, yükleniyor...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller başarıyla yüklendi")
            return True
        except Exception as e:
            print(f"❌ PyInstaller yüklenemedi: {e}")
            return False

def modify_mezaxx_for_portable():
    """mezaxx.py dosyasını portable kullanım için düzenle"""
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
            
            # sys.exit(1) kodlarını sys.exit(0) ile değiştir
            content = content.replace("sys.exit(1)", "sys.exit(0)")
            
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

def create_portable_exe():
    """PyInstaller ile portable EXE oluştur"""
    print("🚀 Portable EXE oluşturuluyor...")
    
    # Gerekli dosyaları kontrol et
    sound_dir = os.path.join(os.getcwd(), "sound")
    if not os.path.exists(sound_dir):
        print(f"❌ Ses dosyaları bulunamadı: {sound_dir}")
        return False
    
    # Ek dosyaları kontrol et
    required_files = ["license_codes.json", "settings.json", "LOGO.ico"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Bazı dosyalar eksik: {', '.join(missing_files)}")
        if "LOGO.ico" in missing_files and os.path.exists("LOGO.png"):
            convert_png_to_ico()
        else:
            return False
    
    # PyInstaller komutunu oluştur
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "YouTube Mezat Yardimcisi",
        "--onefile",
        "--windowed",
        "--icon", "LOGO.ico",
        "--add-data", f"sound{os.pathsep}sound",
        "--add-data", f"license_codes.json{os.pathsep}.",
        "--add-data", f"settings.json{os.pathsep}.",
    ]
    
    # Auth data varsa ekle
    if os.path.exists("auth_data.json"):
        pyinstaller_cmd.extend(["--add-data", f"auth_data.json{os.pathsep}."])
    
    # mezaxx.py ekle
    pyinstaller_cmd.append("mezaxx.py")
    
    print("⏳ PyInstaller çalıştırılıyor...")
    print(f"📋 Komut: {' '.join(pyinstaller_cmd)}")
    print("⚠️ Bu işlem birkaç dakika sürebilir, lütfen bekleyin...")
    
    try:
        # PyInstaller çalıştır
        process = subprocess.Popen(
            pyinstaller_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # İlerlemeyi göster
        print("\n📊 İşlem durumu:")
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(f"  {output.strip()}")
            
            error = process.stderr.readline()
            if error:
                print(f"  ⚠️ {error.strip()}")
        
        # Son çıktıları kontrol et
        remaining_output, remaining_error = process.communicate()
        if remaining_output:
            print(remaining_output)
        if remaining_error:
            print(f"⚠️ {remaining_error}")
        
        # Başarı kontrolü
        if process.returncode == 0:
            print("\n✅ PyInstaller başarıyla tamamlandı!")
            
            # EXE dosyasını kontrol et
            exe_path = os.path.join("dist", "YouTube Mezat Yardimcisi.exe")
            if os.path.exists(exe_path):
                print(f"📦 EXE dosyası oluşturuldu: {exe_path}")
                
                # Sonuç klasörü oluştur
                result_dir = "YOUTUBE_MEZAT_YARDIMCISI_PORTABLE"
                if os.path.exists(result_dir):
                    shutil.rmtree(result_dir)
                os.makedirs(result_dir)
                
                # EXE dosyasını kopyala
                shutil.copy2(exe_path, os.path.join(result_dir, "YouTube Mezat Yardimcisi.exe"))
                
                # Readme oluştur
                with open(os.path.join(result_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
                    f.write("""╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🎯 YouTube Mezat Yardımcısı v2.0 🎯                ║
║                                                              ║
║                 KULLANIM TALİMATLARI                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 KOLAY KULLANIM
═══════════════════════════════════════════════════════════════

1️⃣ "YouTube Mezat Yardimcisi.exe" dosyasına ÇİFT TIKLAYIN
2️⃣ Program otomatik olarak başlayacak
3️⃣ YouTube canlı yayın URL'sini girin ve başlatın

⚠️ ÖNEMLİ NOTLAR
═══════════════════════════════════════════════════════════════

• Bu program KURULUM GEREKTİRMEZ
• USB bellek veya harici disk üzerinden çalıştırabilirsiniz
• Windows Defender uyarı verebilir, "Daha Fazla Bilgi" > "Yine de Çalıştır" seçeneklerini kullanın
• İlk çalıştırmada birkaç saniye beklemek gerekebilir

💡 SORUN GİDERME
═══════════════════════════════════════════════════════════════

SORUN: "Program açılmıyor"
ÇÖZÜM: 
• Antivirüs programınızı geçici olarak devre dışı bırakın
• Windows Defender'da istisna ekleyin
• Programı Yönetici olarak çalıştırın

SORUN: "Bağlantı hatası"
ÇÖZÜM:
• İnternet bağlantınızı kontrol edin
• YouTube URL'sini doğru girdiğinizden emin olun
• Canlı yayının aktif olduğundan emin olun

═══════════════════════════════════════════════════════════════
© 2024 Mezat Yazılım - Başarılı mezatlar dileriz! 🎯
═══════════════════════════════════════════════════════════════""")
                
                # ZIP oluştur
                zip_path = f"{result_dir}.zip"
                print(f"📦 ZIP dosyası oluşturuluyor: {zip_path}")
                
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(result_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, os.path.dirname(result_dir))
                            zipf.write(file_path, arc_name)
                
                print(f"✅ ZIP dosyası oluşturuldu: {zip_path}")
                
                return True
            else:
                print(f"❌ EXE dosyası bulunamadı: {exe_path}")
                return False
        else:
            print(f"❌ PyInstaller hatası: İşlem kodu {process.returncode}")
            return False
    except Exception as e:
        print(f"❌ PyInstaller çalıştırma hatası: {e}")
        return False

def create_single_portable_exe():
    """Tek tıkla çalışan portable EXE oluştur"""
    print("🎯 YouTube Mezat Yardımcısı - PORTABLE EXE OLUŞTURUCU")
    print("=" * 70)
    
    # PyInstaller kontrolü
    if not check_pyinstaller():
        return False
    
    # mezaxx.py dosyasını düzenle
    modify_mezaxx_for_portable()
    
    # PNG'yi ICO'ya dönüştür
    convert_png_to_ico()
    
    # Portable EXE oluştur
    success = create_portable_exe()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 PORTABLE EXE DOSYASI TAMAMLANDI!")
        print("=" * 70)
        print("\n✅ MÜŞTERİLERİNİZ İÇİN TEK YAPMANIZ GEREKEN:")
        print("  1. YOUTUBE_MEZAT_YARDIMCISI_PORTABLE.zip dosyasını gönderin")
        print("  2. Müşterilerinize şu talimatı verin:")
        print("     \"ZIP'i açın ve YouTube Mezat Yardimcisi.exe dosyasına çift tıklayın\"")
        print("\n✅ AVANTAJLARI:")
        print("  • Kurulum gerektirmez")
        print("  • Tek tıkla çalışır")
        print("  • CMD penceresi göstermez")
        print("  • Tüm dosyalar içinde")
        print("  • USB bellekten bile çalıştırılabilir")
        print("\n🚀 MÜŞTERİLERİNİZE GÖNDERMEYE HAZIR!")
    else:
        print("\n❌ Portable EXE dosyası oluşturulamadı!")
        print("🔧 Alternatif çözüm için:")
        print("  1. auto-py-to-exe aracını kullanabilirsiniz:")
        print("     pip install auto-py-to-exe")
        print("     auto-py-to-exe")
        print("  2. Grafik arayüzünden mezaxx.py'yi seçin")
        print("  3. 'One File' ve 'Window Based' seçeneklerini işaretleyin")
        print("  4. 'Additional Files' bölümünden ses dosyalarını ve JSON dosyalarını ekleyin")
        print("  5. 'Convert .py to .exe' düğmesine tıklayın")
    
    return success

if __name__ == "__main__":
    create_single_portable_exe()
    input("\nDevam etmek için Enter tuşuna basın...")


