# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı - Tam Paket EXE Oluşturucu
Bu script, YouTube Mezat Yardımcısı uygulaması için tam bir EXE paketi oluşturur.
Supabase entegrasyonu ve lisans doğrulaması tam olarak çalışır.
"""
import os
import sys
import subprocess
import shutil
import datetime
import tempfile
import zipfile
import json
import logging

# Loglama ayarları
logging.basicConfig(
    filename="exe_builder.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def check_pyinstaller():
    """PyInstaller kurulu mu kontrol eder, yoksa kurar."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], check=True, capture_output=True)
        print("[+] PyInstaller zaten kurulu.")
        return True
    except subprocess.CalledProcessError:
        print("[*] PyInstaller kuruluyor...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==5.13.0"], check=True)
            print("[+] PyInstaller başarıyla kuruldu.")
            return True
        except subprocess.CalledProcessError:
            print("[-] PyInstaller kurulamadı.")
            return False

def check_and_install_required_packages():
    """Gerekli paketleri kontrol eder ve kurar"""
    packages = [
        "customtkinter>=5.2.1",
        "CTkMessagebox>=2.5",
        "Pillow>=10.0.0",
        "pygame>=2.5.2",
        "requests>=2.31.0",
        "chat-downloader>=0.2.7",
        "supabase>=2.3.0",
        "websockets>=12.0.0",
        "websocket-client>=1.6.4",
        "babel>=2.14.0",
        "beautifulsoup4>=4.12.2"
    ]
    
    print("[*] Gerekli paketler kontrol ediliyor ve yükleniyor...")
    for package in packages:
        try:
            package_name = package.split(">=")[0]
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--upgrade"], check=True)
            print(f"[+] {package_name} yüklendi.")
        except subprocess.CalledProcessError as e:
            print(f"[-] {package} yüklenemedi: {e}")
            return False
    return True

def validate_supabase_connection():
    """Supabase bağlantısını doğrular ve customers tablosunu kontrol eder"""
    print("[*] Supabase bağlantısı doğrulanıyor...")
    
    # supabase_config.json dosyasını kontrol et
    if not os.path.exists("supabase_config.json"):
        print("[-] supabase_config.json dosyası bulunamadı!")
        
        # Dosyayı oluştur
        config = {
            "url": "https://xrrtkiqxnlfbmqikcoic.supabase.co",
            "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhycnRraXF4bmxmYm1xaWtjb2ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4Mzg0NzUsImV4cCI6MjA3NDQxNDQ3NX0.Z2MF8FR9XEc8wqt939lGiRc9zUsrlJW1hvETxIbdkjg"
        }
        with open("supabase_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("[+] supabase_config.json dosyası oluşturuldu.")
    
    # Test bağlantısı oluştur
    try:
        # Test python kodu oluştur
        test_code = """
import json
from supabase import create_client

# Supabase yapılandırması
with open("supabase_config.json", encoding="utf-8") as f:
    config = json.load(f)

# İstemciyi oluştur
supabase = create_client(config["url"], config["key"])

# Test sorgusu çalıştır
response = supabase.table("customers").select("count").execute()
print("Supabase bağlantısı başarılı!")
"""
        
        # Geçici dosya oluştur
        temp_file = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path = temp_file.name
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(test_code)
        
        # Test kodunu çalıştır
        try:
            subprocess.run([sys.executable, temp_file_path], check=True, capture_output=True)
            print("[+] Supabase bağlantısı başarılı.")
            os.unlink(temp_file_path)
            return True
        except subprocess.CalledProcessError:
            print("[-] Supabase bağlantısı başarısız.")
            os.unlink(temp_file_path)
            return False
    except Exception as e:
        print(f"[-] Supabase bağlantısı test edilirken hata: {e}")
        return False

def optimize_license_validation():
    """Lisans doğrulama sistemini optimize eder"""
    print("[*] Lisans doğrulama sistemi optimize ediliyor...")
    
    # auth_data.json dosyasını kontrol et
    if not os.path.exists("auth_data.json"):
        # Örnek auth_data oluştur
        auth_data = {
            "youtube_name": "mezat_yardimcisi",
            "youtube_url": "https://www.youtube.com/@mezat_yardimcisi",
            "authenticated": True,
            "supabase_user_id": "e773632b-72b7-438e-9f7e-04dd69bbf4f6"
        }
        
        with open("auth_data.json", "w", encoding="utf-8") as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)
        print("[+] auth_data.json dosyası oluşturuldu.")
        
        # Yedekleme dosyası oluştur
        with open("auth_data.json.backup", "w", encoding="utf-8") as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)
    
    # license_codes.json dosyasını kontrol et
    if not os.path.exists("license_codes.json"):
        print("[-] license_codes.json dosyası bulunamadı!")
        return False
    
    # license_codes.json dosyasını oku
    try:
        with open("license_codes.json", "r", encoding="utf-8") as f:
            license_data = json.load(f)
        
        # Lisans kodlarını temizle (boşluk ve özel karakterleri kaldır)
        valid_codes = license_data.get("valid_codes", [])
        cleaned_valid_codes = [code.strip() for code in valid_codes]
        license_data["valid_codes"] = cleaned_valid_codes
        
        # Kanal lisanslarını temizle
        channel_licenses = license_data.get("channel_licenses", {})
        cleaned_channel_licenses = {}
        for channel, codes in channel_licenses.items():
            cleaned_channel_licenses[channel.lower()] = [code.strip() for code in codes]
        license_data["channel_licenses"] = cleaned_channel_licenses
        
        # Test lisansı ekle
        default_license_code = "YMY-2024-TEST-CODE"
        if default_license_code not in cleaned_valid_codes:
            cleaned_valid_codes.append(default_license_code)
        
        # Test kanalını ekle
        if "mezat_yardimcisi" not in cleaned_channel_licenses:
            cleaned_channel_licenses["mezat_yardimcisi"] = [default_license_code]
            
        # Güncellemeyi kaydet
        license_data["valid_codes"] = cleaned_valid_codes
        license_data["channel_licenses"] = cleaned_channel_licenses
        
        # Dosyayı kaydet
        with open("license_codes.json", "w", encoding="utf-8") as f:
            json.dump(license_data, f, ensure_ascii=False, indent=2)
        
        # Yedekleme dosyası oluştur
        with open("license_codes.json.backup", "w", encoding="utf-8") as f:
            json.dump(license_data, f, ensure_ascii=False, indent=2)
        
        print("[+] license_codes.json dosyası optimize edildi.")
        return True
    except Exception as e:
        print(f"[-] Lisans dosyası optimize edilirken hata: {e}")
        return False

def create_comprehensive_exe():
    """PyInstaller ile kapsamlı bir EXE paketi oluşturur"""
    # Bugünün tarihi
    today = datetime.datetime.now().strftime("%d%m%Y")
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_COMPLETE_EXE_{today}"
    
    # Gerekli klasörleri oluştur
    dist_dir = os.path.join(os.getcwd(), "dist")
    build_dir = os.path.join(os.getcwd(), "build")
    
    # Önceki build klasörlerini temizle
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            print(f"[*] Temizleniyor: {dir_path}")
            shutil.rmtree(dir_path)
    
    # Gerekli dosyaları kontrol et
    required_files = ["license_codes.json", "supabase_config.json", "mezaxx.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"[-] {file} dosyası bulunamadı!")
            return False
    
    # Ses dosyaları klasörünü kontrol et
    if not os.path.exists("sound"):
        os.makedirs("sound")
        print("[+] 'sound' klasörü oluşturuldu.")
    
    # PyInstaller spec dosyası içeriği
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Tüm gerekli modülleri topla
chat_downloader_datas, chat_downloader_binaries, chat_downloader_hiddenimports = collect_all('chat_downloader')
websockets_datas, websockets_binaries, websockets_hiddenimports = collect_all('websockets')
customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all('customtkinter')
supabase_datas, supabase_binaries, supabase_hiddenimports = collect_all('supabase')
babel_datas, babel_binaries, babel_hiddenimports = collect_all('babel')
ctkmessagebox_datas, ctkmessagebox_binaries, ctkmessagebox_hiddenimports = collect_all('CTkMessagebox')
requests_datas, requests_binaries, requests_hiddenimports = collect_all('requests')
pillow_datas, pillow_binaries, pillow_hiddenimports = collect_all('PIL')
pygame_datas, pygame_binaries, pygame_hiddenimports = collect_all('pygame')
bs4_datas, bs4_binaries, bs4_hiddenimports = collect_all('bs4')
websocket_datas, websocket_binaries, websocket_hiddenimports = collect_all('websocket')

# Tüm gizli bağımlılıkları birleştir
all_hiddenimports = []
all_hiddenimports.extend(chat_downloader_hiddenimports)
all_hiddenimports.extend(websockets_hiddenimports)
all_hiddenimports.extend(customtkinter_hiddenimports)
all_hiddenimports.extend(supabase_hiddenimports)
all_hiddenimports.extend(babel_hiddenimports)
all_hiddenimports.extend(ctkmessagebox_hiddenimports)
all_hiddenimports.extend(requests_hiddenimports)
all_hiddenimports.extend(pillow_hiddenimports)
all_hiddenimports.extend(pygame_hiddenimports)
all_hiddenimports.extend(bs4_hiddenimports)
all_hiddenimports.extend(websocket_hiddenimports)
all_hiddenimports.extend([
    'websocket', 'websocket-client', 'realtime', 'realtime.connection',
    'chat_downloader', 'chat_downloader.sites', 'chat_downloader.sites.youtube',
    'babel.numbers', 'babel.dates', 'babel.core',
    'json', 'os', 'time', 'threading', 'datetime', 'socket'
])

# Tüm veri dosyalarını birleştir
all_datas = []
all_datas.extend(chat_downloader_datas)
all_datas.extend(websockets_datas)
all_datas.extend(customtkinter_datas)
all_datas.extend(supabase_datas)
all_datas.extend(babel_datas)
all_datas.extend(ctkmessagebox_datas)
all_datas.extend(requests_datas)
all_datas.extend(pillow_datas)
all_datas.extend(pygame_datas)
all_datas.extend(bs4_datas)
all_datas.extend(websocket_datas)

# Kendi veri dosyalarımızı ekle
all_datas.extend([
    ('sound', 'sound'),
    ('license_codes.json', '.'),
    ('supabase_config.json', '.'),
    ('auth_data.json', '.'),
])

if os.path.exists('printer_settings.py'):
    all_datas.append(('printer_settings.py', '.'))
if os.path.exists('LOGO.png'):
    all_datas.append(('LOGO.png', '.'))
if os.path.exists('LOGO.ico'):
    all_datas.append(('LOGO.ico', '.'))
if os.path.exists('settings.json'):
    all_datas.append(('settings.json', '.'))
if os.path.exists('save_customer_to_supabase.py'):
    all_datas.append(('save_customer_to_supabase.py', '.'))
if os.path.exists('improved_chat_downloader.py'):
    all_datas.append(('improved_chat_downloader.py', '.'))
if os.path.exists('license_usage.json'):
    all_datas.append(('license_usage.json', '.'))

a = Analysis(
    ['mezaxx.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTube_Mezat_Yardimcisi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='LOGO.ico' if os.path.exists('LOGO.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTube_Mezat_Yardimcisi',
)
"""
    
    spec_file = os.path.join(os.getcwd(), "YouTube_Mezat_Yardimcisi_Complete.spec")
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"[+] Spec dosyası oluşturuldu: {spec_file}")

    # PyInstaller komutu
    print("\n[*] PyInstaller ile EXE oluşturuluyor...")
    print("Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        spec_file,
        "--clean",
        "--noconfirm"
    ]
    
    # PyInstaller'ı çalıştır
    try:
        print(f"[*] Komut: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("\n[+] EXE dosyası başarıyla oluşturuldu.")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] EXE oluşturma hatası: {e}")
        return False

    # Çıktı klasörünü kontrol et
    exe_path = os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi", "YouTube_Mezat_Yardimcisi.exe")
    if not os.path.exists(exe_path):
        print(f"[-] Beklenen EXE dosyası bulunamadı: {exe_path}")
        return False

    # Final klasörü oluştur
    final_dir = os.path.join(os.getcwd(), package_name)
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    
    # dist klasöründeki YouTube_Mezat_Yardimcisi klasörünü kopyala
    shutil.copytree(os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi"), final_dir)
    
    # Dosya izinlerini güncelle
    try:
        for root, dirs, files in os.walk(final_dir):
            for file in files:
                os.chmod(os.path.join(root, file), 0o755)
    except Exception as e:
        print(f"[-] Dosya izinleri güncellenirken hata: {e}")

    # Bilgi dosyası oluştur
    info_text = """
YouTube Mezat Yardımcısı - KULLANIM TALIMATLARI

1. YouTube_Mezat_Yardimcisi.exe dosyasına çift tıklayarak programı başlatın.

2. Program başladığında YouTube kanal URL'nizi ve lisans kodunuzu girerek giriş yapın.
   - Lisans kodunu tam olarak yazdığınızdan emin olun
   - Lisans kodundaki boşluk veya özel karakterlere dikkat edin

3. Programa ilk kez giriş yaptıktan sonra, kullanıcı bilgileriniz yerel olarak kaydedilecektir.

4. Sistemi kullanırken internet bağlantınızın aktif olduğundan emin olun.

5. Programı normal şekilde başlatmak için kısayol oluşturabilirsiniz:
   - YouTube_Mezat_Yardimcisi.exe dosyasına sağ tıklayın
   - "Masaüstüne kısayol oluştur" seçeneğini tıklayın

ÖZELLİKLER:

1. YouTube Canlı Yayın Takibi:
   - Canlı yayın URL'sini girin ve "Başlat" butonuna tıklayın
   - Program otomatik olarak chat mesajlarını takip edecektir

2. Teklif Takibi:
   - Program chat mesajlarındaki teklifleri otomatik olarak tespit eder
   - Teklifler listelenir ve en yüksek teklif gösterilir

3. Yazıcı Ayarları:
   - Farklı yazıcı tipleri için destek (Standart, Termal, Etiket)
   - Kağıt boyutları ve kenar boşlukları ayarları
   - Yazı tipi ve boyutu ayarları

4. Ödeme Yapan Kullanıcılar:
   - Ödeme yapan kullanıcıların bilgilerini kaydedebilirsiniz
   - Kullanıcı bilgileri hem yerel hem de Supabase veritabanında saklanır

5. Supabase Müşteri Entegrasyonu:
   - Müşteri bilgileriniz otomatik olarak Supabase veritabanına kaydedilir
   - İnternet bağlantısı olmadığında bile program çalışmaya devam eder
   - Bağlantı sağlandığında bekleyen veriler otomatik olarak senkronize edilir

Önemli Notlar:
- Bu program, YouTube canlı yayınlarınızdaki mezat katılımcılarını takip etmek için tasarlanmıştır.
- Lisans kodunuz geçerli olduğu sürece programı kullanabilirsiniz.
- Kullanım sırasında herhangi bir sorun yaşarsanız, program yöneticinizle iletişime geçin.

İletişim:
Telefon: 05439269670
E-posta: sthillmanbusiness@gmail.com
"""

    with open(os.path.join(final_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(info_text)

    # ZIP olarak paketle
    print(f"\n[*] Final paketi '{package_name}' klasörüne oluşturuldu.")
    print(f"[*] ZIP dosyası oluşturuluyor...")
    
    # ZIP oluştur
    zip_file_name = f"{package_name}.zip"
    try:
        shutil.make_archive(package_name, 'zip', os.path.dirname(final_dir), os.path.basename(final_dir))
        print(f"[+] ZIP dosyası başarıyla oluşturuldu: {zip_file_name}")
    except Exception as e:
        print(f"[-] ZIP oluşturma hatası: {e}")
    
    return True

def main():
    print("======== YouTube Mezat Yardımcısı - KAPSAMLI EXE PAKETLEME ========")
    print("===============================================================")
    
    # 1. Supabase bağlantısını kontrol et
    if not validate_supabase_connection():
        print("[-] Supabase bağlantısı doğrulanamadı, ancak işleme devam ediliyor...")
    else:
        print("[+] Supabase bağlantısı doğrulandı.")
    
    # 2. Lisans doğrulama sistemini optimize et
    if not optimize_license_validation():
        print("[-] Lisans doğrulama sistemi optimize edilemedi. İşlem durduruluyor.")
        return
    else:
        print("[+] Lisans doğrulama sistemi optimize edildi.")
    
    # 3. PyInstaller'ı kontrol et ve kur
    if not check_pyinstaller():
        print("[-] PyInstaller kurulamadı. İşlem durduruluyor.")
        return
    
    # 4. Gerekli paketleri yükle
    if not check_and_install_required_packages():
        print("[-] Gerekli paketler yüklenemedi. İşlem durduruluyor.")
        return
    
    # 5. Kapsamlı EXE paketi oluştur
    if create_comprehensive_exe():
        print("\n[+] Kapsamlı EXE paketi başarıyla oluşturuldu.")
        print("[*] Kurulum tamamlandı. Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    else:
        print("\n[-] EXE paketi oluşturulamadı.")

if __name__ == "__main__":
    main()