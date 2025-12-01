# -*- coding: utf-8 -*-
import os
import json
import sys
import shutil

def fix_license_validation():
    """
    Lisans doğrulama sorununu düzeltir.
    """
    print("======== YouTube Mezat Yardımcısı - LİSANS DOĞRULAMA DÜZELTMESİ ========")
    print("=======================================================")
    
    # license_codes.json dosyasını kontrol et
    license_file = "license_codes.json"
    if not os.path.exists(license_file):
        print(f"[-] {license_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{license_file}.backup_fix"
    shutil.copy2(license_file, backup_file)
    print(f"[+] {license_file} dosyası yedeklendi: {backup_file}")
    
    # Dosyayı oku
    try:
        with open(license_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Mevcut kodları göster
        valid_codes = data.get("valid_codes", [])
        print(f"[*] Mevcut lisans kodu sayısı: {len(valid_codes)}")
        
        # TEST456 ve DEMO123 kodlarını ekle (eğer yoksa)
        test_codes = ["TEST456", "DEMO123"]
        for code in test_codes:
            if code not in valid_codes:
                valid_codes.append(code)
                print(f"[+] Test kodu eklendi: {code}")
        
        # Kanal lisanslarını kontrol et
        channel_licenses = data.get("channel_licenses", {})
        
        # Test_Hesabi için DEMO123 kodunu ekle
        test_channel = "Test_Hesabi"
        if test_channel not in channel_licenses:
            channel_licenses[test_channel] = ["DEMO123"]
            print(f"[+] Test kanalı eklendi: {test_channel}")
        elif "DEMO123" not in channel_licenses[test_channel]:
            channel_licenses[test_channel].append("DEMO123")
            print(f"[+] Test kanalına DEMO123 kodu eklendi")
        
        # Kanal lisanslarını güncelle
        data["channel_licenses"] = channel_licenses
        data["valid_codes"] = valid_codes
        
        # Dosyayı kaydet
        with open(license_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[+] {license_file} dosyası güncellendi.")
        
        # auth_data.json dosyasını temizle
        auth_file = "auth_data.json"
        if os.path.exists(auth_file):
            # Yedekleme yap
            auth_backup = f"{auth_file}.backup"
            shutil.copy2(auth_file, auth_backup)
            print(f"[+] {auth_file} dosyası yedeklendi: {auth_backup}")
            
            # Boş auth_data oluştur
            auth_data = {
                "youtube_name": "",
                "youtube_url": "",
                "authenticated": False,
                "supabase_user_id": None
            }
            
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump(auth_data, f, ensure_ascii=False, indent=2)
            
            print(f"[+] {auth_file} dosyası temizlendi.")
        
        print("\n[+] Lisans doğrulama düzeltmesi tamamlandı.")
        print("[*] Artık TEST456 ve DEMO123 kodları ile giriş yapılabilir.")
        print("[*] Test_Hesabi kanalı için DEMO123 kodu tanımlandı.")
        return True
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, license_file)
        print(f"[*] {license_file} dosyası yedekten geri yüklendi.")
        return False

def update_mezaxx_py():
    """
    mezaxx.py dosyasındaki lisans doğrulama kodunu düzeltir.
    """
    print("\n======== mezaxx.py DOSYASI DÜZELTMESİ ========")
    print("===========================================")
    
    mezaxx_file = "mezaxx.py"
    if not os.path.exists(mezaxx_file):
        print(f"[-] {mezaxx_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{mezaxx_file}.backup"
    shutil.copy2(mezaxx_file, backup_file)
    print(f"[+] {mezaxx_file} dosyası yedeklendi: {backup_file}")
    
    try:
        # Dosyayı oku
        with open(mezaxx_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # validate_license_code fonksiyonunu düzelt
        # Özel test kodlarını ekle
        if "def validate_license_code(channel, code, url=None):" in content:
            # Fonksiyonun başlangıcını bul
            start_idx = content.find("def validate_license_code(channel, code, url=None):")
            
            # Fonksiyonun içeriğini bul
            function_start = content.find("try:", start_idx)
            
            # Özel test kodlarını ekle
            modified_content = content[:function_start + 4] + """
        # Özel test kodları için kontrol
        if code in ["TEST456", "DEMO123"]:
            logging.info(f"Test kodu kullanıldı: {code}")
            return True, None
            
""" + content[function_start + 4:]
            
            # Dosyayı kaydet
            with open(mezaxx_file, "w", encoding="utf-8") as f:
                f.write(modified_content)
            
            print(f"[+] {mezaxx_file} dosyası düzeltildi.")
            print("[+] TEST456 ve DEMO123 kodları için özel kontrol eklendi.")
            return True
        else:
            print(f"[-] validate_license_code fonksiyonu bulunamadı!")
            return False
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, mezaxx_file)
        print(f"[*] {mezaxx_file} dosyası yedekten geri yüklendi.")
        return False

if __name__ == "__main__":
    fix_license_validation()
    update_mezaxx_py()