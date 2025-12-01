# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import zipfile
import json
import datetime

def fix_final_package():
    """
    Eksik dosyaları içeren yeni bir paket oluşturur.
    """
    print("======== YouTube Mezat Yardımcısı - FINAL PAKET DÜZELTME ========")
    print("=======================================================")
    
    # Oluşturulan ZIP dosyasını bul
    zip_files = [f for f in os.listdir() if f.startswith("YOUTUBE_MEZAT_YARDIMCISI_FINAL_EXE_") and f.endswith(".zip")]
    
    if not zip_files:
        print("[-] Oluşturulmuş ZIP paketi bulunamadı!")
        return False
    
    # En son oluşturulan ZIP dosyasını al
    latest_zip = sorted(zip_files)[-1]
    print(f"[+] Düzeltilecek paket: {latest_zip}")
    
    # Geçici klasörü oluştur
    temp_dir = "temp_package"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # ZIP dosyasını geçici klasöre çıkart
    print(f"[*] ZIP dosyası çıkartılıyor: {latest_zip}")
    with zipfile.ZipFile(latest_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # EXE klasörünü bul
    exe_dir = None
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".exe"):
                exe_dir = root
                break
        if exe_dir:
            break
    
    if not exe_dir:
        print("[-] EXE klasörü bulunamadı!")
        return False
    
    print(f"[+] EXE klasörü bulundu: {exe_dir}")
    
    # Eksik dosyaları ekle
    required_files = {
        "license_codes.json": "license_codes.json",
        "supabase_config.json": "supabase_config.json",
        "auth_data.json": "auth_data.json"
    }
    
    for dest_file, src_file in required_files.items():
        dest_path = os.path.join(exe_dir, dest_file)
        if not os.path.exists(dest_path):
            if os.path.exists(src_file):
                shutil.copy2(src_file, dest_path)
                print(f"[+] Eksik dosya eklendi: {dest_file}")
            else:
                print(f"[-] Kaynak dosya bulunamadı: {src_file}")
                
                # Eğer kaynak dosya yoksa, oluştur
                if dest_file == "auth_data.json":
                    auth_data = {
                        "youtube_name": "hüseyin_usta_mezat",
                        "youtube_url": "https://www.youtube.com/@hüseyin_usta_mezat",
                        "authenticated": True,
                        "supabase_user_id": "e773632b-72b7-438e-9f7e-04dd69bbf4f6"
                    }
                    with open(dest_path, "w", encoding="utf-8") as f:
                        json.dump(auth_data, f, ensure_ascii=False, indent=2)
                    print(f"[+] {dest_file} dosyası oluşturuldu.")
                
                elif dest_file == "license_codes.json":
                    license_data = {
                        "valid_codes": ["YMY-2024-J3K6-L8M2"],
                        "channel_licenses": {
                            "hüseyin_usta_mezat": ["YMY-2024-J3K6-L8M2"]
                        }
                    }
                    with open(dest_path, "w", encoding="utf-8") as f:
                        json.dump(license_data, f, ensure_ascii=False, indent=2)
                    print(f"[+] {dest_file} dosyası oluşturuldu.")
                
                elif dest_file == "supabase_config.json":
                    supabase_config = {
                        "url": "https://xrrtkiqxnlfbmqikcoic.supabase.co",
                        "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhycnRraXF4bmxmYm1xaWtjb2ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4Mzg0NzUsImV4cCI6MjA3NDQxNDQ3NX0.Z2MF8FR9XEc8wqt939lGiRc9zUsrlJW1hvETxIbdkjg"
                    }
                    with open(dest_path, "w", encoding="utf-8") as f:
                        json.dump(supabase_config, f, ensure_ascii=False, indent=2)
                    print(f"[+] {dest_file} dosyası oluşturuldu.")
    
    # Bugünün tarihi
    today = datetime.datetime.now().strftime("%d%m%Y")
    fixed_package_name = f"YOUTUBE_MEZAT_YARDIMCISI_FIXED_FINAL_EXE_{today}"
    
    # Yeni ZIP dosyası oluştur
    print(f"[*] Düzeltilmiş ZIP dosyası oluşturuluyor: {fixed_package_name}.zip")
    
    # Önce temp_dir içindeki klasörü yeniden adlandır
    inner_dir = os.path.basename(exe_dir)
    os.rename(exe_dir, os.path.join(os.path.dirname(exe_dir), fixed_package_name))
    
    # ZIP oluştur
    shutil.make_archive(fixed_package_name, 'zip', temp_dir)
    print(f"[+] ZIP dosyası başarıyla oluşturuldu: {fixed_package_name}.zip")
    
    # Geçici klasörü temizle
    shutil.rmtree(temp_dir)
    print(f"[+] Geçici klasör temizlendi.")
    
    print("\n[+] Paket düzeltme tamamlandı!")
    print(f"[*] Düzeltilmiş paket: {fixed_package_name}.zip")
    print("[*] Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    print("[*] Lisans kodu: YMY-2024-J3K6-L8M2")
    print("[*] YouTube kanal URL'si: https://www.youtube.com/@hüseyin_usta_mezat")
    
    return True

if __name__ == "__main__":
    fix_final_package()

