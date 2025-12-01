# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import datetime
import tempfile

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

def create_exe_package():
    """mezaxx.py ve save_customer_to_supabase.py dosyalarından EXE paketi oluşturur"""
    print("======== YouTube Mezat Yardimcisi - MUSTERI KAYIT EXE OLUSTURUCU ========")
    print("============================================================")

    # PyInstaller'ı kontrol et
    if not check_pyinstaller():
        print("[-] PyInstaller gerekli. Lutfen manuel olarak kurun: pip install pyinstaller")
        return False

    # Gerekli dosyaları kontrol et
    required_files = ["mezaxx.py", "save_customer_to_supabase.py", "license_codes.json", "supabase_config.json", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"[-] Gerekli dosya bulunamadi: {file}")
            return False

    print("[*] Ses klasoru ve dosyalarin varligi kontrol ediliyor...")
    if os.path.exists("sound"):
        print("[+] Ses klasoru bulundu.")
    else:
        print("[!] Ses klasoru bulunamadi.")

    # Logo kontrolü
    if os.path.exists("LOGO.png"):
        print("[+] LOGO.png bulundu.")
        use_logo = True
    else:
        print("[!] LOGO.png bulunamadi, logo kullanilmayacak.")
        use_logo = False

    # Paket adı oluştur
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_MUSTERI_EXE_v4.0_{datetime.datetime.now().strftime('%d%m%Y')}"
    build_dir = os.path.join(os.getcwd(), "build")
    dist_dir = os.path.join(os.getcwd(), "dist")
    exe_path = os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi", "YouTube_Mezat_Yardimcisi.exe")
    
    # Eski build ve dist klasörlerini temizle
    if os.path.exists(build_dir):
        print("[*] Eski build klasoru temizleniyor...")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"[!] Temizleme hatasi: {e}")
    
    if os.path.exists(dist_dir):
        print("[*] Eski dist klasoru temizleniyor...")
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"[!] Temizleme hatasi: {e}")

    # PyInstaller komutu doğrudan çalıştır
    print("\n[*] PyInstaller ile EXE olusturuluyor...")
    print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
    
    mezaxx_py_path = os.path.join(os.getcwd(), "mezaxx.py")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=YouTube_Mezat_Yardimcisi",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--add-data", f"sound{os.pathsep}sound",
        "--add-data", f"license_codes.json{os.pathsep}.",
        "--add-data", f"supabase_config.json{os.pathsep}.",
        "--add-data", f"save_customer_to_supabase.py{os.pathsep}.",
    ]
    
    # Logo ekle
    if os.path.exists("LOGO.png"):
        cmd.extend(["--add-data", f"LOGO.png{os.pathsep}."])
    
    # Settings ekle
    if os.path.exists("settings.json"):
        cmd.extend(["--add-data", f"settings.json{os.pathsep}."])
    
    # Ek modülleri ekle
    hidden_imports = [
        'customtkinter', 'CTkMessagebox', 'supabase', 'requests', 'websockets',
        'chatdownloader', 'realtime.connection', 'websockets.legacy', 'realtime',
        'PIL.Image', 'PIL.ImageTk', 'babel.numbers'
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Mezaxx.py dosyasını ekle
    cmd.append(mezaxx_py_path)
    
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
    
    # dist klasöründeki YouTube_Mezat_Yardimcisi klasörünü kopyala
    shutil.copytree(os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi"), final_dir)

    # Bilgi dosyası oluştur
    info_text = """
YouTube Mezat Yardimcisi - KULLANIM TALIMATLARI:

1. YouTube_Mezat_Yardimcisi.exe dosyasina cift tiklayarak programi baslatin.

2. Program basladiginda YouTube kanal URL'nizi ve lisans kodunuzu girerek giris yapin.

3. Programa ilk kez giris yaptiktan sonra, kullanici bilgileriniz yerel olarak kaydedilecektir.

4. Sistemi kullanirken internet baglantinizin aktif oldugundan emin olun.

5. Programi normal sekilde baslatmak icin kisayol olusturabilirsiniz:
   - YouTube_Mezat_Yardimcisi.exe dosyasina sag tiklayin
   - "Masaustune kisayol olustur" secenegini tiklayin

YENI OZELLIK - MUSTERI BILGILERINI KAYDETME:

Bu surumde, musteri bilgilerini hem yerel olarak hem de Supabase veritabanina kaydedebilirsiniz:

1. Menuden "Odeme Yapanlar" secenegine tiklayin.
2. Acilan pencerede, kullanici ekleyebilir veya mevcut kullanicilari duzenleyebilirsiniz.
3. Her kullanici icin:
   - YouTube Kullanici Adi
   - Ad Soyad
   - Telefon
   - Adres
   bilgilerini girebilirsiniz.
4. "Kaydet" butonuna tikladiginizda, bilgiler hem yerel olarak kaydedilecek hem de Supabase veritabanina gonderilecektir.
5. Internet baglantiniz olmasa bile bilgiler yerel olarak kaydedilir, internet baglantisi saglandiginda otomatik olarak Supabase'e gonderilir.

Onemli Notlar:
- Bu program, YouTube canli yayinlarinizdaki mezat katilimcilarini takip etmek icin tasarlanmistir.
- Lisans kodunuz gecerli oldugu surece programi kullanabilirsiniz.
- Kullanim sirasinda herhangi bir sorun yasarsaniz, program yoneticinizle iletisime gecin.

Iletisim:
Telefon: 05439269670
E-posta: sthillmanbusiness@gmail.com
"""

    with open(os.path.join(final_dir, "KULLANIM_TALIMATLARI.txt"), "w") as f:
        f.write(info_text)

    # ZIP olarak paketleyelim
    print(f"\n[*] Final paketi '{package_name}' klasorune olusturuldu.")
    print(f"[*] ZIP dosyasi olusturuluyor...")
    
    # ZIP oluştur
    zip_file_name = f"{package_name}.zip"
    try:
        shutil.make_archive(package_name, 'zip', final_dir)
        print(f"[+] ZIP dosyasi basariyla olusturuldu: {zip_file_name}")
    except Exception as e:
        print(f"[-] ZIP olusturma hatasi: {e}")
        return False

    print("\n============================================================")
    print("*** MUSTERI KAYIT EXE PAKETI TAMAMLANDI! ***")
    print("============================================================")
    print(f"- EXE Klasoru: {package_name}")
    print(f"- ZIP: {zip_file_name}")
    print("\n- MUSTERILERINIZE GONDERMEK ICIN:")
    print(f"  1. {zip_file_name} dosyasini gonderin")
    print("  2. Musterilerinize su talimatlari verin:")
    print("     - ZIP dosyasini acin")
    print("     - YouTube_Mezat_Yardimcisi.exe dosyasina cift tiklayin")
    print("\n[+] TEK TIKLA CALISAN EXE COZUMU HAZIR! Musterilerinize gondermeye hazir.")
    
    return True

if __name__ == "__main__":
    create_exe_package()
    input("\nDevam etmek icin Enter tusuna basin...")

