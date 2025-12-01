# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import datetime
import tempfile
import zipfile
import site

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

def create_exe_package():
    """PyInstaller ile EXE paketi oluşturur"""
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
    
    # Beklenen EXE dosyası yolu
    exe_path = os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi", "YouTube_Mezat_Yardimcisi.exe")
    
    # license_codes.json dosyasını kontrol et
    if not os.path.exists("license_codes.json"):
        print("[-] license_codes.json dosyası bulunamadı!")
        return False
    
    # supabase_config.json dosyasını kontrol et
    if not os.path.exists("supabase_config.json"):
        print("[-] supabase_config.json dosyası bulunamadı!")
        return False
    
    # mezaxx.py dosyasını kontrol et
    if not os.path.exists("mezaxx.py"):
        print("[-] mezaxx.py dosyası bulunamadı!")
        return False
    
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
all_hiddenimports.extend([
    'websocket', 'websocket-client', 'realtime', 'realtime.connection',
    'chat_downloader', 'chat_downloader.sites', 'chat_downloader.sites.youtube',
    'babel.numbers', 'babel.dates', 'babel.core'
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

# Kendi veri dosyalarımızı ekle
all_datas.extend([
    ('sound', 'sound'),
    ('license_codes.json', '.'),
    ('supabase_config.json', '.'),
])

if os.path.exists('printer_settings.py'):
    all_datas.append(('printer_settings.py', '.'))
if os.path.exists('LOGO.png'):
    all_datas.append(('LOGO.png', '.'))
if os.path.exists('settings.json'):
    all_datas.append(('settings.json', '.'))

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
    icon=None,
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
    
    spec_file = os.path.join(os.getcwd(), "YouTube_Mezat_Yardimcisi_Fixed_Complete.spec")
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"[+] Spec dosyasi olusturuldu: {spec_file}")

    # PyInstaller komutu doğrudan çalıştır
    print("\n[*] PyInstaller ile EXE olusturuluyor...")
    print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        spec_file,
        "--noconfirm"
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
    
    # dist klasöründeki YouTube_Mezat_Yardimcisi klasörünü kopyala
    shutil.copytree(os.path.join(dist_dir, "YouTube_Mezat_Yardimcisi"), final_dir)

    # Bilgi dosyası oluştur
    info_text = """
YouTube Mezat Yardimcisi - KULLANIM TALIMATLARI:

1. YouTube_Mezat_Yardimcisi.exe dosyasina cift tiklayarak programi baslatin.

2. Program basladiginda YouTube kanal URL'nizi ve lisans kodunuzu girerek giris yapin.
   - Lisans kodunu tam olarak yazdiginizdan emin olun
   - Lisans kodundaki bosluk veya ozel karakterlere dikkat edin

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

    with open(os.path.join(final_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(info_text)

    # ZIP olarak paketleyelim
    print(f"\n[*] Final paketi '{package_name}' klasorune olusturuldu.")
    print(f"[*] ZIP dosyasi olusturuluyor...")
    
    # ZIP oluştur
    zip_file_name = f"{package_name}.zip"
    try:
        shutil.make_archive(package_name, 'zip', os.path.dirname(final_dir), os.path.basename(final_dir))
        print(f"[+] ZIP dosyasi basariyla olusturuldu: {zip_file_name}")
    except Exception as e:
        print(f"[-] ZIP olusturma hatasi: {e}")
    
    return True

def main():
    print("======== YouTube Mezat Yardımcısı - EXE Paketleme ========")
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
        print("\n[+] EXE paketi başarıyla oluşturuldu.")
        print("[*] Kurulum tamamlandı. Kullanıcılar artık ZIP dosyasını açıp EXE'yi çalıştırabilir.")
    else:
        print("\n[-] EXE paketi oluşturulamadı.")

if __name__ == "__main__":
    main()

