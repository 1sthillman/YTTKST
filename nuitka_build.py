#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Nuitka Derleme Betiği
"""

import os
import sys
import shutil
import subprocess
import platform

# Gerekli dosyalar
REQUIRED_FILES = [
    "LOGO.png", 
    "license_codes.json",
    "license_usage.json",
    "settings.json",
    "auth_data.json", 
    "paid_users.json", 
    "LICENSE.txt",
]

def check_nuitka():
    """Nuitka'nın kurulu olup olmadığını kontrol et"""
    try:
        import nuitka
        import pkg_resources
        version = pkg_resources.get_distribution("nuitka").version
        print(f"✓ Nuitka bulundu: {version}")
        return True
    except ImportError:
        print("× Nuitka bulunamadı. Yükleniyor...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])
            return True
        except Exception as e:
            print(f"Hata: Nuitka yüklenemedi: {e}")
            return False

def check_dependencies():
    """Gerekli modülleri kontrol et"""
    dependencies = [
        "customtkinter",
        "PIL",
        "requests",
        "chat_downloader"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == "PIL":
                __import__("PIL.Image")
            else:
                __import__(dep)
            print(f"✓ {dep} kurulu")
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"Eksik modüller: {', '.join(missing)}")
        try:
            for dep in missing:
                if dep == "PIL":
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
                else:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            return True
        except Exception as e:
            print(f"Hata: Bağımlılıklar yüklenemedi: {e}")
            return False
    return True

def check_required_files():
    """Gerekli dosyaların varlığını kontrol et"""
    missing = []
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            if file in ["license_usage.json", "auth_data.json", "paid_users.json"]:
                # Bu dosyalar olmayabilir, boş dosya oluştur
                with open(file, "w", encoding="utf-8") as f:
                    f.write("{}")
                print(f"→ {file} oluşturuldu")
            else:
                missing.append(file)
    
    if missing:
        print(f"Hata: Eksik dosyalar: {', '.join(missing)}")
        return False
    return True

def build_with_nuitka():
    """Nuitka ile uygulamayı derle"""
    print("\n=== Nuitka ile derleme işlemi başlıyor ===\n")
    
    options = [
        "--standalone",               # Bağımsız çalışabilen uygulama
        "--onefile",                  # Tek dosya olarak paketleme
        "--remove-output",            # Önceki derlemeler varsa temizle
        "--windows-icon-from-ico=LOGO.png",  # Program ikonu
        "--windows-company-name=YouTube Mezat Yardimcisi",  # Şirket adı
        "--windows-product-name=YouTube Mezat Yardimcisi",  # Ürün adı
        "--windows-file-version=1.0.0.0",  # Dosya sürümü
        "--windows-product-version=1.0.0.0",  # Ürün sürümü
        "--include-data-dir=.=.",    # Tüm klasör içeriğini ekle
        "--include-package=customtkinter",   # Tam paketleri dahil et
        "--include-package=PIL", 
        "--include-package=requests",
        "--include-package=chat_downloader",
    ]
    
    # Windows için konsolu gizle
    if platform.system() == "Windows":
        options.append("--windows-disable-console")

    # Nuitka komutu oluştur
    cmd = [sys.executable, "-m", "nuitka"] + options + ["mezaxx.py"]
    
    try:
        # Komutu çalıştır
        print(f"Komut çalıştırılıyor: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Çıktıyı göster
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Hata kontrolü
        if process.returncode != 0:
            print("\n=== HATA ===")
            print(process.stderr.read())
            return False
            
        # Başarı mesajı
        print("\n=== DERLEME TAMAMLANDI ===")
        
        # Windows'da dosyayı yeniden adlandır
        if platform.system() == "Windows":
            try:
                src = "mezaxx.exe"
                dst = "YouTube Mezat Yardimcisi.exe"
                if os.path.exists(src):
                    if os.path.exists(dst):
                        os.remove(dst)
                    os.rename(src, dst)
                    print(f"{src} → {dst} olarak yeniden adlandırıldı")
            except Exception as e:
                print(f"Yeniden adlandırma hatası: {e}")
        
        return True
        
    except Exception as e:
        print(f"Derleme hatası: {e}")
        return False

def main():
    """Ana işlev"""
    print("YouTube Mezat Yardımcısı - Nuitka Derleyicisi")
    print("=" * 50)
    
    # Gerekli kontroller
    if not check_nuitka():
        return False
    
    if not check_dependencies():
        return False
    
    if not check_required_files():
        return False
    
    # Derleme işlemi
    success = build_with_nuitka()
    
    if success:
        print("\n✓ İşlem başarıyla tamamlandı!")
        print("  Program çalıştırılabilir dosyası oluşturuldu.")
    else:
        print("\n× Derleme sırasında bir hata oluştu.")
    
    return success

if __name__ == "__main__":
    main()
