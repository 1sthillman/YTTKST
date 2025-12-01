# -*- coding: utf-8 -*-
import os
import json
import sys
import shutil

def update_license_codes():
    """
    license_codes.json dosyasını güncelleyerek Uzmanbicak için lisans kodunu ekler.
    """
    print("======== YouTube Mezat Yardımcısı - LİSANS KODU GÜNCELLEME ========")
    print("============================================================")
    
    # license_codes.json dosyasını kontrol et
    license_file = "license_codes.json"
    if not os.path.exists(license_file):
        print(f"[-] {license_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{license_file}.backup2"
    shutil.copy2(license_file, backup_file)
    print(f"[+] {license_file} dosyası yedeklendi: {backup_file}")
    
    # Dosyayı oku
    try:
        with open(license_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Mevcut kodları göster
        valid_codes = data.get("valid_codes", [])
        print(f"[*] Mevcut lisans kodu sayısı: {len(valid_codes)}")
        
        # Uzmanbicak için lisans kodu ekle
        license_code = "YMY-2024-W3X7-Y2Z8"  # Resimde görülen kod
        uzmanbicak_channel = "Uzmanbicak"
        
        # Lisans kodunu kontrol et
        if license_code not in valid_codes:
            print(f"[*] Lisans kodu '{license_code}' valid_codes listesinde bulunamadı.")
            print(f"[*] Lisans kodu zaten listede mevcut olabilir, kontrol ediliyor...")
            
            # Lisans kodu zaten listede var mı?
            found = False
            for code in valid_codes:
                if code.strip() == license_code.strip():
                    found = True
                    print(f"[+] Lisans kodu '{license_code}' zaten listede mevcut.")
                    break
            
            if not found:
                # Lisans kodunu ekle
                valid_codes.append(license_code)
                data["valid_codes"] = valid_codes
                print(f"[+] Lisans kodu '{license_code}' valid_codes listesine eklendi.")
        else:
            print(f"[+] Lisans kodu '{license_code}' zaten valid_codes listesinde mevcut.")
        
        # Kanal lisanslarını kontrol et
        channel_licenses = data.get("channel_licenses", {})
        
        # Kanal adını normalize et
        normalized_channel = uzmanbicak_channel.lower()
        
        # Kanal lisansı var mı?
        if normalized_channel in channel_licenses:
            # Kanal lisansında kod var mı?
            if license_code not in channel_licenses[normalized_channel]:
                channel_licenses[normalized_channel].append(license_code)
                print(f"[+] Lisans kodu '{license_code}' kanal '{uzmanbicak_channel}' için eklendi.")
            else:
                print(f"[+] Lisans kodu '{license_code}' zaten kanal '{uzmanbicak_channel}' için tanımlı.")
        else:
            # Yeni kanal lisansı oluştur
            channel_licenses[normalized_channel] = [license_code]
            print(f"[+] Yeni kanal lisansı oluşturuldu: '{uzmanbicak_channel}' - '{license_code}'")
        
        # Kanal lisanslarını güncelle
        data["channel_licenses"] = channel_licenses
        
        # Dosyayı kaydet
        with open(license_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[+] {license_file} dosyası güncellendi.")
        print("\n[*] Kanal URL'si: https://www.youtube.com/@Uzmanbicak")
        print(f"[*] Lisans kodu: {license_code}")
        return True
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, license_file)
        print(f"[*] {license_file} dosyası yedekten geri yüklendi.")
        return False

if __name__ == "__main__":
    update_license_codes()

