# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import datetime
import json
import zipfile

def create_fixed_package():
    """Tüm gerekli dosyaları içeren düzeltilmiş bir paket oluşturur"""
    # Bugünün tarihi
    today = datetime.datetime.now().strftime("%d%m%Y")
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_COMPLETE_FIXED_EXE_{today}"
    
    # Çalışma klasörü oluştur
    work_dir = package_name
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    
    # Oluşturulan ZIP dosyasını bul
    zip_files = [f for f in os.listdir() if f.startswith("YOUTUBE_MEZAT_YARDIMCISI_FINAL_EXE_") and f.endswith(".zip")]
    
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
    
    # Eksik dosyaları ekle
    # auth_data.json dosyasını oluştur
    auth_data = {
        "youtube_name": "hüseyin_usta_mezat",
        "youtube_url": "https://www.youtube.com/@hüseyin_usta_mezat",
        "authenticated": True,
        "supabase_user_id": "e773632b-72b7-438e-9f7e-04dd69bbf4f6"
    }
    
    with open(os.path.join(work_dir, "auth_data.json"), "w", encoding="utf-8") as f:
        json.dump(auth_data, f, ensure_ascii=False, indent=2)
    print(f"[+] auth_data.json dosyası oluşturuldu.")
    
    # license_codes.json dosyasını oluştur
    license_data = {
        "valid_codes": ["YMY-2024-J3K6-L8M2"],
        "channel_licenses": {
            "hüseyin_usta_mezat": ["YMY-2024-J3K6-L8M2"]
        }
    }
    
    with open(os.path.join(work_dir, "license_codes.json"), "w", encoding="utf-8") as f:
        json.dump(license_data, f, ensure_ascii=False, indent=2)
    print(f"[+] license_codes.json dosyası oluşturuldu.")
    
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

2. Program basladiginda YouTube kanal URL'nizi ve lisans kodunuzu girerek giris yapin.
   - YouTube kanal URL'si: https://www.youtube.com/@hüseyin_usta_mezat
   - Lisans kodu: YMY-2024-J3K6-L8M2

3. Programa ilk kez giris yaptiktan sonra, kullanici bilgileriniz yerel olarak kaydedilecektir.

4. Sistemi kullanirken internet baglantinizin aktif oldugundan emin olun.

5. Programi normal sekilde baslatmak icin kisayol olusturabilirsiniz:
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
    
    print("\n[+] Düzeltilmiş paket oluşturma tamamlandı!")
    print(f"[*] Düzeltilmiş paket: {package_name}.zip")
    print("[*] Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    print("[*] Lisans kodu: YMY-2024-J3K6-L8M2")
    print("[*] YouTube kanal URL'si: https://www.youtube.com/@hüseyin_usta_mezat")
    
    return True

def main():
    print("======== YouTube Mezat Yardımcısı - DÜZELTILMIŞ PAKET OLUŞTURMA ========")
    print("=======================================================")
    
    if create_fixed_package():
        print("\n[+] Düzeltilmiş paket başarıyla oluşturuldu.")
    else:
        print("\n[-] Düzeltilmiş paket oluşturulamadı.")

if __name__ == "__main__":
    main()

