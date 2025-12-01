# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import datetime
import json

def check_pyinstaller():
    """PyInstaller kurulu mu kontrol eder, yoksa kurar."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], check=True, capture_output=True)
        print("[+] PyInstaller zaten kurulu.")
        return True
    except subprocess.CalledProcessError:
        print("[*] PyInstaller kuruluyor...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("[+] PyInstaller basariyla kuruldu.")
            return True
        except subprocess.CalledProcessError:
            print("[-] PyInstaller kurulamadi.")
            return False

def install_required_packages():
    """Gerekli paketleri yükler"""
    packages = [
        "customtkinter>=5.2.0",
        "CTkMessagebox>=2.5",
        "Pillow>=10.0.0",
        "pygame>=2.5.0",
        "requests>=2.31.0",
        "chat-downloader>=0.2.0",
        "supabase>=2.0.0",
        "websockets>=15.0.0",
        "babel>=2.9.0"
    ]
    
    print("[*] Gerekli paketler yükleniyor...")
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--upgrade"], check=True)
            print(f"[+] {package} yüklendi.")
        except subprocess.CalledProcessError as e:
            print(f"[-] {package} yüklenemedi: {e}")
            return False
    return True

def create_empty_auth_data():
    """Boş auth_data.json dosyası oluşturur"""
    auth_data = {
        "youtube_name": "",
        "youtube_url": "",
        "authenticated": False,
        "supabase_user_id": None
    }
    
    with open("auth_data.json", "w", encoding="utf-8") as f:
        json.dump(auth_data, f, ensure_ascii=False, indent=2)
    print("[+] Boş auth_data.json dosyası oluşturuldu.")
    return True

def create_exe_package():
    """PyInstaller ile EXE paketi oluşturur"""
    # Bugünün tarihi
    today = datetime.datetime.now().strftime("%d%m%Y")
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_FINAL_EXE_{today}"
    
    # Gerekli klasörleri oluştur
    dist_dir = os.path.join(os.getcwd(), "dist")
    build_dir = os.path.join(os.getcwd(), "build")
    
    # Önceki build klasörlerini temizle
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            print(f"[*] Temizleniyor: {dir_path}")
            shutil.rmtree(dir_path)
    
    # Beklenen EXE dosyası yolu
    exe_path = os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi.exe")
    
    # Gerekli dosyaları kontrol et
    required_files = ["license_codes.json", "supabase_config.json", "mezaxx.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"[-] {file} dosyası bulunamadı!")
            return False
    
    # Boş auth_data.json oluştur
    create_empty_auth_data()
    
    # PyInstaller komutu doğrudan çalıştır
    print("\n[*] PyInstaller ile EXE olusturuluyor...")
    print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
    
    # PyInstaller komut satırı
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "YouTube_Mezat_Yardimcisi",
        "--add-data", "license_codes.json;.",
        "--add-data", "supabase_config.json;.",
        "--add-data", "auth_data.json;.",
        "--add-data", "sound;sound",
        "--hidden-import", "chat_downloader",
        "--hidden-import", "chat_downloader.sites",
        "--hidden-import", "chat_downloader.sites.youtube",
        "--hidden-import", "websockets",
        "--hidden-import", "babel",
        "--hidden-import", "babel.numbers",
        "--hidden-import", "babel.dates",
        "--hidden-import", "customtkinter",
        "--hidden-import", "CTkMessagebox",
        "--hidden-import", "PIL",
        "--hidden-import", "pygame",
        "--hidden-import", "requests",
        "--hidden-import", "supabase",
        "--hidden-import", "websocket",
        "--hidden-import", "websocket-client",
        "--hidden-import", "realtime",
        "--hidden-import", "realtime.connection",
        "mezaxx.py"
    ]
    
    # PyInstaller'ı çalıştır
    try:
        print(f"[*] Komut: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("\n[+] EXE dosyasi basariyla olusturuldu.")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] EXE olusturma hatasi: {e}")
        return False

    # Çıktı klasörünü kontrol et
    if not os.path.exists(exe_path):
        print(f"[-] Beklenen EXE dosyasi bulunamadi: {exe_path}")
        return False

    # Final klasörü oluştur
    final_dir = os.path.join(os.getcwd(), package_name)
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    os.makedirs(final_dir)
    
    # EXE dosyasını final klasörüne kopyala
    shutil.copy2(exe_path, os.path.join(final_dir, "YouTube_Mezat_Yardimcisi.exe"))
    print(f"[+] EXE dosyası final klasörüne kopyalandı.")

    # Kullanım talimatları dosyası oluştur
    info_text = """
YouTube Mezat Yardimcisi - KULLANIM TALIMATLARI:

1. YouTube_Mezat_Yardimcisi.exe dosyasina cift tiklayarak programi baslatin.

2. Program basladiginda, YouTube kanal URL'nizi ve lisans kodunuzu girerek giris yapin.
   - YouTube kanal URL'si: Size verilen YouTube kanal URL'sini girin
   - Lisans kodu: Size verilen lisans kodunu girin

3. "Doğrula ve Devam Et" butonuna tıklayarak programa giriş yapabilirsiniz.

4. Programa ilk kez giris yaptiktan sonra, kullanici bilgileriniz yerel olarak kaydedilecektir.

5. Sistemi kullanirken internet baglantinizin aktif oldugundan emin olun.

GERÇEK LİSANS KODLARI:

Aşağıdaki lisans kodları ve kanal bilgileri, programın kullanımı için geçerlidir:

1. Uzmanbicak:
   - Kanal URL: https://www.youtube.com/@Uzmanbicak
   - Lisans Kodu: YMY-2024-W3X7-Y2Z8

2. Karavil_bıçak:
   - Kanal URL: https://www.youtube.com/@Karavil_bıçak
   - Lisans Kodu: YMY-2024-J2K7-L4M9

3. Hüseyin_usta_mezat:
   - Kanal URL: https://www.youtube.com/@hüseyin_usta_mezat
   - Lisans Kodu: YMY-2024-J3K6-L8M2

TEST KODLARI:

Aşağıdaki test kodlarını da kullanarak programa giriş yapabilirsiniz:
- TEST456 (herhangi bir kanal ile kullanılabilir)
- DEMO123 (herhangi bir kanal ile kullanılabilir)

ÖNEMLİ NOTLAR:

- Program klasörünü güvenli bir yere kopyalayın, içindeki dosyaları silmeyin veya değiştirmeyin.
- Programı kullanırken internet bağlantınızın açık olduğundan emin olun.
- Herhangi bir sorun yaşarsanız, lütfen bizimle iletişime geçin.

İletişim:
Telefon: 05439269670
E-posta: sthillmanbusiness@gmail.com

İyi çalışmalar dileriz!
"""

    with open(os.path.join(final_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(info_text)
    print(f"[+] KULLANIM_TALIMATLARI.txt dosyası oluşturuldu.")
    
    # ZIP dosyası oluştur
    print(f"[*] ZIP dosyası oluşturuluyor: {package_name}.zip")
    shutil.make_archive(package_name, 'zip', os.path.dirname(final_dir), os.path.basename(final_dir))
    print(f"[+] ZIP dosyası başarıyla oluşturuldu: {package_name}.zip")
    
    # Çalışma klasörünü temizle
    shutil.rmtree(final_dir)
    print(f"[+] Çalışma klasörü temizlendi.")
    
    print("\n[+] FINAL EXE paketi oluşturma tamamlandı!")
    print(f"[*] Paket: {package_name}.zip")
    print("[*] Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    print("[*] Hem gerçek lisans kodları hem de test kodları çalışacaktır.")
    
    return True

def main():
    print("======== YouTube Mezat Yardımcısı - FINAL EXE OLUŞTURMA ========")
    print("=======================================================")
    
    # PyInstaller'ı kontrol et ve kur
    if not check_pyinstaller():
        print("[-] PyInstaller kurulamadı. İşlem durduruluyor.")
        return
    
    # Gerekli paketleri yükle
    if not install_required_packages():
        print("[-] Gerekli paketler yüklenemedi. İşlem durduruluyor.")
        return
    
    # EXE paketi oluştur
    if create_exe_package():
        print("\n[+] FINAL EXE paketi başarıyla oluşturuldu.")
        print("[*] Kullanıcılar artık EXE'yi çalıştırarak programa giriş yapabilirler.")
        print("[*] Hem gerçek lisans kodları hem de test kodları çalışacaktır.")
    else:
        print("\n[-] EXE paketi oluşturulamadı.")

if __name__ == "__main__":
    main()

