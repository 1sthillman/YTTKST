#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Inno Setup Kurulum Oluşturucu
Profesyonel ve hızlı kurulum paketi oluşturur
"""

import os
import sys
import shutil
import subprocess
import requests
import zipfile
from pathlib import Path

def download_inno_setup():
    """Inno Setup indirir"""
    print("📥 Inno Setup indiriliyor...")
    
    inno_url = "https://jrsoftware.org/download.php/is.exe"
    inno_installer = "innosetup.exe"
    
    try:
        response = requests.get(inno_url, stream=True)
        with open(inno_installer, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Inno Setup indirildi")
        return inno_installer
    except Exception as e:
        print(f"❌ Inno Setup indirilemedi: {e}")
        return None

def download_python_installer():
    """Python yükleyicisini indir"""
    print("📥 Python yükleyicisi indiriliyor...")
    
    python_url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    python_installer = "python-3.10.11-amd64.exe"
    
    try:
        if os.path.exists(python_installer):
            print("✅ Python yükleyicisi zaten mevcut")
            return python_installer
            
        response = requests.get(python_url, stream=True)
        with open(python_installer, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Python yükleyicisi indirildi")
        return python_installer
    except Exception as e:
        print(f"❌ Python yükleyicisi indirilemedi: {e}")
        return None

def install_inno_setup(installer_path):
    """Inno Setup'ı yükler"""
    print("🛠️ Inno Setup yükleniyor...")
    
    try:
        subprocess.run([installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], check=True)
        print("✅ Inno Setup yüklendi")
        return True
    except Exception as e:
        print(f"❌ Inno Setup yüklenemedi: {e}")
        return False

def find_inno_compiler():
    """Inno Setup derleyicisini bulur"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_inno_setup_package():
    """Inno Setup ile kurulum paketi oluşturur"""
    print("🎯 YouTube Mezat Yardımcısı - Inno Setup Paketi")
    print("=" * 60)
    
    # Python yükleyicisini indir
    python_installer = download_python_installer()
    if not python_installer:
        print("❌ Python yükleyicisi indirilemedi, devam ediliyor...")
    
    # Inno Setup'ı bul veya indir/yükle
    iscc_path = find_inno_compiler()
    if not iscc_path:
        print("⚠️ Inno Setup bulunamadı, indiriliyor...")
        inno_installer = download_inno_setup()
        if inno_installer:
            install_inno_setup(inno_installer)
            iscc_path = find_inno_compiler()
    
    if not iscc_path:
        print("❌ Inno Setup bulunamadı veya yüklenemedi")
        print("🔗 https://jrsoftware.org/isdl.php adresinden manuel olarak yükleyin")
        return False
    
    print(f"✅ Inno Setup bulundu: {iscc_path}")
    
    # Inno Script'i derle
    print("\n🔨 Kurulum paketi oluşturuluyor...")
    try:
        result = subprocess.run([iscc_path, "inno_setup_script.iss"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Kurulum paketi başarıyla oluşturuldu!")
            if os.path.exists("YouTube_Mezat_Yardimcisi_Setup.exe"):
                print(f"📦 Kurulum dosyası: YouTube_Mezat_Yardimcisi_Setup.exe")
                return True
            else:
                print("❌ Kurulum dosyası bulunamadı")
                return False
        else:
            print(f"❌ Derleme hatası: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Derleme hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    try:
        print("🎯 YouTube Mezat Yardımcısı - Inno Setup Kurulum Oluşturucu")
        print("=" * 70)
        
        # Inno Setup script'i kontrol et
        if not os.path.exists("inno_setup_script.iss"):
            print("❌ inno_setup_script.iss bulunamadı!")
            return False
        
        # Gerekli dosyaları kontrol et
        required_files = ["mezaxx.py", "auto_installer.py", "requirements.txt", "LOGO.png", "LICENSE.txt"]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"❌ Bazı dosyalar eksik: {', '.join(missing_files)}")
            return False
        
        # Kurulum paketi oluştur
        success = create_inno_setup_package()
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 INNO SETUP PAKETİ TAMAMLANDI!")
            print("=" * 70)
            print("✅ Tek tıkla kurulum: YouTube_Mezat_Yardimcisi_Setup.exe")
            print("✅ Otomatik Python yükleme")
            print("✅ Gerekli modülleri otomatik kurma")
            print("✅ Masaüstü kısayolu oluşturma")
            print("✅ Başlat menüsü kısayolu")
            print("✅ Profesyonel kurulum sihirbazı")
            print("\n📋 MÜŞTERİLERİNİZ İÇİN TALİMATLAR:")
            print("  1. YouTube_Mezat_Yardimcisi_Setup.exe dosyasını gönderin")
            print("  2. Çift tıklayıp çalıştırmalarını söyleyin")
            print("  3. 'İleri > İleri > Yükle' ile kurulumu tamamlayacaklar")
            print("  4. Kurulum sonrası program otomatik başlayacak")
            print("\n✅ MÜŞTERİLERİNİZE GÖNDERMEYE HAZIR!")
        else:
            print("\n❌ Kurulum paketi oluşturulamadı!")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter tuşuna basın...")

