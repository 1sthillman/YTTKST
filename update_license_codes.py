# -*- coding: utf-8 -*-
import os
import json
import sys
import shutil

def update_license_codes():
    """
    license_codes.json dosyasını güncelleyerek müşteri tarafından girilen lisans kodunu ekler.
    """
    print("======== YouTube Mezat Yardımcısı - LİSANS KODU GÜNCELLEME ========")
    print("============================================================")
    
    # license_codes.json dosyasını kontrol et
    license_file = "license_codes.json"
    if not os.path.exists(license_file):
        print(f"[-] {license_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{license_file}.backup"
    shutil.copy2(license_file, backup_file)
    print(f"[+] {license_file} dosyası yedeklendi: {backup_file}")
    
    # Dosyayı oku
    try:
        with open(license_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Mevcut kodları göster
        valid_codes = data.get("valid_codes", [])
        print(f"[*] Mevcut lisans kodu sayısı: {len(valid_codes)}")
        
        # Müşteri tarafından girilen kodu al
        print("\n[*] Müşteri tarafından girilen lisans kodu:")
        customer_code = input("Lisans Kodu: ").strip()
        
        if not customer_code:
            print("[-] Lisans kodu girilmedi!")
            return False
        
        # Kodun mevcut olup olmadığını kontrol et
        if customer_code in valid_codes:
            print(f"[+] '{customer_code}' kodu zaten lisans listesinde mevcut.")
        else:
            # Yeni kodu ekle
            valid_codes.append(customer_code)
            data["valid_codes"] = valid_codes
            
            # Dosyaya kaydet
            with open(license_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[+] '{customer_code}' kodu başarıyla lisans listesine eklendi!")
        
        # Özel kanal lisansı eklemek ister misin?
        print("\n[*] Özel kanal lisansı eklemek ister misiniz? (e/h)")
        add_channel = input().strip().lower()
        
        if add_channel == "e":
            channel = input("YouTube Kanal Adı: ").strip()
            if channel:
                channel_licenses = data.get("channel_licenses", {})
                if channel.lower() not in channel_licenses:
                    channel_licenses[channel.lower()] = []
                
                if customer_code not in channel_licenses[channel.lower()]:
                    channel_licenses[channel.lower()].append(customer_code)
                    data["channel_licenses"] = channel_licenses
                    
                    # Dosyaya kaydet
                    with open(license_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"[+] '{customer_code}' kodu '{channel}' kanalına özel lisans olarak eklendi!")
                else:
                    print(f"[+] '{customer_code}' kodu zaten '{channel}' kanalına özel lisans olarak ekli.")
        
        print("\n[+] Lisans kodu güncelleme işlemi tamamlandı!")
        return True
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, license_file)
        print(f"[*] {license_file} dosyası yedekten geri yüklendi.")
        return False

def create_test_license_file():
    """
    Test için basit bir license_codes.json dosyası oluşturur.
    """
    test_code = "YMY-2024-A3B6-C8D1"
    test_channel = "hüseyin_usta_mezat"
    
    data = {
        "valid_codes": [test_code],
        "channel_licenses": {
            test_channel.lower(): [test_code]
        }
    }
    
    test_file = "test_license_codes.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[+] Test lisans dosyası oluşturuldu: {test_file}")
    print(f"[+] Test lisans kodu: {test_code}")
    print(f"[+] Test kanal adı: {test_channel}")

if __name__ == "__main__":
    choice = input("1. Lisans kodunu güncelle\n2. Test lisans dosyası oluştur\nSeçiminiz (1/2): ")
    if choice == "1":
        update_license_codes()
    elif choice == "2":
        create_test_license_file()
    else:
        print("Geçersiz seçim!")

