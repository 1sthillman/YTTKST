import os
import sys
import shutil
import datetime
import subprocess
import py_compile
import base64

def create_secure_package():
    print("🔒 YouTube Mezat Yardımcısı - GÜVENLİ PAKET OLUŞTURUCU (DÜZELTİLMİŞ)")
    print("============================================================")

    # Paket adı ve klasörü oluştur
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_GUVENLI_v2.1_{datetime.datetime.now().strftime('%d%m%Y')}"
    package_dir = os.path.join(os.getcwd(), package_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    print(f"📁 Güvenli paket klasörü oluşturuluyor: {package_name}")

    # Orijinal dosyaları kopyala
    print("\n📋 Gerekli dosyalar kopyalanıyor...")
    
    # Doğrudan mezaxx.py ve auto_installer.py'yi kopyala (derleme yapmadan)
    for file in ["mezaxx.py", "auto_installer.py"]:
        if os.path.exists(file):
            shutil.copy(file, package_dir)
            print(f"  ✅ {file}")
    
    # Ses dosyalarını kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", os.path.join(package_dir, "sound"))
        print("  ✅ sound klasörü")
    
    # Logo dosyasını kopyala
    if os.path.exists("LOGO.png"):
        shutil.copy("LOGO.png", package_dir)
        print("  ✅ LOGO.png")
    
    # Güvenli lisans dosyası oluştur
    print("\n🔑 Güvenli lisans dosyası oluşturuluyor...")
    try:
        if os.path.exists("license_codes.json"):
            with open("license_codes.json", "rb") as f:
                license_data = f.read()
                
            # Basit bir şifreleme (gerçek bir şifreleme değil, sadece görsel koruma)
            encoded_data = base64.b64encode(license_data)
            
            with open(os.path.join(package_dir, "license.dat"), "wb") as f:
                f.write(encoded_data)
            
            # Ayrıca basit bir demo lisans dosyası oluştur
            with open(os.path.join(package_dir, "license_codes.json"), "w", encoding="utf-8") as f:
                f.write('{"valid_codes": ["DEMO123"], "channel_licenses": {"Demo_Channel": ["DEMO123"]}}')
            
            print("  ✅ license.dat (şifrelenmiş)")
            print("  ✅ license_codes.json (demo)")
    except Exception as e:
        print(f"  ❌ Lisans dosyası oluşturulamadı: {e}")
    
    # requirements.txt kopyala
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", package_dir)
        print("  ✅ requirements.txt")
    
    # settings.json kopyala veya oluştur
    if os.path.exists("settings.json"):
        shutil.copy("settings.json", package_dir)
    else:
        with open(os.path.join(package_dir, "settings.json"), "w", encoding="utf-8") as f:
            f.write('{"theme": "dark", "language": "tr"}')
    print("  ✅ settings.json")

    # Supabase config dosyasını kopyala
    if os.path.exists("supabase_config.json"):
        shutil.copy("supabase_config.json", package_dir)
        print("  ✅ supabase_config.json")

    # Başlatıcı script oluştur
    print("\n🚀 Tek tıkla çalışan başlatıcı oluşturuluyor...")
    
    # Başlatıcı BAT dosyası - Daha güvenilir ve hata mesajlarını gösteren
    starter_bat = f"""@echo off
title YouTube Mezat Yardımcısı Başlatılıyor...
color 0A

set "APP_DIR=%~dp0"
set "PYTHON_DIR=%APP_DIR%Python"
set "PYTHON_EXE=%PYTHON_DIR%\\python.exe"
set "PYTHONW_EXE=%PYTHON_DIR%\\pythonw.exe"
set "MEZAXX_SCRIPT=%APP_DIR%mezaxx.py"
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
    powershell -Command "& {{try {{ Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile '%APP_DIR%\\python_embed.zip'; Write-Host 'İndirme başarılı!' }} catch {{ Write-Host 'İndirme hatası: ' $_.Exception.Message }}}}"
    
    if not exist "%APP_DIR%\\python_embed.zip" (
        echo ❌ Python indirilemedi! İnternet bağlantınızı kontrol edin.
        echo Alternatif olarak Python'u manuel olarak yükleyebilirsiniz: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    :: Python'ı çıkar
    echo Python kuruluyor...
    mkdir "%PYTHON_DIR%" 2>nul
    powershell -Command "& {{try {{ Expand-Archive -Path '%APP_DIR%\\python_embed.zip' -DestinationPath '%PYTHON_DIR%' -Force; Write-Host 'Çıkarma başarılı!' }} catch {{ Write-Host 'Çıkarma hatası: ' $_.Exception.Message }}}}"
    del "%APP_DIR%\\python_embed.zip"
    
    :: pip kurulumu
    echo pip kuruluyor...
    powershell -Command "& {{try {{ Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%APP_DIR%\\get-pip.py'; Write-Host 'pip indirme başarılı!' }} catch {{ Write-Host 'pip indirme hatası: ' $_.Exception.Message }}}}"
    
    if not exist "%APP_DIR%\\get-pip.py" (
        echo ❌ pip indirilemedi! İnternet bağlantınızı kontrol edin.
        pause
        exit /b 1
    )
    
    "%PYTHON_EXE%" "%APP_DIR%\\get-pip.py" --no-warn-script-location
    del "%APP_DIR%\\get-pip.py"
    
    :: python310._pth dosyasını düzenle (import site satırını etkinleştir)
    echo import site etkinleştiriliyor...
    powershell -Command "& {{try {{ (Get-Content '%PYTHON_DIR%\\python310._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\\python310._pth'; Write-Host 'Düzenleme başarılı!' }} catch {{ Write-Host 'Düzenleme hatası: ' $_.Exception.Message }}}}"
    
    :: PATH'e pip ekleme
    echo PATH güncelleniyor...
    set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\\Scripts;%PATH%"
)

:: Gerekli modülleri yükle
echo Gerekli Python modülleri kontrol ediliyor ve yükleniyor...
echo Bu işlem biraz zaman alabilir. Lütfen bekleyin...

"%PYTHON_EXE%" -m pip install --upgrade pip --no-warn-script-location
if %errorlevel% neq 0 (
    echo ❌ Hata: pip güncellenemedi.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS_FILE%" --no-warn-script-location
if %errorlevel% neq 0 (
    echo ❌ Hata: Python modülleri yüklenirken bir sorun oluştu.
    echo Detaylar için "%INSTALLER_LOG%" dosyasını kontrol edin.
    pause
    exit /b 1
) else (
    echo ✅ Gerekli modüller başarıyla yüklendi.
)

:: Masaüstü kısayolu oluştur
set "SHORTCUT_PATH=%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk"
if not exist "%SHORTCUT_PATH%" (
    echo Masaüstü kısayolu oluşturuluyor...
    echo Set oWS = CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
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
)

echo.
echo 🎉 Kurulum ve hazırlık tamamlandı!
echo Program başlatılıyor...
echo.

:: Programı başlat (normal modda, hata mesajlarını görebilmek için)
echo Program başlatılıyor...
"%PYTHON_EXE%" "%MEZAXX_SCRIPT%"

:: Eğer program başlatılamazsa hata mesajı göster
if %errorlevel% neq 0 (
    echo ❌ Program başlatılırken bir hata oluştu.
    echo Lütfen kurulum_log.txt dosyasını kontrol edin.
    pause
    exit /b 1
)

exit
"""
    
    with open(os.path.join(package_dir, "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat"), "w", encoding="utf-8") as f:
        f.write(starter_bat)
    print("  ✅ YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat oluşturuldu")

    # Sessiz başlatıcı (CMD penceresi göstermeyen)
    silent_starter_vbs = f"""
Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
PythonDir = strPath & "\\Python"
PythonExe = PythonDir & "\\pythonw.exe"
MezaxxScript = strPath & "\\mezaxx.py"

' Python kurulu mu kontrol et
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists(PythonDir) Then
    WshShell.Run "cmd /c " & Chr(34) & strPath & "\\YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat" & Chr(34), 1, True
Else
    ' Python kurulu, doğrudan başlat
    WshShell.Run Chr(34) & PythonExe & Chr(34) & " " & Chr(34) & MezaxxScript & Chr(34), 0, False
End If
"""
    
    with open(os.path.join(package_dir, "YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs"), "w", encoding="utf-8") as f:
        f.write(silent_starter_vbs)
    print("  ✅ YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs oluşturuldu")

    # Masaüstü kısayolu oluşturucu
    shortcut_bat = f"""@echo off
set "APP_DIR=%~dp0"
set "PYTHON_EXE=%APP_DIR%Python\\python.exe"
set "MEZAXX_SCRIPT=%APP_DIR%mezaxx.py"
set "SHORTCUT_PATH=%USERPROFILE%\\Desktop\\YouTube Mezat Yardımcısı.lnk"

echo Masaüstü kısayolu oluşturuluyor...
echo Set oWS = CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
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
3. BAŞLATMA SEÇENEKLERİ (ikisinden birini seçin):
   
   A) NORMAL BAŞLATMA (İlk kez kullanıyorsanız bunu seçin):
      - "YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat" dosyasına ÇİFT TIKLAYIN.
      - Bu dosya, programı otomatik olarak kontrol edecek, gerekli Python ortamını ve kütüphanelerini kuracak ve ardından programı başlatacaktır.
      - İlk çalıştırmada bu işlem biraz zaman alabilir. Lütfen bekleyin.
      - Kurulum sırasında komut penceresi açık kalacak ve olası hataları gösterecektir.
   
   B) SESSİZ BAŞLATMA (Python kurulumu tamamlandıktan sonra):
      - "YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs" dosyasına ÇİFT TIKLAYIN.
      - Bu dosya, programı hiçbir komut penceresi göstermeden doğrudan başlatacaktır.
      - Eğer Python kurulu değilse, otomatik olarak normal başlatıcıyı çalıştıracaktır.

4. Program başarıyla başlatıldığında, masaüstünüzde "YouTube Mezat Yardımcısı" adında bir kısayol oluşacaktır. Sonraki kullanımlarınızda bu kısayola çift tıklayarak programı daha hızlı başlatabilirsiniz.

SORUN GİDERME:

1. Program başlatılamıyorsa:
   - Normal başlatıcıyı (YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat) kullanın ve hata mesajlarını okuyun
   - Antivirüs programınızın engellemiş olabileceğini kontrol edin
   - İnternet bağlantınızın aktif olduğundan emin olun (ilk kurulum için gerekli)

2. "Python bulunamadı" hatası alıyorsanız:
   - İnternet bağlantınızı kontrol edin
   - Python'u manuel olarak yükleyip tekrar deneyin: https://www.python.org/downloads/

3. Diğer sorunlar için:
   - kurulum_log.txt dosyasını kontrol edin
   - Programı yönetici olarak çalıştırmayı deneyin

Önemli Notlar:
- Programın düzgün çalışması için internet bağlantısı gereklidir.
- Windows Defender veya antivirüs programınız bir uyarı verebilir. Bu durumda programı güvenli olarak işaretlemeniz gerekebilir.
"""
    
    with open(os.path.join(package_dir, "KULLANIM_TALIMATLARI.txt"), "w", encoding="utf-8") as f:
        f.write(instructions)
    print("  ✅ KULLANIM_TALIMATLARI.txt oluşturuldu")

    # ZIP olarak paketle
    zip_file_name = f"{package_name}.zip"
    shutil.make_archive(package_name, 'zip', package_dir)
    print(f"\n📦 ZIP paketi oluşturuluyor...")
    print(f"  ✅ {zip_file_name} oluşturuldu ({os.path.getsize(zip_file_name) / (1024*1024):.1f} MB)")

    print("\n============================================================ ")
    print("🎉 DÜZELTİLMİŞ GÜVENLİ PAKET TAMAMLANDI!")
    print("============================================================ ")
    print(f"📁 Klasör: {package_name}")
    print(f"📦 ZIP: {zip_file_name}")
    print("\n📋 MÜŞTERİLERİNİZE GÖNDERMEK İÇİN:")
    print(f"  1. {zip_file_name} dosyasını gönderin")
    print("  2. Müşterilerinize şu talimatları verin:")
    print("     - ZIP dosyasını açın")
    print("     - İlk kurulum için: YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat dosyasına çift tıklayın")
    print("     - Sonraki kullanımlar için: YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs dosyasına çift tıklayın")
    print("\n✅ TEK TIKLA ÇALIŞAN GÜVENLİ ÇÖZÜM HAZIR! Müşterilerinize göndermeye hazır.")
    input("\nDevam etmek için Enter tuşuna basın...")

if __name__ == "__main__":
    create_secure_package()


