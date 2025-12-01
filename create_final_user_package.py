# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import datetime
import json
import zipfile

def create_user_package():
    """Boş auth_data.json ile kullanıcı paketi oluşturur"""
    # Bugünün tarihi
    today = datetime.datetime.now().strftime("%d%m%Y")
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_USER_PACKAGE_{today}"
    
    # Çalışma klasörü oluştur
    work_dir = package_name
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    
    # Oluşturulan ZIP dosyasını bul
    zip_files = [f for f in os.listdir() if f.startswith("YOUTUBE_MEZAT_YARDIMCISI_") and f.endswith(".zip")]
    
    if not zip_files:
        print("[-] Oluşturulmuş ZIP paketi bulunamadı!")
        return False
    
    # En son oluşturulan ZIP dosyasını al
    latest_zip = sorted(zip_files)[-1]
    print(f"[+] Kaynak paket: {latest_zip}")
    
    # Geçici klasör oluştur
    temp_dir = "temp_extract"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # ZIP dosyasını geçici klasöre çıkart
    print(f"[*] ZIP dosyası çıkartılıyor: {latest_zip}")
    with zipfile.ZipFile(latest_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # EXE dosyasını ve diğer dosyaları bul
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".exe"):
                # EXE dosyasını ve diğer dosyaları çalışma klasörüne kopyala
                for item in os.listdir(root):
                    s = os.path.join(root, item)
                    d = os.path.join(work_dir, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
                        print(f"[+] Dosya kopyalandı: {item}")
                    else:
                        shutil.copytree(s, d)
                        print(f"[+] Klasör kopyalandı: {item}")
                break
    
    # Geçici klasörü temizle
    shutil.rmtree(temp_dir)
    
    # Boş auth_data.json dosyasını oluştur
    auth_data = {
        "youtube_name": "",
        "youtube_url": "",
        "authenticated": False,
        "supabase_user_id": ""
    }
    
    with open(os.path.join(work_dir, "auth_data.json"), "w", encoding="utf-8") as f:
        json.dump(auth_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Boş auth_data.json dosyası oluşturuldu.")
    
    # license_codes.json dosyasını kopyala
    if os.path.exists("license_codes.json"):
        shutil.copy2("license_codes.json", os.path.join(work_dir, "license_codes.json"))
        print(f"[+] license_codes.json dosyası kopyalandı.")
    else:
        print(f"[-] license_codes.json dosyası bulunamadı!")
        return False
    
    # supabase_config.json dosyasını kopyala
    if os.path.exists("supabase_config.json"):
        shutil.copy2("supabase_config.json", os.path.join(work_dir, "supabase_config.json"))
        print(f"[+] supabase_config.json dosyası kopyalandı.")
    else:
        # supabase_config.json dosyasını oluştur
        supabase_config = {
            "url": "https://xrrtkiqxnlfbmqikcoic.supabase.co",
            "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhycnRraXF4bmxmYm1xaWtjb2ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4Mzg0NzUsImV4cCI6MjA3NDQxNDQ3NX0.Z2MF8FR9XEc8wqt939lGiRc9zUsrlJW1hvETxIbdkjg"
        }
        
        with open(os.path.join(work_dir, "supabase_config.json"), "w", encoding="utf-8") as f:
            json.dump(supabase_config, f, ensure_ascii=False, indent=2)
        print(f"[+] supabase_config.json dosyası oluşturuldu.")
    
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

6. Programi normal sekilde baslatmak icin kisayol olusturabilirsiniz:
   - YouTube_Mezat_Yardimcisi.exe dosyasina sag tiklayin
   - "Masaustune kisayol olustur" secenegini tiklayin

OZELLIKLER:

1. YouTube Canli Yayin Takibi:
   - Canli yayin URL'sini girin ve "Baslat" butonuna tiklayin
   - Program otomatik olarak chat mesajlarini takip edecektir

2. Teklif Takibi:
   - Program chat mesajlarindaki teklifleri otomatik olarak tespit eder
   - Teklifler listelenir ve en yuksek teklif gosterilir

3. Yazici Ayarlari:
   - Farkli yazici tipleri icin destek (Standart, Thermal, Etiket)
   - Kagit boyutlari ve kenar bosluklari ayarlari
   - Yazi tipi ve boyutu ayarlari

4. Odeme Yapan Kullanicilar:
   - Odeme yapan kullanicilarin bilgilerini kaydedebilirsiniz
   - Kullanici bilgileri hem yerel hem de Supabase veritabaninda saklanir

Onemli Notlar:
- Bu program, YouTube canli yayinlarinizdaki mezat katilimcilarini takip etmek icin tasarlanmistir.
- Lisans kodunuz gecerli oldugu surece programi kullanabilirsiniz.
- Kullanim sirasinda herhangi bir sorun yasarsaniz, program yoneticinizle iletisime gecin.

Iletisim:
Telefon: 05439269670
E-posta: sthillmanbusiness@gmail.com
"""

    with open(os.path.join(work_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(info_text)
    print(f"[+] KULLANIM_TALIMATLARI.txt dosyası oluşturuldu.")
    
    # ZIP dosyası oluştur
    print(f"[*] ZIP dosyası oluşturuluyor: {package_name}.zip")
    shutil.make_archive(package_name, 'zip', work_dir)
    print(f"[+] ZIP dosyası başarıyla oluşturuldu: {package_name}.zip")
    
    # Çalışma klasörünü temizle
    shutil.rmtree(work_dir)
    print(f"[+] Çalışma klasörü temizlendi.")
    
    print("\n[+] Kullanıcı paketi oluşturma tamamlandı!")
    print(f"[*] Kullanıcı paketi: {package_name}.zip")
    print("[*] Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    print("[*] Her kullanıcı kendi YouTube kanal URL'sini ve lisans kodunu girebilecek.")
    
    return True

def main():
    print("======== YouTube Mezat Yardımcısı - KULLANICI PAKETİ OLUŞTURMA ========")
    print("=======================================================")
    
    if create_user_package():
        print("\n[+] Kullanıcı paketi başarıyla oluşturuldu.")
    else:
        print("\n[-] Kullanıcı paketi oluşturulamadı.")

if __name__ == "__main__":
    main()

