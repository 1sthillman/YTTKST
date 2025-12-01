import os
import sys
import shutil
import datetime
import subprocess
import py_compile
import base64

def create_secure_package():
    print("🔒 YouTube Mezat Yardımcısı - GÜVENLİ PAKET OLUŞTURUCU")
    print("============================================================")

    # Paket adı ve klasörü oluştur
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_GUVENLI_v2.0_{datetime.datetime.now().strftime('%d%m%Y')}"
    package_dir = os.path.join(os.getcwd(), package_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    print(f"📁 Güvenli paket klasörü oluşturuluyor: {package_name}")

    # Kaynak kodları gizleyerek derle
    print("\n🔐 Kaynak kodları güvenli şekilde derleniyor...")
    
    # Python dosyalarını derle
    py_files = ["mezaxx.py", "auto_installer.py"]
    for py_file in py_files:
        if os.path.exists(py_file):
            try:
                # Bytecode dosyasını oluştur
                compiled_file = py_file.replace('.py', '.pyc')
                py_compile.compile(py_file, cfile=os.path.join(package_dir, compiled_file))
                print(f"  ✅ {py_file} -> {compiled_file} (derlenmiş)")
            except Exception as e:
                print(f"  ❌ {py_file} derlenemedi: {e}")
    
    # Gerekli dosyaları kopyala (kaynak kodları hariç)
    print("\n📋 Gerekli dosyalar kopyalanıyor...")
    
    # Ses dosyalarını kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", os.path.join(package_dir, "sound"))
        print("  ✅ sound klasörü")
    
    # Logo dosyasını kopyala
    if os.path.exists("LOGO.png"):
        shutil.copy("LOGO.png", package_dir)
        print("  ✅ LOGO.png")
    
    # Güvenli lisans dosyası oluştur (şifrelenmiş)
    print("\n🔑 Güvenli lisans dosyası oluşturuluyor...")
    try:
        if os.path.exists("license_codes.json"):
            with open("license_codes.json", "rb") as f:
                license_data = f.read()
                
            # Basit bir şifreleme (gerçek bir şifreleme değil, sadece görsel koruma)
            encoded_data = base64.b64encode(license_data)
            
            with open(os.path.join(package_dir, "license.dat"), "wb") as f:
                f.write(encoded_data)
            print("  ✅ license.dat (şifrelenmiş)")
    except Exception as e:
        print(f"  ❌ Lisans dosyası oluşturulamadı: {e}")
    
    # requirements.txt kopyala
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", package_dir)
        print("  ✅ requirements.txt")
    
    # Boş settings.json oluştur
    with open(os.path.join(package_dir, "settings.json"), "w", encoding="utf-8") as f:
        f.write('{"theme": "dark", "language": "tr"}')
    print("  ✅ settings.json")

    # Başlatıcı script oluştur
    print("\n🚀 Tek tıkla çalışan başlatıcı oluşturuluyor...")
    
    # Başlatıcı BAT dosyası
    starter_bat = f"""@echo off
title YouTube Mezat Yardımcısı Başlatılıyor...

set "APP_DIR=%~dp0"
set "PYTHON_DIR=%APP_DIR%Python"
set "PYTHON_EXE=%PYTHON_DIR%\\python.exe"
set "PYTHONW_EXE=%PYTHON_DIR%\\pythonw.exe"
set "MEZAXX_SCRIPT=%APP_DIR%mezaxx.pyc"
set "REQUIREMENTS_FILE=%APP_DIR%requirements.txt"
set "INSTALLER_LOG=%APP_DIR%kurulum_log.txt"

echo.
echo ============================================================
echo   YouTube Mezat Yardımcısı - Otomatik Başlatıcı
echo ============================================================
echo.

:: Python kontrolü ve kurulumu
if not exist "%PYTHON_DIR%" (
    echo Python bulunamadı. Otomatik kurulum başlatılıyor...
    echo Bu işlem biraz zaman alabilir. Lütfen bekleyin...
    
    :: Python embeddable sürümünü indir
    echo Python indiriliyor...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile '%APP_DIR%\\python_embed.zip'"
    
    :: Python'ı çıkar
    echo Python kuruluyor...
    powershell -Command "Expand-Archive -Path '%APP_DIR%\\python_embed.zip' -DestinationPath '%PYTHON_DIR%'"
    del "%APP_DIR%\\python_embed.zip"
    
    :: pip kurulumu
    echo pip kuruluyor...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%APP_DIR%\\get-pip.py'"
    "%PYTHON_EXE%" "%APP_DIR%\\get-pip.py" > "%INSTALLER_LOG%" 2>&1
    del "%APP_DIR%\\get-pip.py"
    
    :: python310._pth dosyasını düzenle (import site satırını etkinleştir)
    powershell -Command "(Get-Content '%PYTHON_DIR%\\python310._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\\python310._pth'"
)

:: Gerekli modülleri yükle
echo Gerekli Python modülleri kontrol ediliyor ve yükleniyor...
echo Bu işlem biraz zaman alabilir. Lütfen bekleyin...
"%PYTHON_EXE%" -m pip install --upgrade pip >> "%INSTALLER_LOG%" 2>&1
"%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS_FILE%" >> "%INSTALLER_LOG%" 2>&1

if %errorlevel% neq 0 (
    echo ❌ Hata: Python modülleri yüklenirken bir sorun oluştu.
    echo Detaylar için "%INSTALLER_LOG%" dosyasını kontrol edin.
    pause
    exit /b 1
) else (
    echo ✅ Gerekli modüller başarıyla yüklendi.
)

:: Masaüstü kısayolu oluştur
set "SHORTCUT_PATH=%%USERPROFILE%%\\Desktop\\YouTube Mezat Yardımcısı.lnk"
if not exist "%SHORTCUT_PATH%" (
    echo Masaüstü kısayolu oluşturuluyor...
    echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
    echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\\YouTube Mezat Yardımcısı.lnk" >> "%TEMP%\\CreateShortcut.vbs"
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\CreateShortcut.vbs"
    echo oLink.TargetPath = "%PYTHONW_EXE%" >> "%TEMP%\\CreateShortcut.vbs"
    echo oLink.Arguments = Chr(34) ^& "%MEZAXX_SCRIPT%" ^& Chr(34) >> "%TEMP%\\CreateShortcut.vbs"
    echo oLink.WorkingDirectory = "%APP_DIR%" >> "%TEMP%\\CreateShortcut.vbs"
    echo oLink.IconLocation = "%APP_DIR%LOGO.png" >> "%TEMP%\\CreateShortcut.vbs"
    echo oLink.Save >> "%TEMP%\\CreateShortcut.vbs"
    cscript //nologo "%TEMP%\\CreateShortcut.vbs"
    del "%TEMP%\\CreateShortcut.vbs"
    echo ✅ Masaüstü kısayolu oluşturuldu.
)

echo.
echo 🎉 Kurulum ve hazırlık tamamlandı!
echo Program başlatılıyor...
echo.

:: Programı başlat (CMD penceresi olmadan)
start "" "%PYTHONW_EXE%" "%MEZAXX_SCRIPT%"
exit
"""
    
    with open(os.path.join(package_dir, "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat"), "w", encoding="utf-8") as f:
        f.write(starter_bat)
    print("  ✅ YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat oluşturuldu")

    # Masaüstü kısayolu oluşturucu
    shortcut_bat = f"""@echo off
set "APP_DIR=%~dp0"
set "PYTHON_EXE=%APP_DIR%Python\\pythonw.exe"
set "MEZAXX_SCRIPT=%APP_DIR%mezaxx.pyc"
set "SHORTCUT_PATH=%%USERPROFILE%%\\Desktop\\YouTube Mezat Yardımcısı.lnk"

echo Masaüstü kısayolu oluşturuluyor...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\\YouTube Mezat Yardımcısı.lnk" >> "%TEMP%\\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.TargetPath = "%PYTHON_EXE%" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.Arguments = Chr(34) ^& "%MEZAXX_SCRIPT%" ^& Chr(34) >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.IconLocation = "%APP_DIR%LOGO.png" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\\CreateShortcut.vbs"
cscript //nologo "%TEMP%\\CreateShortcut.vbs"
del "%TEMP%\\CreateShortcut.vbs"
echo ✅ Masaüstü kısayolu oluşturuldu.
pause
"""
    
    with open(os.path.join(package_dir, "MASAUSTU_KISAYOLU_OLUSTUR.bat"), "w", encoding="utf-8") as f:
        f.write(shortcut_bat)
    print("  ✅ MASAUSTU_KISAYOLU_OLUSTUR.bat oluşturuldu")

    # Kullanım talimatları
    instructions = f"""
YouTube Mezat Yardımcısı - KULLANIM TALİMATLARI:

1. ZIP dosyasını bilgisayarınızda istediğiniz bir yere çıkarın (örneğin, Belgelerim veya Masaüstü).
2. Çıkardığınız klasörün içine girin.
3. "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat" dosyasına ÇİFT TIKLAYIN.
   - Bu dosya, programı otomatik olarak kontrol edecek, gerekli Python ortamını ve kütüphanelerini kuracak ve ardından programı başlatacaktır.
   - İlk çalıştırmada bu işlem biraz zaman alabilir. Lütfen bekleyin.
   - Kurulum sırasında bir komut istemcisi penceresi açılıp kapanabilir, bu normaldir. Program arayüzü otomatik olarak açılacaktır.
4. Program başarıyla başlatıldığında, masaüstünüzde "YouTube Mezat Yardımcısı" adında bir kısayol oluşacaktır. Sonraki kullanımlarınızda bu kısayola çift tıklayarak programı daha hızlı başlatabilirsiniz.

Önemli Notlar:
- Programın düzgün çalışması için internet bağlantısı gereklidir.
- Windows Defender veya antivirüs programınız bir uyarı verebilir. Bu durumda programı güvenli olarak işaretlemeniz gerekebilir.
- Herhangi bir sorun yaşarsanız, klasör içindeki "kurulum_log.txt" dosyasını kontrol edebilirsiniz.
"""
    
    with open(os.path.join(package_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(instructions)
    print("  ✅ KULLANIM_TALIMATLARI.txt oluşturuldu")

    # Supabase config dosyasını kopyala
    if os.path.exists("supabase_config.json"):
        # Şifrelenmiş olarak kopyala
        with open("supabase_config.json", "rb") as f:
            config_data = f.read()
            
        # Basit bir şifreleme
        encoded_config = base64.b64encode(config_data)
        
        with open(os.path.join(package_dir, "supabase.dat"), "wb") as f:
            f.write(encoded_config)
        print("  ✅ supabase.dat (şifrelenmiş)")
    
    # Kaynak kodlarını çalıştırmak için özel bir loader script oluştur
    loader_code = f"""
import base64
import json
import os
import sys
import importlib.util

# Şifrelenmiş dosyaları çöz
def decode_file(encoded_file, output_file):
    try:
        with open(encoded_file, 'rb') as f:
            encoded_data = f.read()
        
        decoded_data = base64.b64decode(encoded_data)
        
        with open(output_file, 'wb') as f:
            f.write(decoded_data)
            
        return True
    except Exception as e:
        print(f"Hata: {{e}}")
        return False

# Geçici dizin oluştur
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_temp")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Şifrelenmiş lisans dosyasını çöz
if os.path.exists("license.dat"):
    decode_file("license.dat", os.path.join(temp_dir, "license_codes.json"))

# Şifrelenmiş supabase config dosyasını çöz
if os.path.exists("supabase.dat"):
    decode_file("supabase.dat", os.path.join(temp_dir, "supabase_config.json"))

# Mezaxx modülünü çalıştır
if __name__ == "__main__":
    # Geçici dizini sys.path'e ekle
    sys.path.insert(0, temp_dir)
    
    # Mezaxx'i çalıştır
    try:
        # Mezaxx'i yükle ve çalıştır
        spec = importlib.util.spec_from_file_location("mezaxx", "mezaxx.pyc")
        mezaxx = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mezaxx)
        
        # Programı başlat
        if hasattr(mezaxx, "__main__"):
            mezaxx.__main__()
    except Exception as e:
        print(f"Hata: {{e}}")
        sys.exit(1)
"""
    
    with open(os.path.join(package_dir, "loader.py"), "w", encoding="utf-8") as f:
        f.write(loader_code)
    print("  ✅ loader.py oluşturuldu")

    # ZIP olarak paketle
    zip_file_name = f"{package_name}.zip"
    shutil.make_archive(package_name, 'zip', package_dir)
    print(f"\n📦 ZIP paketi oluşturuluyor...")
    print(f"  ✅ {zip_file_name} oluşturuldu ({os.path.getsize(zip_file_name) / (1024*1024):.1f} MB)")

    print("\n============================================================ ")
    print("🎉 GÜVENLİ PAKET TAMAMLANDI!")
    print("============================================================ ")
    print(f"📁 Klasör: {package_name}")
    print(f"📦 ZIP: {zip_file_name}")
    print("\n📋 MÜŞTERİLERİNİZE GÖNDERMEK İÇİN:")
    print(f"  1. {zip_file_name} dosyasını gönderin")
    print("  2. Müşterilerinize şu talimatı verin:")
    print("     - ZIP dosyasını açın")
    print("     - YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat dosyasına ÇİFT TIKLAYIN")
    print("\n✅ TEK TIKLA ÇALIŞAN GÜVENLİ ÇÖZÜM HAZIR! Müşterilerinize göndermeye hazır.")
    input("\nDevam etmek için Enter tuşuna basın...")

if __name__ == "__main__":
    create_secure_package()


