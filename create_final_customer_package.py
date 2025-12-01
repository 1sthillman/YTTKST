# -*- coding: utf-8 -*-
import os
import sys
import shutil
import datetime
import tempfile

def create_final_package():
    """Müşteri bilgilerini Supabase'e kaydeden güncellenmiş paketi oluşturur"""
    print("======== YouTube Mezat Yardimcisi - MUSTERI KAYIT PAKETI ========")
    print("============================================================")

    # Paket adı ve klasörü oluştur
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_MUSTERI_v4.0_{datetime.datetime.now().strftime('%d%m%Y')}"
    package_dir = os.path.join(os.getcwd(), package_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    print(f"[*] Final paket klasoru olusturuluyor: {package_name}")

    # Ana dosyaları kopyala
    print("\n[*] Ana dosyalar kopyalaniyor...")
    
    # Python dosyalarını kopyala
    py_files = ["mezaxx.py", "auto_installer.py", "save_customer_to_supabase.py"]
    for py_file in py_files:
        if os.path.exists(py_file):
            shutil.copy(py_file, package_dir)
            print(f"  [+] {py_file}")
    
    # Ses dosyalarını kopyala
    if os.path.exists("sound"):
        shutil.copytree("sound", os.path.join(package_dir, "sound"))
        print("  [+] sound klasoru")
    
    # Logo dosyasını kopyala
    if os.path.exists("LOGO.png"):
        shutil.copy("LOGO.png", package_dir)
        print("  [+] LOGO.png")
    
    # Gerekli JSON dosyalarını kopyala
    json_files = ["license_codes.json", "supabase_config.json"]
    for json_file in json_files:
        if os.path.exists(json_file):
            shutil.copy(json_file, package_dir)
            print(f"  [+] {json_file}")
    
    # requirements.txt kopyala veya oluştur
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", package_dir)
    else:
        with open(os.path.join(package_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("""customtkinter>=5.2.0
CTkMessagebox>=2.5
Pillow>=10.0.0
pygame>=2.5.0
requests>=2.31.0
chat-downloader>=0.2.0
supabase>=2.0.0
websockets>=11.0.0
""")
    print("  [+] requirements.txt")

    # settings.json kopyala veya oluştur
    if os.path.exists("settings.json"):
        shutil.copy("settings.json", package_dir)
    else:
        with open(os.path.join(package_dir, "settings.json"), "w", encoding="utf-8") as f:
            f.write('{"theme": "dark", "language": "tr"}')
    print("  [+] settings.json")

    # Başlatıcı script oluştur
    print("\n[*] Tek tikla calisan baslaticilar olusturuluyor...")
    
    # Başlatıcı BAT dosyası
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
    print("  [+] YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat olusturuldu")

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
    print("  [+] YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs olusturuldu")

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

YENİ ÖZELLİK - MÜŞTERİ BİLGİLERİNİ KAYDETME:

Bu sürümde, müşteri bilgilerini hem yerel olarak hem de Supabase veritabanına kaydedebilirsiniz:

1. Menüden "Ödeme Yapanlar" seçeneğine tıklayın.
2. Açılan pencerede, kullanıcı ekleyebilir veya mevcut kullanıcıları düzenleyebilirsiniz.
3. Her kullanıcı için:
   - YouTube Kullanıcı Adı
   - Ad Soyad
   - Telefon
   - Adres
   bilgilerini girebilirsiniz.
4. "Kaydet" butonuna tıkladığınızda, bilgiler hem yerel olarak kaydedilecek hem de Supabase veritabanına gönderilecektir.
5. İnternet bağlantınız olmasa bile bilgiler yerel olarak kaydedilir, internet bağlantısı sağlandığında otomatik olarak Supabase'e gönderilir.

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
    print("  [+] KULLANIM_TALIMATLARI.txt olusturuldu")

    # ZIP olarak paketle
    zip_file_name = f"{package_name}.zip"
    shutil.make_archive(package_name, 'zip', package_dir)
    print(f"\n[*] ZIP paketi olusturuluyor...")
    print(f"  [+] {zip_file_name} olusturuldu ({os.path.getsize(zip_file_name) / (1024*1024):.1f} MB)")

    print("\n============================================================ ")
    print("*** MUSTERI KAYIT PAKETI TAMAMLANDI! ***")
    print("============================================================ ")
    print(f"- Klasor: {package_name}")
    print(f"- ZIP: {zip_file_name}")
    print("\n- MUSTERILERINIZE GONDERMEK ICIN:")
    print(f"  1. {zip_file_name} dosyasini gonderin")
    print("  2. Musterilerinize su talimatlari verin:")
    print("     - ZIP dosyasini acin")
    print("     - Ilk kurulum icin: YOUTUBE_MEZAT_YARDIMCISI_BASLAT.bat dosyasina cift tiklayin")
    print("     - Sonraki kullanimlar icin: YOUTUBE_MEZAT_YARDIMCISI_SESSIZ_BASLAT.vbs dosyasina cift tiklayin")
    print("\n[+] TEK TIKLA CALISAN COZUM HAZIR! Musterilerinize gondermeye hazir.")
    
    return True

if __name__ == "__main__":
    create_final_package()
    input("\nDevam etmek icin Enter tusuna basin...")

