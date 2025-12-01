"""
mezaxx.py için yazıcı ayarları entegrasyonu
Bu dosya mezaxx.py'ye eklenecek kodu içerir
"""

# show_settings fonksiyonuna eklenecek kod (Yazıcı Ayarları bölümü)
PRINTER_SETTINGS_SECTION = """
        # Yazıcı Ayarları
        printer_section = ctk.CTkFrame(frame, fg_color="transparent")
        printer_section.pack(fill="x", pady=20)
        
        ctk.CTkLabel(printer_section, 
                    text="Yazıcı Ayarları", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        # Yazıcı ayarları butonu
        printer_btn_frame = ctk.CTkFrame(printer_section, fg_color="transparent")
        printer_btn_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(printer_btn_frame,
                     text="Yazıcı Ayarlarını Düzenle",
                     command=self.show_printer_settings,
                     height=40,
                     corner_radius=10,
                     fg_color=self.colors["primary"]).pack(fill="x")
"""

# show_printer_settings fonksiyonu
SHOW_PRINTER_SETTINGS_FUNCTION = """
    def show_printer_settings(self):
        """Yazıcı ayarları penceresini göster"""
        try:
            from printer_settings import PrinterSettings, show_printer_settings_dialog
            printer_settings = PrinterSettings()
            show_printer_settings_dialog(self.root, printer_settings)
        except Exception as e:
            logging.exception("show_printer_settings")
            self.show_notification("Hata", f"Yazıcı ayarları açılamadı: {str(e)}", "error")
"""

# Kurulum talimatları
INSTALLATION_INSTRUCTIONS = """
Yazıcı ayarları entegrasyonu için:

1. printer_settings.py dosyasını mezaxx.py ile aynı dizine kopyalayın

2. mezaxx.py dosyasında, show_settings fonksiyonunda "Diğer Ayarlar" bölümünden önce 
   PRINTER_SETTINGS_SECTION içeriğini ekleyin

3. mezaxx.py dosyasında, apply_settings fonksiyonundan sonra 
   SHOW_PRINTER_SETTINGS_FUNCTION içeriğini ekleyin

4. direct_print fonksiyonunu güncelleyin (zaten yapıldı)
"""

