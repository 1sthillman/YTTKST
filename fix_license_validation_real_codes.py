# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_license_validation():
    """
    Lisans doğrulama sorununu düzeltir.
    """
    print("======== YouTube Mezat Yardımcısı - LİSANS DOĞRULAMA DÜZELTMESİ ========")
    print("=======================================================")
    
    # mezaxx.py dosyasını kontrol et
    mezaxx_file = "mezaxx.py"
    if not os.path.exists(mezaxx_file):
        print(f"[-] {mezaxx_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{mezaxx_file}.backup_real_codes"
    shutil.copy2(mezaxx_file, backup_file)
    print(f"[+] {mezaxx_file} dosyası yedeklendi: {backup_file}")
    
    try:
        # Dosyayı oku
        with open(mezaxx_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Sorunlu kod bloğunu bul
        if "# Özel test kodları için kontrol" in content and "if code in [\"TEST456\", \"DEMO123\"]:" in content:
            # Sorunlu kodu düzelt
            old_code = """    try:
        # Özel test kodları için kontrol
        if code in ["TEST456", "DEMO123"]:
            logging.info(f"Test kodu kullanıldı: {code}")
            return True, None
            

        # Yerel doğrulama için dosyadan kontrol et"""
            
            new_code = """    try:
        # Özel test kodları için kontrol
        if code in ["TEST456", "DEMO123"]:
            logging.info(f"Test kodu kullanıldı: {code}")
            return True, None
            
        # Gerçek lisans kodları için doğrulama
        # Yerel doğrulama için dosyadan kontrol et"""
            
            # Kodu değiştir
            modified_content = content.replace(old_code, new_code)
            
            # Lisans kodunu temizleme kısmını düzelt
            old_validation = """        # Lisans kodunu temizle (boşlukları kaldır)
        code = code.strip()
        
        # Yerel doğrulama başarısız olursa False döndür
        valid_codes = [c.strip() for c in data.get("valid_codes", [])]
        if code not in valid_codes:
            logging.warning(f"Lisans kodu bulunamadı: {code}")
            return False, None"""
            
            new_validation = """        # Lisans kodunu temizle (boşlukları kaldır)
        code = code.strip()
        
        # Gerçek lisans kodları için doğrulama
        # Kanal lisanslarını kontrol et
        channel_licenses = {k.lower(): v for k, v in data.get("channel_licenses", {}).items()}
        if channel.lower() in channel_licenses:
            valid_channel_codes = [c.strip() for c in channel_licenses[channel.lower()]]
            if code in valid_channel_codes:
                logging.info(f"Kanal lisans doğrulama başarılı: {channel} - {code}")
                return True, None
        
        # Yerel doğrulama başarısız olursa False döndür
        valid_codes = [c.strip() for c in data.get("valid_codes", [])]
        if code not in valid_codes:
            logging.warning(f"Lisans kodu bulunamadı: {code}")
            return False, None"""
            
            # Kodu değiştir
            modified_content = modified_content.replace(old_validation, new_validation)
            
            # Dosyayı kaydet
            with open(mezaxx_file, "w", encoding="utf-8") as f:
                f.write(modified_content)
            
            print(f"[+] {mezaxx_file} dosyası düzeltildi.")
            print("[+] Lisans doğrulama kodu iyileştirildi.")
            print("[+] Gerçek lisans kodları artık doğru çalışacak.")
            return True
        else:
            print(f"[-] Düzeltilecek kod bloğu bulunamadı!")
            return False
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, mezaxx_file)
        print(f"[*] {mezaxx_file} dosyası yedekten geri yüklendi.")
        return False

def check_license_codes_file():
    """
    license_codes.json dosyasını kontrol eder ve düzeltir.
    """
    print("\n======== license_codes.json DOSYASI KONTROLÜ ========")
    print("===========================================")
    
    license_file = "license_codes.json"
    if not os.path.exists(license_file):
        print(f"[-] {license_file} dosyası bulunamadı!")
        return False
    
    # Yedekleme yap
    backup_file = f"{license_file}.backup_real_codes"
    shutil.copy2(license_file, backup_file)
    print(f"[+] {license_file} dosyası yedeklendi: {backup_file}")
    
    try:
        # Dosyayı oku
        with open(license_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Kanal lisanslarını kontrol et
        channel_licenses = data.get("channel_licenses", {})
        
        # Uzmanbicak kanalı için lisans kodunu kontrol et
        if "uzmanbicak" in channel_licenses:
            uzmanbicak_codes = channel_licenses["uzmanbicak"]
            if "YMY-2024-W3X7-Y2Z8" not in uzmanbicak_codes:
                uzmanbicak_codes.append("YMY-2024-W3X7-Y2Z8")
                print("[+] Uzmanbicak kanalı için YMY-2024-W3X7-Y2Z8 kodu eklendi.")
        else:
            channel_licenses["uzmanbicak"] = ["YMY-2024-W3X7-Y2Z8"]
            print("[+] Uzmanbicak kanalı ve lisans kodu eklendi.")
        
        # Karavil_bıçak kanalı için lisans kodunu kontrol et
        if "karavil_bıçak" in channel_licenses:
            karavil_codes = channel_licenses["karavil_bıçak"]
            if "YMY-2024-J2K7-L4M9" not in karavil_codes:
                karavil_codes.append("YMY-2024-J2K7-L4M9")
                print("[+] Karavil_bıçak kanalı için YMY-2024-J2K7-L4M9 kodu eklendi.")
        else:
            channel_licenses["karavil_bıçak"] = ["YMY-2024-J2K7-L4M9"]
            print("[+] Karavil_bıçak kanalı ve lisans kodu eklendi.")
        
        # Hüseyin_usta_mezat kanalı için lisans kodunu kontrol et
        if "hüseyin_usta_mezat" in channel_licenses:
            huseyin_codes = channel_licenses["hüseyin_usta_mezat"]
            if "YMY-2024-J3K6-L8M2" not in huseyin_codes:
                huseyin_codes.append("YMY-2024-J3K6-L8M2")
                print("[+] Hüseyin_usta_mezat kanalı için YMY-2024-J3K6-L8M2 kodu eklendi.")
        else:
            channel_licenses["hüseyin_usta_mezat"] = ["YMY-2024-J3K6-L8M2"]
            print("[+] Hüseyin_usta_mezat kanalı ve lisans kodu eklendi.")
        
        # Geçerli kodları kontrol et
        valid_codes = data.get("valid_codes", [])
        
        # Gerçek lisans kodlarını ekle
        real_codes = [
            "YMY-2024-W3X7-Y2Z8",  # Uzmanbicak
            "YMY-2024-J2K7-L4M9",  # Karavil_bıçak
            "YMY-2024-J3K6-L8M2",  # Hüseyin_usta_mezat
            "YMY-2024-S7T9-U1V2"   # Görselde görülen kod
        ]
        
        for code in real_codes:
            if code not in valid_codes:
                valid_codes.append(code)
                print(f"[+] Geçerli kodlara eklendi: {code}")
        
        # Dosyayı kaydet
        data["valid_codes"] = valid_codes
        data["channel_licenses"] = channel_licenses
        
        with open(license_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[+] {license_file} dosyası güncellendi.")
        return True
    
    except Exception as e:
        print(f"[-] Hata: {str(e)}")
        # Yedekten geri yükle
        shutil.copy2(backup_file, license_file)
        print(f"[*] {license_file} dosyası yedekten geri yüklendi.")
        return False

if __name__ == "__main__":
    check_license_codes_file()
    fix_license_validation()

