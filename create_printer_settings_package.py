# -*- coding: utf-8 -*-
import os
import sys
import shutil
import datetime

def create_printer_settings_package():
    """Yazici ayarlari modulunu iceren paketi olusturur"""
    print("======== YouTube Mezat Yardimcisi - YAZICI AYARLARI PAKETI ========")
    print("============================================================")

    # Paket adı ve klasörü oluştur
    package_name = f"YOUTUBE_MEZAT_YARDIMCISI_YAZICI_AYARLARI_{datetime.datetime.now().strftime('%d%m%Y')}"
    package_dir = os.path.join(os.getcwd(), package_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    print(f"[*] Paket klasoru olusturuluyor: {package_name}")

    # Dosyaları kopyala
    print("\n[*] Dosyalar kopyalaniyor...")
    
    # printer_settings.py dosyasını kopyala
    if os.path.exists("printer_settings.py"):
        shutil.copy("printer_settings.py", package_dir)
        print("  [+] printer_settings.py")
    else:
        print("  [-] printer_settings.py bulunamadi!")
        return False
    
    # mezaxx_printer_settings.py dosyasını kopyala
    if os.path.exists("mezaxx_printer_settings.py"):
        shutil.copy("mezaxx_printer_settings.py", package_dir)
        print("  [+] mezaxx_printer_settings.py")
    else:
        print("  [-] mezaxx_printer_settings.py bulunamadi!")
    
    # README dosyası oluştur
    readme_content = """# YOUTUBE MEZAT YARDIMCISI - YAZICI AYARLARI MODULU

Bu paket, YouTube Mezat Yardimcisi programina yazici ayarlari eklemek icin gerekli dosyalari icerir.

## Icerik

1. `printer_settings.py` - Yazici ayarlari modulu
2. `mezaxx_printer_settings.py` - Entegrasyon talimatlari

## Kurulum Adimlari

1. `printer_settings.py` dosyasini mezaxx.py ile ayni dizine kopyalayin

2. mezaxx.py dosyasinda, show_settings fonksiyonunda "Diger Ayarlar" bolumunden once 
   asagidaki kodu ekleyin:

```python
        # Yazici Ayarlari
        printer_section = ctk.CTkFrame(frame, fg_color="transparent")
        printer_section.pack(fill="x", pady=20)
        
        ctk.CTkLabel(printer_section, 
                    text="Yazici Ayarlari", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        # Yazici ayarlari butonu
        printer_btn_frame = ctk.CTkFrame(printer_section, fg_color="transparent")
        printer_btn_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(printer_btn_frame,
                     text="Yazici Ayarlarini Duzenle",
                     command=self.show_printer_settings,
                     height=40,
                     corner_radius=10,
                     fg_color=self.colors["primary"]).pack(fill="x")
```

3. mezaxx.py dosyasinda, apply_settings fonksiyonundan sonra 
   asagidaki fonksiyonu ekleyin:

```python
    def show_printer_settings(self):
        try:
            from printer_settings import PrinterSettings, show_printer_settings_dialog
            printer_settings = PrinterSettings()
            show_printer_settings_dialog(self.root, printer_settings)
        except Exception as e:
            logging.exception("show_printer_settings")
            self.show_notification("Hata", f"Yazici ayarlari acilamadi: {str(e)}", "error")
```

4. mezaxx.py dosyasindaki direct_print fonksiyonunu asagidaki gibi guncelleyin:

```python
    def direct_print(self, text):
        try:
            # Yazici ayarlarini yukle
            try:
                from printer_settings import PrinterSettings
                printer_settings = PrinterSettings()
                # Metni yazici tipine gore formatla
                text = printer_settings.format_text_for_printer(text)
            except Exception as e:
                logging.exception("Yazici ayarlari yuklenemedi")
                # Yazici ayarlari yuklenemezse orijinal metni kullan
            
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(text)
                path = f.name
            os.startfile(path, "print")
            self.root.after(30000, lambda: os.unlink(path))
            self.show_notification("Yazdirildi", "Fis yazdiriciya gonderildi", "success")
        except Exception as e:
            logging.exception("direct_print")
            self.show_notification("Yazdirma Hatasi", str(e), "error")
```

## Ozellikler

Bu modul asagidaki yazici ayarlarini yapmaniza olanak tanir:

1. Yazici tipi secimi:
   - Standart yazici
   - Thermal yazici
   - Etiket yazicisi (yapiskanli barkod)

2. Kagit boyutlari (mm cinsinden)
   - Genislik
   - Yukseklik

3. Kenar bosluklari (mm cinsinden)
   - Sol, sag, ust, alt

4. Yazi tipi ayarlari
   - Boyut
   - Yazi tipi

5. Fis genisligi (karakter sayisi)

6. Ek ozellikler
   - Logo yazdirma
   - Otomatik kesim (thermal yazicilar icin)
   - Barkod yazdirma

## Destek

Herhangi bir sorunuz veya oneriniz varsa, lutfen iletisime gecin:
Telefon: 05439269670
E-posta: sthillmanbusiness@gmail.com
"""
    
    with open(os.path.join(package_dir, "README.md"), "w") as f:
        f.write(readme_content)
    print("  [+] README.md olusturuldu")
    
    # ZIP olarak paketle
    zip_file_name = f"{package_name}.zip"
    shutil.make_archive(package_name, 'zip', package_dir)
    print(f"\n[*] ZIP paketi olusturuluyor...")
    print(f"  [+] {zip_file_name} olusturuldu ({os.path.getsize(zip_file_name) / (1024*1024):.1f} MB)")

    print("\n============================================================ ")
    print("*** YAZICI AYARLARI PAKETI TAMAMLANDI! ***")
    print("============================================================ ")
    print(f"- Klasor: {package_name}")
    print(f"- ZIP: {zip_file_name}")
    
    return True

if __name__ == "__main__":
    create_printer_settings_package()
    input("\nDevam etmek icin Enter tusuna basin...")