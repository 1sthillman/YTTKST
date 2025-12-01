"""
Yazıcı ayarları modülü
"""
import os
import json
import logging
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class PrinterSettings:
    """Yazıcı ayarları yönetimi için sınıf"""
    
    def __init__(self):
        # Varsayılan ayarlar
        self.default_settings = {
            "printer_type": "standard",  # standard, thermal, label
            "paper_width": 80,  # mm cinsinden
            "paper_height": 297,  # mm cinsinden (A4 varsayılan)
            "margin_left": 5,  # mm cinsinden
            "margin_right": 5,  # mm cinsinden
            "margin_top": 5,  # mm cinsinden
            "margin_bottom": 5,  # mm cinsinden
            "font_size": 10,  # punto cinsinden
            "font_family": "Courier New",  # sabit genişlikli yazı tipi
            "print_logo": False,  # Logo yazdırma
            "auto_cut": False,  # Otomatik kesim (thermal yazıcılar için)
            "barcode_enabled": False,  # Barkod yazdırma
            "receipt_width_chars": 40,  # Fiş genişliği (karakter sayısı)
        }
        
        # Ayarları yükle veya varsayılanları kullan
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Yazıcı ayarlarını dosyadan yükler"""
        try:
            if os.path.exists("printer_settings.json"):
                with open("printer_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Eksik ayarları varsayılanlarla tamamla
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            return self.default_settings.copy()
        except Exception as e:
            logging.exception("Yazıcı ayarları yüklenirken hata oluştu")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Yazıcı ayarlarını dosyaya kaydeder"""
        try:
            with open("printer_settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.exception("Yazıcı ayarları kaydedilirken hata oluştu")
            return False
    
    def get_setting(self, key):
        """Belirli bir ayarı döndürür"""
        return self.settings.get(key, self.default_settings.get(key))
    
    def update_setting(self, key, value):
        """Belirli bir ayarı günceller"""
        if key in self.default_settings:
            self.settings[key] = value
            return True
        return False
    
    def reset_settings(self):
        """Tüm ayarları varsayılanlara sıfırlar"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def format_text_for_printer(self, text):
        """Metni seçilen yazıcı tipine göre formatlar"""
        printer_type = self.get_setting("printer_type")
        receipt_width = self.get_setting("receipt_width_chars")
        
        if printer_type == "thermal":
            # Thermal yazıcı için formatla
            lines = text.split("\n")
            formatted_lines = []
            
            for line in lines:
                if len(line) > receipt_width:
                    # Uzun satırları böl
                    chunks = [line[i:i+receipt_width] for i in range(0, len(line), receipt_width)]
                    formatted_lines.extend(chunks)
                else:
                    # Kısa satırları ortala veya olduğu gibi bırak
                    if "====" in line:
                        # Başlık satırlarını ortala
                        formatted_lines.append(line.center(receipt_width))
                    else:
                        formatted_lines.append(line)
            
            return "\n".join(formatted_lines)
            
        elif printer_type == "label":
            # Etiket yazıcısı için formatla (daha kompakt)
            lines = text.split("\n")
            # Gereksiz boşlukları ve ayırıcıları kaldır
            formatted_lines = []
            for line in lines:
                if "====" not in line and "----" not in line and line.strip():
                    formatted_lines.append(line)
            
            return "\n".join(formatted_lines)
        
        # Standart yazıcı için formatlamaya gerek yok
        return text

def show_printer_settings_dialog(parent, printer_settings):
    """Yazıcı ayarları için dialog penceresi gösterir"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Yazıcı Ayarları")
    dialog.geometry("600x700")
    dialog.resizable(False, False)
    dialog.grab_set()  # Modal dialog
    
    # Ana çerçeve
    main_frame = ctk.CTkFrame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Başlık
    ctk.CTkLabel(main_frame, text="📝 Yazıcı Ayarları", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
    
    # Ayarlar için bir frame
    settings_frame = ctk.CTkScrollableFrame(main_frame, width=550, height=550)
    settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Yazıcı tipi seçimi
    ctk.CTkLabel(settings_frame, text="Yazıcı Tipi:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(10, 5))
    
    printer_type_var = tk.StringVar(value=printer_settings.get_setting("printer_type"))
    
    printer_types_frame = ctk.CTkFrame(settings_frame)
    printer_types_frame.pack(fill="x", pady=(0, 15))
    
    ctk.CTkRadioButton(printer_types_frame, text="Standart Yazıcı", variable=printer_type_var, value="standard").pack(side="left", padx=10)
    ctk.CTkRadioButton(printer_types_frame, text="Thermal Yazıcı", variable=printer_type_var, value="thermal").pack(side="left", padx=10)
    ctk.CTkRadioButton(printer_types_frame, text="Etiket Yazıcısı", variable=printer_type_var, value="label").pack(side="left", padx=10)
    
    # Kağıt boyutları
    ctk.CTkLabel(settings_frame, text="Kağıt Boyutları (mm):", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(15, 5))
    
    paper_size_frame = ctk.CTkFrame(settings_frame)
    paper_size_frame.pack(fill="x", pady=(0, 15))
    
    ctk.CTkLabel(paper_size_frame, text="Genişlik:").pack(side="left", padx=(10, 5))
    paper_width_var = tk.StringVar(value=str(printer_settings.get_setting("paper_width")))
    paper_width_entry = ctk.CTkEntry(paper_size_frame, width=60, textvariable=paper_width_var)
    paper_width_entry.pack(side="left", padx=(0, 15))
    
    ctk.CTkLabel(paper_size_frame, text="Yükseklik:").pack(side="left", padx=(10, 5))
    paper_height_var = tk.StringVar(value=str(printer_settings.get_setting("paper_height")))
    paper_height_entry = ctk.CTkEntry(paper_size_frame, width=60, textvariable=paper_height_var)
    paper_height_entry.pack(side="left", padx=(0, 15))
    
    # Kenar boşlukları
    ctk.CTkLabel(settings_frame, text="Kenar Boşlukları (mm):", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(15, 5))
    
    margins_frame = ctk.CTkFrame(settings_frame)
    margins_frame.pack(fill="x", pady=(0, 15))
    
    # Sol kenar boşluğu
    ctk.CTkLabel(margins_frame, text="Sol:").grid(row=0, column=0, padx=5, pady=5)
    margin_left_var = tk.StringVar(value=str(printer_settings.get_setting("margin_left")))
    margin_left_entry = ctk.CTkEntry(margins_frame, width=60, textvariable=margin_left_var)
    margin_left_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Sağ kenar boşluğu
    ctk.CTkLabel(margins_frame, text="Sağ:").grid(row=0, column=2, padx=5, pady=5)
    margin_right_var = tk.StringVar(value=str(printer_settings.get_setting("margin_right")))
    margin_right_entry = ctk.CTkEntry(margins_frame, width=60, textvariable=margin_right_var)
    margin_right_entry.grid(row=0, column=3, padx=5, pady=5)
    
    # Üst kenar boşluğu
    ctk.CTkLabel(margins_frame, text="Üst:").grid(row=1, column=0, padx=5, pady=5)
    margin_top_var = tk.StringVar(value=str(printer_settings.get_setting("margin_top")))
    margin_top_entry = ctk.CTkEntry(margins_frame, width=60, textvariable=margin_top_var)
    margin_top_entry.grid(row=1, column=1, padx=5, pady=5)
    
    # Alt kenar boşluğu
    ctk.CTkLabel(margins_frame, text="Alt:").grid(row=1, column=2, padx=5, pady=5)
    margin_bottom_var = tk.StringVar(value=str(printer_settings.get_setting("margin_bottom")))
    margin_bottom_entry = ctk.CTkEntry(margins_frame, width=60, textvariable=margin_bottom_var)
    margin_bottom_entry.grid(row=1, column=3, padx=5, pady=5)
    
    # Yazı tipi ayarları
    ctk.CTkLabel(settings_frame, text="Yazı Tipi Ayarları:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(15, 5))
    
    font_frame = ctk.CTkFrame(settings_frame)
    font_frame.pack(fill="x", pady=(0, 15))
    
    ctk.CTkLabel(font_frame, text="Boyut:").pack(side="left", padx=(10, 5))
    font_size_var = tk.StringVar(value=str(printer_settings.get_setting("font_size")))
    font_size_entry = ctk.CTkEntry(font_frame, width=60, textvariable=font_size_var)
    font_size_entry.pack(side="left", padx=(0, 15))
    
    ctk.CTkLabel(font_frame, text="Yazı Tipi:").pack(side="left", padx=(10, 5))
    font_family_var = tk.StringVar(value=printer_settings.get_setting("font_family"))
    font_family_options = ["Courier New", "Arial", "Times New Roman", "Consolas", "Verdana"]
    font_family_dropdown = ctk.CTkOptionMenu(font_frame, values=font_family_options, variable=font_family_var)
    font_family_dropdown.pack(side="left", padx=(0, 15))
    
    # Fiş genişliği (karakter sayısı)
    ctk.CTkLabel(settings_frame, text="Fiş Genişliği (karakter sayısı):", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(15, 5))
    
    receipt_width_frame = ctk.CTkFrame(settings_frame)
    receipt_width_frame.pack(fill="x", pady=(0, 15))
    
    receipt_width_var = tk.StringVar(value=str(printer_settings.get_setting("receipt_width_chars")))
    receipt_width_entry = ctk.CTkEntry(receipt_width_frame, width=60, textvariable=receipt_width_var)
    receipt_width_entry.pack(side="left", padx=(10, 5))
    
    ctk.CTkLabel(receipt_width_frame, text="karakter").pack(side="left")
    
    # Ek özellikler
    ctk.CTkLabel(settings_frame, text="Ek Özellikler:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(15, 5))
    
    features_frame = ctk.CTkFrame(settings_frame)
    features_frame.pack(fill="x", pady=(0, 15))
    
    # Logo yazdırma
    print_logo_var = tk.BooleanVar(value=printer_settings.get_setting("print_logo"))
    ctk.CTkCheckBox(features_frame, text="Logo Yazdır", variable=print_logo_var).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    # Otomatik kesim
    auto_cut_var = tk.BooleanVar(value=printer_settings.get_setting("auto_cut"))
    ctk.CTkCheckBox(features_frame, text="Otomatik Kesim (Thermal)", variable=auto_cut_var).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    # Barkod yazdırma
    barcode_enabled_var = tk.BooleanVar(value=printer_settings.get_setting("barcode_enabled"))
    ctk.CTkCheckBox(features_frame, text="Barkod Yazdır", variable=barcode_enabled_var).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    # Butonlar için frame
    buttons_frame = ctk.CTkFrame(main_frame)
    buttons_frame.pack(fill="x", pady=(20, 0))
    
    # Kaydet butonu
    def save_settings():
        try:
            # Sayısal değerleri kontrol et
            paper_width = int(paper_width_var.get())
            paper_height = int(paper_height_var.get())
            margin_left = int(margin_left_var.get())
            margin_right = int(margin_right_var.get())
            margin_top = int(margin_top_var.get())
            margin_bottom = int(margin_bottom_var.get())
            font_size = int(font_size_var.get())
            receipt_width = int(receipt_width_var.get())
            
            # Değerleri güncelle
            printer_settings.update_setting("printer_type", printer_type_var.get())
            printer_settings.update_setting("paper_width", paper_width)
            printer_settings.update_setting("paper_height", paper_height)
            printer_settings.update_setting("margin_left", margin_left)
            printer_settings.update_setting("margin_right", margin_right)
            printer_settings.update_setting("margin_top", margin_top)
            printer_settings.update_setting("margin_bottom", margin_bottom)
            printer_settings.update_setting("font_size", font_size)
            printer_settings.update_setting("font_family", font_family_var.get())
            printer_settings.update_setting("print_logo", print_logo_var.get())
            printer_settings.update_setting("auto_cut", auto_cut_var.get())
            printer_settings.update_setting("barcode_enabled", barcode_enabled_var.get())
            printer_settings.update_setting("receipt_width_chars", receipt_width)
            
            # Ayarları kaydet
            if printer_settings.save_settings():
                messagebox.showinfo("Başarılı", "Yazıcı ayarları kaydedildi!")
                dialog.destroy()
            else:
                messagebox.showerror("Hata", "Yazıcı ayarları kaydedilemedi!")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tüm sayısal değerleri doğru formatta girin!")
    
    ctk.CTkButton(buttons_frame, text="Kaydet", command=save_settings, width=120).pack(side="left", padx=(0, 10))
    
    # Sıfırla butonu
    def reset_settings():
        if messagebox.askyesno("Sıfırla", "Tüm yazıcı ayarlarını varsayılanlara sıfırlamak istediğinizden emin misiniz?"):
            printer_settings.reset_settings()
            dialog.destroy()
            show_printer_settings_dialog(parent, printer_settings)  # Pencereyi yeniden aç
    
    ctk.CTkButton(buttons_frame, text="Sıfırla", command=reset_settings, width=120, fg_color="#ff6666", hover_color="#ff3333").pack(side="left")
    
    # İptal butonu
    ctk.CTkButton(buttons_frame, text="İptal", command=dialog.destroy, width=120, fg_color="#999999", hover_color="#777777").pack(side="right")
    
    # Yazıcı tipine göre ilgili alanları etkinleştir/devre dışı bırak
    def update_ui_based_on_printer_type(*args):
        printer_type = printer_type_var.get()
        
        if printer_type == "thermal":
            # Thermal yazıcı için boyutları güncelle
            paper_width_var.set("80")  # 80mm genişlik
            auto_cut_var.set(True)  # Otomatik kesim aktif
        elif printer_type == "label":
            # Etiket yazıcısı için boyutları güncelle
            paper_width_var.set("62")  # 62mm genişlik
            paper_height_var.set("100")  # 100mm yükseklik
            auto_cut_var.set(False)  # Otomatik kesim pasif
        else:  # standard
            # Standart yazıcı için A4 boyutları
            paper_width_var.set("210")  # A4 genişlik
            paper_height_var.set("297")  # A4 yükseklik
            auto_cut_var.set(False)  # Otomatik kesim pasif
    
    # Yazıcı tipi değiştiğinde UI'ı güncelle
    printer_type_var.trace_add("write", update_ui_based_on_printer_type)
    
    # Diyaloğu göster
    dialog.transient(parent)  # Ana pencereye bağlı
    dialog.wait_visibility()  # Pencere görünür olana kadar bekle
    dialog.focus_set()  # Klavye odağını al
    
    return dialog

