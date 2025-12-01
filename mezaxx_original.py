#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Mezat Yardımcısı – Tek Dosya, Hatasız, Kapanmaz
Python ≥3.8 – Windows / Linux / macOS
"""

import json
import os
import re
import sys
import time
import uuid
import socket
import logging
import datetime
import tempfile
import threading
import platform
import subprocess
import hashlib
import webbrowser
import importlib.util  # Dinamik modül yükleme için
from queue import Queue
from pathlib import Path

# Gerekli modülleri kontrol et ve yüklemeyi dene
def check_required_modules():
    try:
        # auto_installer.py dosyasını çalıştır (eğer mevcutsa)
        if os.path.exists("auto_installer.py"):
            print("Modül kontrolü yapılıyor...")
            spec = importlib.util.spec_from_file_location("auto_installer", "auto_installer.py")
            installer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installer)
            installer.main()
    except Exception as e:
        print(f"Otomatik modül kontrolü sırasında hata: {e}")

# Program başlamadan önce modülleri kontrol et
check_required_modules()

try:
    import requests
    import customtkinter as ctk
    import tkinter as tk
    from tkinter import messagebox, filedialog, simpledialog
    import pygame  # Ses efektleri için
    from PIL import Image
except ImportError as e:
    print(f"Gerekli modül yüklenemedi: {e}")
    print("Lütfen 'pip install -r requirements.txt' komutu ile gerekli modülleri yükleyin.")
    time.sleep(5)
    sys.exit(1)

# Kritik CustomTkinter hatalarını önlemek için özel patch
import sys
# TclError hatalarını yakalamak için daha erken tanımlıyoruz
# Hata mesajlarını bastırmak için null_writer kullanıyoruz
class NullWriter:
    def write(self, *args, **kwargs):
        pass
    def flush(self):
        pass
        
# sys.stderr'i NullWriter ile değiştiriyoruz
sys.stderr = NullWriter()

# ChatDownloader modülünü kontrol et ve yüklemeyi dene
try:
    from chat_downloader import ChatDownloader
except ImportError:
    ChatDownloader = None
    print("ChatDownloader modülü bulunamadı. Yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "chat-downloader>=0.1.8"])
        print("ChatDownloader başarıyla yüklendi, yeniden yükleniyor...")
        try:
            from chat_downloader import ChatDownloader
        except ImportError:
            print("ChatDownloader yüklendi ancak içe aktarılamadı. Program sınırlı işlevsellikle devam edecek.")
    except Exception as e:
        print(f"ChatDownloader yüklenirken hata oluştu: {e}")
        print("Program sınırlı işlevsellikle devam edecek.")

# -------------------- GLOBAL AYARLAR --------------------
logging.basicConfig(
    filename="mezat.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK = {
    "primary": "#2563eb", "secondary": "#10b981", "accent": "#f59e0b",
    "danger": "#ef4444", "dark": "#1e293b", "darker": "#0f172a",
    "light": "#f8fafc", "gray": "#64748b", "card": "#334155"
}
LIGHT = {
    "primary": "#3b82f6", "secondary": "#10b981", "accent": "#f59e0b",
    "danger": "#ef4444", "dark": "#f1f5f9", "darker": "#e2e8f0",
    "light": "#1e293b", "gray": "#64748b", "card": "#f8fafc"
}

TRANSLATIONS = {
    "tr": {"app_title": "🎯 YouTube Mezat Yardımcısı", "settings": "⚙️ Ayarlar",
           "connection_none": "● Bağlantı Yok", "connection_connecting": "● Bağlantı Kuruluyor...",
           "connection_connected": "● Bağlandı", "live_chat": "💬 Canlı Chat", "live": "🔴 CANLI",
           "offers": "💰 Teklifler", "offers_count": "{} teklif", "product_settings": "📋 Ürün Ayarları",
           "product_name": "Ürün Adı:", "product_name_placeholder": "Ürün adını girin...",
           "fixed_price": "💰 Sabit Fiyat", "fixed_product": "📦 Sabit Ürün",
           "highest_offer": "🏆 En Yüksek Teklif", "target_price": "Hedef Fiyat (TL):",
           "user_header": "Kullanıcı", "offer_header": "Teklif", "time_header": "Zaman",
           "action_header": "İşlem", "product_price": "Ürün Fiyatı (TL):", "stock_count": "Stok Adedi:",
           "mezat_control": "🎯 Mezat Kontrolü", "start": "▶️ BAŞLAT", "stop": "⏹️ DURDUR",
           "paid_users": "👤 Ödeme Yapanlar", "paid_users_count": "{} kullanıcı", "manage": "🛠️ Yönet",
           "ready": "📡 Hazır - Bağlantı bekleniyor...", "mezat_status": "🎯 Mezat: {}",
           "active": "Aktif", "passive": "Pasif", "stream_url": "🔗 Canlı Yayın URL'si",
           "start_chat": "▶️ Chat'i Başlat", "stop_chat": "⏹️ Chat'i Durdur",
           "add": "➕ Ekle", "remove": "➖ Çıkar", "print": "🖨️ Yazdır",
           "settings_title": "⚙️ Ayarlar", "appearance": "Görünüm Modu:",
           "dark_mode": "🌙 Karanlık Mod", "light_mode": "☀️ Aydınlık Mod",
           "language": "Dil:", "save": "💾 Kaydet", "cancel": "❌ İptal",
           "settings_saved": "Ayarlar Kaydedildi", "settings_saved_message": "Değişiklikler uygulandı.",
           "ok": "Tamam"},
    "en": {"app_title": "🎯 YouTube Auction Assistant", "settings": "⚙️ Settings",
           "connection_none": "● No Connection", "connection_connecting": "● Connecting...",
           "connection_connected": "● Connected", "live_chat": "💬 Live Chat", "live": "🔴 LIVE",
           "offers": "💰 Offers", "offers_count": "{} offers", "product_settings": "📋 Product Settings",
           "product_name": "Product Name:", "product_name_placeholder": "Enter product name...",
           "fixed_price": "💰 Fixed Price", "fixed_product": "📦 Fixed Product",
           "highest_offer": "🏆 Highest Offer", "target_price": "Target Price (TL):",
           "user_header": "User", "offer_header": "Offer", "time_header": "Time",
           "action_header": "Action", "product_price": "Product Price (TL):", "stock_count": "Stock Count:",
           "mezat_control": "🎯 Auction Control", "start": "▶️ START", "stop": "⏹️ STOP",
           "paid_users": "👤 Paid Users", "paid_users_count": "{} users", "manage": "🛠️ Manage",
           "ready": "📡 Ready - Waiting for connection...", "mezat_status": "🎯 Auction: {}",
           "active": "Active", "passive": "Passive", "stream_url": "🔗 Live Stream URL",
           "start_chat": "▶️ Start Chat", "stop_chat": "⏹️ Stop Chat",
           "add": "➕ Add", "remove": "➖ Remove", "print": "🖨️ Print",
           "settings_title": "⚙️ Settings", "appearance": "Appearance Mode:",
           "dark_mode": "🌙 Dark Mode", "light_mode": "☀️ Light Mode",
           "language": "Language:", "save": "💾 Save", "cancel": "❌ Cancel",
           "settings_saved": "Settings Saved", "settings_saved_message": "Changes applied.",
           "ok": "OK"}
}

# -------------------- YARDIMCI FONKSİYONLAR --------------------
def get_machine_fingerprint():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
        os_info = f"{platform.system()}-{platform.release()}"
        return hashlib.sha256(f"{ip}-{mac}-{os_info}".encode()).hexdigest()[:16]
    except Exception as e:
        logging.exception("fingerprint")
        return "unknown"

def validate_license_code(channel, code):
    try:
        with open("license_codes.json", encoding="utf-8") as f:
            data = json.load(f)
        if code not in data.get("valid_codes", []):
            return False
        machine = get_machine_fingerprint()
        usage_file = "license_usage.json"
        usage = {}
        if os.path.exists(usage_file):
            with open(usage_file, encoding="utf-8") as f:
                usage = json.load(f)
        if code in usage and usage[code]["fingerprint"] != machine:
            logging.warning(f"Lisans kodu başka makinede kullanılıyor: {code}")
            return False
        if code not in usage:
            usage[code] = {"fingerprint": machine, "first_use": datetime.datetime.now().isoformat(),
                           "channel": channel, "ip": socket.gethostbyname(socket.gethostname())}
            with open(usage_file, "w", encoding="utf-8") as f:
                json.dump(usage, f, ensure_ascii=False, indent=2)
        channel_licenses = {k.lower(): v for k, v in data.get("channel_licenses", {}).items()}
        if channel.lower() in channel_licenses:
            return code in channel_licenses[channel.lower()]
        return code in data["valid_codes"][:100]
    except Exception as e:
        logging.exception("license")
        return False

# -------------------- AUTH EKRANI --------------------
class AuthScreen:
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = ctk.CTk()
        self.root.title("YouTube Mezat Yardımcısı - Kimlik Doğrulama")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.colors = DARK
        self.setup_keyboard_blocking()
        self.build_ui()

    def setup_keyboard_blocking(self):
        def block(event):
            if (event.state == 8 and event.keysym == "F4") or (event.state == 4 and event.keysym in ("w", "q")):
                return "break"
        self.root.bind_all("<Key>", block)

    def build_ui(self):
        main = ctk.CTkFrame(self.root, fg_color=self.colors["darker"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(main, height=80, fg_color=self.colors["primary"], corner_radius=15)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🎯 YouTube Mezat Yardımcısı", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=20)

        form = ctk.CTkFrame(main, fg_color=self.colors["card"], corner_radius=15)
        form.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(form, text="📋 Kimlik Doğrulama", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.colors["light"]).pack(pady=20)
        ctk.CTkLabel(form, text="YouTube kanal URL'si:", text_color=self.colors["light"]).pack(anchor="w", padx=40)
        self.youtube_entry = ctk.CTkEntry(form, placeholder_text="https://www.youtube.com/@kanaladi", height=40, corner_radius=10, border_width=2, border_color=self.colors["primary"])
        self.youtube_entry.pack(fill="x", padx=40, pady=(0, 15))

        ctk.CTkLabel(form, text="Lisans Kodu:", text_color=self.colors["light"]).pack(anchor="w", padx=40)
        self.key_entry = ctk.CTkEntry(form, placeholder_text="Size verilen kod", height=40, corner_radius=10, border_width=2, border_color=self.colors["secondary"])
        self.key_entry.pack(fill="x", padx=40, pady=(0, 20))

        ctk.CTkButton(form, text="✅ Doğrula ve Devam Et", command=self.authenticate, height=45, corner_radius=15, fg_color=self.colors["secondary"], hover_color="#059669", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=40, pady=(0, 30))

        contact = ctk.CTkFrame(form, fg_color=self.colors["dark"], corner_radius=10)
        contact.pack(fill="x", padx=40, pady=(0, 20))
        ctk.CTkLabel(contact, text="📞 İletişim & Destek", font=ctk.CTkFont(weight="bold"), text_color=self.colors["light"]).pack(pady=10)
        ctk.CTkButton(contact, text="💬 WhatsApp", command=lambda: self.open_contact("wa"), fg_color="#25D366", height=32, corner_radius=10).pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkButton(contact, text="📧 E-mail", command=lambda: self.open_contact("mail"), fg_color=self.colors["accent"], height=32, corner_radius=10).pack(fill="x", padx=20, pady=(0, 12))

    def authenticate(self):
        url = self.youtube_entry.get().strip()
        code = self.key_entry.get().strip()
        if not url or not code:
            messagebox.showerror("Hata", "Tüm alanları doldurun!")
            return
        channel = self.extract_channel(url)
        if not channel:
            messagebox.showerror("Hata", "Geçersiz YouTube kanal URL'si!")
            return
        if not validate_license_code(channel, code):
            messagebox.showerror("Hata", "Geçersiz lisans kodu veya yetkisiz kanal!")
            return
        auth = {"youtube_name": channel, "youtube_url": url, "authenticated": True}
        with open("auth_data.json", "w", encoding="utf-8") as f:
            json.dump(auth, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Başarılı", f"Hoş geldiniz {channel}!")
        self.root.destroy()
        self.on_success(channel)

    def extract_channel(self, url):
        try:
            if "@" in url:
                return url.split("@")[1].split("/")[0]
            if "/c/" in url:
                return url.split("/c/")[1].split("/")[0]
            if "/channel/" in url:
                return url.split("/channel/")[1].split("/")[0]
            return url.strip()
        except:
            return None

    def open_contact(self, typ):
        url = self.youtube_entry.get().strip()
        code = self.key_entry.get().strip()
        msg = f"Merhaba,\nYouTube Mezat Yardımcısı için destek istiyorum.\nKanal: {url}\nKod: {code}"
        if typ == "wa":
            webbrowser.open(f"https://wa.me/?text={requests.utils.quote(msg)}")
        else:
            webbrowser.open(f"mailto:support@example.com?subject=Destek&body={requests.utils.quote(msg)}")

    def run(self):
        self.root.mainloop()

# -------------------- ANA UYGULAMA --------------------
class ModernYouTubeMezatYardimcisi:
    def __init__(self, authorized_youtube_name):
        # Temel değişkenleri başlat
        self.authorized_youtube_name = authorized_youtube_name
        self.root = ctk.CTk()
        self.root.title("🎯 YouTube Mezat Yardımcısı")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.colors = DARK
        # YouTube için durdurma event'i
        self.youtube_stop_event = threading.Event()
        self.stop_event = self.youtube_stop_event  # Geriye uyumluluk için
        
        # YouTube için mesaj kuyruğu ve thread
        self.youtube_msg_queue = Queue(maxsize=10000)
        self.msg_queue = self.youtube_msg_queue  # Geriye uyumluluk için
        
        # Thread yönetimi
        self.youtube_chat_thread = None
        self.chat_thread = None  # Geriye uyumluluk için
        
        # Platform durumu
        self.youtube_connected = False
        
        # Platform URL'si
        self.youtube_last_url = None
        self.last_url = None  # Geriye uyumluluk için
        
        self.offers_list = []
        self.paid_users = []
        self.paid_user_details = {}  # Kullanıcı detayları için sözlük
        self.is_mezat_active = False
        self.current_product = ""
        self.current_price = ""
        self.current_platform = "YouTube"  # Varsayılan platform
        self.current_mode = "fixed"
        self.current_stock = 0
        self.sold_count = 0
        self.last_url = None
        
        # Mesaj işleme için zaman damgaları
        self.mezat_start_time = 0  # Mezat başlangıç zamanı 
        self.mezat_stopped_time = 0  # Mezat bitiş zamanı
        self.processed_message_cache = set()  # İşlenmiş mesaj önbelleği (tekrarları önlemek için)
        
        # Ses efektleri için ayarlar
        self.sounds_enabled = True  # Varsayılan olarak sesler açık
        self.sound_theme = "fight"  # Varsayılan ses teması ("fight" veya "money")
        self.current_sound_index = 0  # Şu anki ses efekti indeksi
        
        # Pygame ses modülünü başlat
        try:
            pygame.mixer.init()
            logging.info("Ses sistemi başlatıldı")
        except Exception as e:
            logging.error(f"Ses sistemi başlatılamadı: {e}")
            self.sounds_enabled = False
        self.chat_thread = None
        self.thread_last_alive = 0
        self._last_user_text = {}
        self.language = "tr"
        self.appearance_mode = "dark"
        
        # UI elemanları önceden tanımla
        self.print_all_btn = None
        self.connection_status = None
        
        # Thread kontrol değişkenleri
        self.health_check_job = None
        self.message_processor_job = None
        self.stop_threads = threading.Event()
        self.queue_processor_active = False
        
        # Bağlantı durumu izleyicisi
        self.connection_monitor = None
        try:
            import importlib.util
            if os.path.exists("connection_status.py"):
                # Bağlantı durumu izleyici modülünü yükle
                spec = importlib.util.spec_from_file_location("connection_status", "connection_status.py")
                status_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(status_module)
                
                # Bağlantı durumu izleyicisini oluştur
                self.connection_monitor = status_module.ConnectionStatusMonitor(message_queue=self.message_queue, update_interval=10)
                self.connection_monitor.start()
                logging.info("Bağlantı durumu izleyicisi başlatıldı")
        except Exception as monitor_err:
            logging.error(f"Bağlantı durumu izleyicisi başlatılırken hata: {monitor_err}")
            self.connection_monitor = None
        
        # Konsol Ctrl-C yönetimi (Windows'ta konsol X düğmesi için)
        import signal
        import os
        
        def ignore_sigint(sig, frame):
            # Tamamen yut - ne log ne event
            pass
            
        # Sadece Windows işletim sisteminde
        if os.name == 'nt':
            # Konsol sinyallerini tamamen engelle (Quick Edit ve otomatik SIGINT'leri engeller)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGBREAK, signal.SIG_IGN)
            
            try:
                import win32api
                import win32con
                # Konsol X düğmesi için özel handler
                def console_ctrl_handler(sig, frame):
                    # GUI thread'inde on_closing metodunu çağır
                    self.root.after(0, self.on_closing)
                    return True  # Windows: "Bu sinyali ben işledim"
                    
                win32api.SetConsoleCtrlHandler(console_ctrl_handler, True)
                logging.info("Konsol kapatma yönlendiricisi aktifleştirildi")
            except ImportError:
                logging.warning("win32api modülü bulunamadı - konsol kapatma düzgün çalışmayabilir")
        self.load_settings()
        self.load_user_details_from_file()  # Kullanıcı detaylarını yükle
        self.setup_ui()
        self.setup_keyboard_blocking()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._setup_global_exception_handler()
        self.start_health_check()
        self.start_message_processor()

    # ---------- TEMA & DİL ----------
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", encoding="utf-8") as f:
                    data = json.load(f)
                    self.language = data.get("language", "tr")
                    self.appearance_mode = data.get("appearance_mode", "dark")
                    self.sounds_enabled = data.get("sounds_enabled", True)  # Ses ayarını yükle
                    self.sound_theme = data.get("sound_theme", "fight")  # Ses teması ayarını yükle
                    self.colors = DARK if self.appearance_mode == "dark" else LIGHT
                    ctk.set_appearance_mode(self.appearance_mode)
        except Exception as e:
            logging.exception("load_settings")

    def save_settings(self):
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump({
                    "language": self.language, 
                    "appearance_mode": self.appearance_mode,
                    "sounds_enabled": self.sounds_enabled,
                    "sound_theme": self.sound_theme
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.exception("save_settings")

    def translate(self, key, *args):
        try:
            text = TRANSLATIONS.get(self.language, TRANSLATIONS["tr"]).get(key, key)
            if args:
                text = text.format(*args)
            return text
        except Exception:
            return key

    # ---------- UI ----------
    def setup_ui(self):
        main = ctk.CTkFrame(self.root, fg_color=self.colors["darker"])
        main.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_header(main)
        self.create_content(main)
        self.create_status_bar(main)

    def create_header(self, parent):
        header = ctk.CTkFrame(parent, height=80, fg_color=self.colors["primary"], corner_radius=15)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=self.translate("app_title"), font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(side="left", padx=30)
        
        # Platform durum göstergesi
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=30)
        
        # YouTube durum göstergesi
        self.youtube_status = ctk.CTkLabel(status_frame, text="Bağlantı Yok", font=ctk.CTkFont(size=12), text_color="#fecaca")
        self.youtube_status.pack(side="left", padx=(0, 10))
        
        # Geriye uyumluluk
        self.connection_status = self.youtube_status
        ctk.CTkButton(header, text=self.translate("settings"), command=self.show_settings, width=100, height=40, corner_radius=10, fg_color=self.colors["accent"]).pack(side="right", padx=10)

    def create_content(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.create_left_panel(content)
        self.create_right_panel(content)

    def create_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Chat
        chat_frame = ctk.CTkFrame(left, fg_color=self.colors["card"], corner_radius=15)
        chat_frame.pack(fill="x", pady=(0, 10))
        header = ctk.CTkFrame(chat_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="💬 Canlı Chat", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.colors["light"]).pack(side="left")
        self.live_indicator = ctk.CTkLabel(header, text="🔴 CANLI", font=ctk.CTkFont(size=10, weight="bold"), text_color="#ef4444")
        self.live_indicator.pack(side="right")
        self.chat_container = ctk.CTkScrollableFrame(chat_frame, height=200, fg_color=self.colors["dark"], corner_radius=10)
        self.chat_container.pack(fill="x", padx=20, pady=(0, 20))

        # Offers
        offers_frame = ctk.CTkFrame(left, fg_color=self.colors["card"], corner_radius=15)
        offers_frame.pack(fill="both", expand=True)
        header = ctk.CTkFrame(offers_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="💰 Teklifler", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.colors["light"]).pack(side="left")
        self.offer_count_label = ctk.CTkLabel(header, text="0 teklif", font=ctk.CTkFont(size=12), text_color=self.colors["gray"])
        self.offer_count_label.pack(side="right")
        self.print_all_btn = ctk.CTkButton(header, text="🖨️ Yazdır", command=self.print_all_offers, width=80, height=30, corner_radius=10, fg_color=self.colors["accent"])
        self.print_all_btn.pack(side="right", padx=10)
        self.create_offers_table(offers_frame)

    def create_offers_table(self, parent):
        table = ctk.CTkFrame(parent, fg_color=self.colors["dark"], corner_radius=10)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        header_frame = ctk.CTkFrame(table, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        headers = [self.translate("user_header"), self.translate("offer_header"), self.translate("time_header"), self.translate("action_header")]
        widths = [150, 80, 80, 100]
        for h, w in zip(headers, widths):
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["light"], width=w).pack(side="left", padx=10)
        
        # Temiz kod düzeni
        self.offers_container = ctk.CTkScrollableFrame(table, fg_color="transparent", height=200)
        self.offers_container.pack(fill="both", expand=True, padx=10, pady=10)

    def create_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent", width=400)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)
        self.create_stream_controls(right)
        self.create_product_settings(right)
        self.create_mezat_controls(right)
        self.create_paid_users_section(right)

    def create_stream_controls(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=15)
        frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(frame, text="🔗 Canlı Yayın URL'si", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["light"]).pack(anchor="w", padx=20, pady=15)
        
        # YouTube URL girişi
        yt_frame = ctk.CTkFrame(frame, fg_color="transparent")
        yt_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(yt_frame, text="📺 YouTube:", text_color=self.colors["light"], width=80).pack(side="left", padx=(0, 5))
        self.youtube_url_entry = ctk.CTkEntry(yt_frame, placeholder_text="YouTube canlı yayın URL'si", height=35, corner_radius=10, border_width=2, border_color="#FF0000")
        self.youtube_url_entry.pack(side="left", fill="x", expand=True)
        
        # YouTube kontrol butonları
        yt_btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        yt_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.youtube_start_btn = ctk.CTkButton(yt_btn_frame, text="▶️ Başlat", command=self.start_youtube_stream, fg_color="#FF0000", hover_color="#d10000", height=35, corner_radius=15)
        self.youtube_start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.youtube_stop_btn = ctk.CTkButton(yt_btn_frame, text="⏹️ Durdur", command=self.stop_youtube_stream, fg_color="#FF0000", hover_color="#d10000", height=35, corner_radius=15, state="disabled")
        self.youtube_stop_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Eski arayüz için uyumluluk
        self.url_entry = self.youtube_url_entry
        self.stream_start_btn = self.youtube_start_btn
        self.stream_stop_btn = self.youtube_stop_btn

    def create_product_settings(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=15)
        frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(frame, text="📋 Ürün Ayarları", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["light"]).pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(frame, text=self.translate("product_name"), text_color=self.colors["light"]).pack(anchor="w", padx=20)
        self.product_entry = ctk.CTkEntry(frame, placeholder_text=self.translate("product_name_placeholder"), height=35, corner_radius=10, border_width=2, border_color=self.colors["primary"])
        self.product_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.create_price_controls(frame)

    def create_price_controls(self, parent):
        mode_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=10)
        self.mode_var = tk.StringVar(value="fixed")
        for mode, label in [("fixed", self.translate("fixed_price")), ("product", self.translate("fixed_product")), ("highest", self.translate("highest_offer"))]:
            ctk.CTkRadioButton(mode_frame, text=label, variable=self.mode_var, value=mode, command=self.on_mode_change, text_color=self.colors["light"]).pack(side="left", padx=10)
        self.price_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.price_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self.price_frame, text=self.translate("target_price"), text_color=self.colors["light"]).pack(anchor="w")
        self.price_entry = ctk.CTkEntry(self.price_frame, placeholder_text="250", height=35, corner_radius=10, border_width=2, border_color=self.colors["secondary"], validate="key", validatecommand=(self.root.register(lambda v: v.isdigit() or v == ""), "%P"))
        self.price_entry.pack(fill="x", pady=(5, 0))
        self.stock_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.stock_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self.stock_frame, text=self.translate("stock_count"), text_color=self.colors["light"]).pack(anchor="w")
        self.stock_entry = ctk.CTkEntry(self.stock_frame, placeholder_text="20", height=35, corner_radius=10, border_width=2, border_color=self.colors["accent"], validate="key", validatecommand=(self.root.register(lambda v: v.isdigit() or v == ""), "%P"))
        self.stock_entry.pack(fill="x", pady=(5, 0))

    def create_mezat_controls(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=15)
        frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(frame, text="🎯 Mezat Kontrolü", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["light"]).pack(anchor="w", padx=20, pady=10)
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        self.start_button = ctk.CTkButton(btn_frame, text="▶️ BAŞLAT", command=self.start_mezat, height=40, corner_radius=20, fg_color=self.colors["secondary"], hover_color="#059669", font=ctk.CTkFont(weight="bold"))
        self.start_button.pack(fill="x", pady=(0, 5))
        self.stop_button = ctk.CTkButton(btn_frame, text="⏹️ DURDUR", command=self.stop_mezat, height=40, corner_radius=20, fg_color=self.colors["danger"], hover_color="#dc2626", font=ctk.CTkFont(weight="bold"), state="disabled")
        self.stop_button.pack(fill="x")

    def create_paid_users_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=15)
        frame.pack(fill="both", expand=True)
        
        # Başlık ve yönet butonu yan yana
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        # Başlık ve kullanıcı sayısı
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        # Başlık metni - tıklanabilir buton olarak
        title_btn = ctk.CTkButton(
            title_frame, 
            text="👤 Ödeme Yapanlar", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", 
            text_color=self.colors["light"],
            hover_color=self.colors["primary"],
            command=self.show_manage_paid_users,
            height=30,
            corner_radius=8
        )
        title_btn.pack(side="left", anchor="w")
        
        # Kullanıcı sayısı
        self.paid_count_label = ctk.CTkLabel(title_frame, text="0 kullanıcı", font=ctk.CTkFont(size=11), text_color=self.colors["gray"])
        self.paid_count_label.pack(side="right", padx=10)
        
        # Yönet butonu
        ctk.CTkButton(
            header, 
            text="🛠️ Yönet", 
            command=self.show_manage_paid_users, 
            width=100, 
            height=30, 
            corner_radius=10, 
            fg_color=self.colors["primary"]
        ).pack(side="right")
        
        # Kullanıcı listesi
        list_container = ctk.CTkFrame(frame, fg_color=self.colors["dark"], corner_radius=10)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.paid_listbox = ctk.CTkTextbox(
            list_container, 
            height=100, 
            font=ctk.CTkFont(size=10), 
            fg_color=self.colors["dark"], 
            text_color=self.colors["light"]
        )
        self.paid_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Kullanıcı listesini tıklanabilir yap
        self.paid_listbox.bind("<Button-1>", lambda e: self.show_manage_paid_users())

    def create_status_bar(self, parent):
        bar = ctk.CTkFrame(parent, height=35, fg_color=self.colors["dark"], corner_radius=10)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.status_label = ctk.CTkLabel(bar, text=self.translate("ready"), font=ctk.CTkFont(size=11), text_color=self.colors["gray"])
        self.status_label.pack(side="left", padx=20)
        self.mezat_status_label = ctk.CTkLabel(bar, text=self.translate("mezat_status", self.translate("passive")), font=ctk.CTkFont(size=11, weight="bold"), text_color=self.colors["accent"])
        self.mezat_status_label.pack(side="right", padx=20)

    # ---------- EVENTS ----------
    def on_mode_change(self):
        mode = self.mode_var.get()
        # Eğer mezat aktifse ve mod değiştiyse, mezatı durdur
        if self.is_mezat_active:
            self.stop_mezat()
            self.show_notification("Mod Değişti", "Mezat modu değiştiği için mezat durduruldu. Lütfen tekrar başlatın.", "warning")
            
        if mode in ("fixed", "product"):
            self.price_frame.pack(fill="x", padx=20, pady=10)
            self.stock_frame.pack(fill="x", padx=20, pady=10)
            label = self.translate("target_price") if mode == "fixed" else self.translate("product_price")
            for w in self.price_frame.winfo_children():
                if isinstance(w, ctk.CTkLabel):
                    w.configure(text=label)
        else:
            self.price_frame.pack_forget()
            self.stock_frame.pack_forget()

    def start_mezat(self):
        self.current_product = self.product_entry.get().strip() or "Ürün"
        self.current_price = self.price_entry.get().strip() or "0"
        self.current_mode = self.mode_var.get()
        self.current_stock = int(self.stock_entry.get().strip() or "0")
        self.sold_count = 0
        self.offers_list = []  # Her mezat başlangıcında teklifleri temizle
        self.refresh_offers_table()  # Teklif tablosunu temizle
        self.offer_count_label.configure(text="0 teklif")
        
        # Yeni mezat başlangıcında son görülen mesaj timestamp'ini kaydet
        # Bu sayede yalnızca bu zamandan sonraki mesajlar tekliflere eklenecek
        self.mezat_start_time = time.time()
        self.is_mezat_active = True
        
        # İşlenmiş mesaj önbelleğini temizle - yeni mezat yeni başlangıç
        self.processed_message_cache = set()
        
        # Mezat başlangıç mesajı gönder
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.safe_append_chat("SISTEM", f"--- MEZAT BAŞLADI - {self.current_product} ---", current_time, "Sistem")
        
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.mezat_status_label.configure(text=f"🎯 {self.current_product} Mezatı: {self.translate('active')}", text_color=self.colors["secondary"])
        self.show_notification("Mezat Başladı", f"{self.current_product} mezatı başlatıldı!", "success")

    # Ses efektini çalma fonksiyonu
    def play_sound_effect(self, sound_name):
        if not self.sounds_enabled:
            return  # Sesler kapalıysa çalma
            
        try:
            # Ses temasına göre yolu belirle
            if self.sound_theme == "money":
                # Money ses teması kullan (t_sound klasöründen)
                if sound_name == "finish":
                    # Money teması için bitiş sesi
                    sound_file = "finish2.mp3"
                else:
                    # Money teması için normal sesler (1t.mp3, 2t.mp3, vb.)
                    sound_file = f"{sound_name}t.mp3"
                    
                sound_path = os.path.join("sound", "t_sound", sound_file)
            else:
                # Fight (varsayılan) ses teması kullan
                sound_path = os.path.join("sound", f"{sound_name}.mp3")
                
            if os.path.exists(sound_path):
                # Önceki sesi durdur ve yeni sesi çal
                pygame.mixer.music.stop()
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
                logging.info(f"Ses çalınıyor: {sound_path} (tema: {self.sound_theme})")
            else:
                logging.warning(f"Ses dosyası bulunamadı: {sound_path}")
        except Exception as e:
            logging.error(f"Ses çalma hatası: {e}")

    def stop_mezat(self):
        self.is_mezat_active = False
        
        # Mezat bitiminde ses çal
        self.play_sound_effect("finish")
        
        # Mezat durdurulduğunda chat'e otomatik bir sistem mesajı gönder
        # Bu mesaj, sonraki mezat için bir sınır noktası olarak kullanılabilir
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.mezat_stopped_time = time.time()
        self.safe_append_chat("SISTEM", f"--- MEZAT DURDURULDU - {self.current_product} ---", current_time, "Sistem")
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.mezat_status_label.configure(text=self.translate("mezat_status", self.translate("passive")), text_color=self.colors["accent"])
        logging.info(f"Mezat durduruldu: {current_time}")
        self.show_notification("Mezat Durduruldu", "Mezat durduruldu", "info")

    def start_youtube_stream(self):
        url = self.youtube_url_entry.get().strip()
        if not url:
            self.show_notification("Hata", "YouTube URL'si girin", "error")
            return
        
        # Basit URL kontrolü
        if "youtube.com" not in url.lower() and "youtu.be" not in url.lower():
            self.show_notification("Hata", "Geçerli YouTube URL'si girin", "error")
            return
        
        # UI güncelle
        self.youtube_status.configure(text="YT: Bağlanıyor...", text_color="yellow")
        self.youtube_start_btn.configure(state="disabled")
        self.youtube_stop_btn.configure(state="normal")
        
        # Önceki thread'i durdur
        self.youtube_stop_event.set()
        time.sleep(0.1)
        
        # Yeni thread başlat
        self.youtube_stop_event.clear()
        self.youtube_last_url = url
        
        # Basit ChatDownloader ile bağlan
        self.youtube_chat_thread = threading.Thread(
            target=self.chat_worker, 
            args=(url, "YouTube", self.youtube_stop_event, self.youtube_msg_queue), 
            daemon=True, 
            name="YouTubeChatWorker"
        )
        self.youtube_chat_thread.start()
        
        # Geriye uyumluluk
        self.chat_thread = self.youtube_chat_thread
        self.last_url = self.youtube_last_url
        
        logging.info(f"YouTube chat başlatıldı: {url}")
        self.show_notification("Başlatıldı", "YouTube chat bağlantısı başlatıldı", "info")

    def stop_youtube_stream(self):
        # YouTube chatini durdur
        self.youtube_stop_event.set()
        if self.youtube_chat_thread and self.youtube_chat_thread.is_alive():
            try:
                self.youtube_chat_thread.join(0.5)  # Kısa bir süre bekle
            except Exception:
                pass
            
        self.youtube_chat_thread = None
        self.youtube_connected = False
        
        # UI durumunu güncelle
        self.youtube_start_btn.configure(state="normal")
        self.youtube_stop_btn.configure(state="disabled")
        self.show_notification("Bilgi", "YouTube chat bağlantısı durduruldu", "info")
        
        # Sistem mesajı ekle
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.safe_append_chat("SISTEM", "--- YOUTUBE BAĞLANTISI DURDURULDU ---", current_time, "YouTube")

    # TikTok kaldırıldığından bu fonksiyon artık kullanılmıyor
    def start_tiktok_stream_removed(self):
        url = self.tiktok_url_entry.get().strip()
        if not url:
            self.show_notification("Hata", "Geçerli bir TikTok canlı yayın URL'si girin", "error")
            return
            
        # URL formatı ve debug bilgisi
        logging.info(f"TikTok bağlantısı başlatılıyor: {url}")
        
        # URL formatını kontrol et
        is_tiktok = "tiktok.com" in url.lower()
        
        if not is_tiktok:
            self.show_notification("Hata", "Geçerli bir TikTok URL'si girin", "error")
            return
        
        # TikTok URL'si için formatlama ve normalize etme
        if not url.startswith("http"):
            url = f"https://{url}"
            
        # TikTok URL'lerini düzeltme ve normalize etme
        # Örnek: https://www.tiktok.com/@username/live -> https://www.tiktok.com/@username/live
        if "tiktok.com" in url:
            # URL'de zaten /live var mı kontrol et
            if not "/live" in url and "@" in url:
                url_parts = url.split("?")[0].rstrip("/")
                url = f"{url_parts}/live"
                logging.info(f"TikTok URL'si normalize edildi: {url}")
            
            # Mobil URL düzeltmesi
            if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
                try:
                    # Kısa URL'yi takip et ve gerçek URL'yi al
                    import requests
                    response = requests.head(url, allow_redirects=True)
                    if response.status_code == 200:
                        final_url = response.url
                        if "@" in final_url:
                            username = final_url.split("@")[1].split("/")[0].split("?")[0]
                            url = f"https://www.tiktok.com/@{username}/live"
                            logging.info(f"TikTok kısa URL'si çözüldü: {url}")
                except Exception as e:
                    logging.error(f"TikTok URL çözümleme hatası: {e}")
                    # Hata durumunda orijinal URL ile devam et
            
        self.tiktok_url_entry.delete(0, "end")
        self.tiktok_url_entry.insert(0, url)
        
        # UI durumunu güncelle
        self.tiktok_start_btn.configure(state="disabled")
        self.tiktok_stop_btn.configure(state="normal")
        
        # Önceki TikTok thread varsa durdur
        self.tiktok_stop_event.set()
        if self.tiktok_chat_thread and self.tiktok_chat_thread.is_alive():
            try:
                self.tiktok_chat_thread.join(0.5)  # Kısa bir süre bekle
            except Exception:
                pass
            
        # TikTok bağlantı stratejisi: Yeni TikTokLive 5.0.8 > WebSocket > HTML Scraping > Selenium > chat-downloader
        self.tiktok_stop_event.clear()
        self.tiktok_last_url = url
        
        # Bağlantı denemesi sayacı
        connection_attempts = 0
        
        # 0. YÖNTEM: Yeni TikTokLive 5.0.8 kütüphanesi ile bağlantı (en güvenilir ve tek seferde bağlanır)
        try:
            import importlib.util
            if os.path.exists("tiktok_chat.py"):
                # Yeni TikTokLive modülünü yükle
                spec = importlib.util.spec_from_file_location("tiktok_chat", "tiktok_chat.py")
                chat_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(chat_module)
                
                # Yeni TikTokLive bağlantısı kullan
                logging.info("TikTok için yeni TikTokLive 5.0.8 kütüphanesi kullanılıyor...")
                self.tiktok_chat_thread = chat_module.start_tiktok_chat(
                    url, 
                    self.tiktok_msg_queue, 
                    self.tiktok_stop_event
                )
                connection_attempts += 1
                
                # Başarılı bildirim
                self.message_queue.put(("SISTEM", "TikTok Live bağlantısı başlatılıyor (tek seferde bağlanacak)...", time.strftime("%H:%M:%S"), "TikTok"))
                
                # Diğer yöntemleri deneme, Yeni TikTokLive yeterli
                return
        except Exception as live_err:
            logging.error(f"Yeni TikTok Live bağlantı hatası: {live_err}")
            
        # 1. YÖNTEM: Eski TikTokLive kütüphanesi ile bağlantı
        if connection_attempts == 0:
            try:
                import importlib.util
                if os.path.exists("tiktok_live_connector.py"):
                    # TikTokLive modülünü yükle
                    spec = importlib.util.spec_from_file_location("tiktok_live_connector", "tiktok_live_connector.py")
                    live_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(live_module)
                    
                    # TikTokLive bağlantısı kullan
                    logging.info("TikTok için eski TikTokLive kütüphanesi kullanılıyor...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=live_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokLiveWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok Live bağlantısı başlatılıyor (eski yöntem)...", time.strftime("%H:%M:%S"), "TikTok"))
                    
                    # Diğer yöntemleri deneme, TikTokLive yeterli
                    return
            except Exception as live_err:
                logging.error(f"Eski TikTok Live bağlantı hatası: {live_err}")
            
        # 1. YÖNTEM: WebSocket ile doğrudan bağlantı
        if connection_attempts == 0:
            try:
                if os.path.exists("tiktok_direct_websocket.py"):
                    # WebSocket modülünü yükle
                    spec = importlib.util.spec_from_file_location("tiktok_direct_websocket", "tiktok_direct_websocket.py")
                    ws_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(ws_module)
                    
                    # WebSocket bağlantısı kullan
                    logging.info("TikTok için doğrudan WebSocket bağlantısı kullanılıyor...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=ws_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokWebSocketWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı başlatılıyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    
                    # Diğer yöntemleri deneme, WebSocket yeterli
                    return
            except Exception as ws_err:
                logging.error(f"TikTok WebSocket bağlantı hatası: {ws_err}")
        
        # 1. YÖNTEM: HTML Scraping ile doğrudan bağlantı (API olmadan)
        if connection_attempts == 0:
            try:
                if os.path.exists("html_chat_scraper.py"):
                    # HTML scraper modülünü yükle
                    spec = importlib.util.spec_from_file_location("html_chat_scraper", "html_chat_scraper.py")
                    scraper_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(scraper_module)
                    
                    # HTML scraping bağlantısı kullan
                    logging.info("TikTok için HTML scraping bağlantısı kullanılıyor (API olmadan)...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=scraper_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokHTMLScraperWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok HTML scraping bağlantısı başlatılıyor (API olmadan)...", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as scraper_err:
                logging.error(f"TikTok HTML scraper bağlantı hatası: {scraper_err}")
        
        # 1. YÖNTEM: Selenium ile doğrudan tarayıcı bağlantısı (yedek)
        if connection_attempts == 0:
            try:
                if os.path.exists("selenium_chat.py"):
                    # Selenium bağlantı modülünü yükle
                    spec = importlib.util.spec_from_file_location("selenium_chat", "selenium_chat.py")
                    selenium_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(selenium_module)
                    
                    # Selenium bağlantısı kullan
                    logging.info("TikTok için Selenium bağlantısı kullanılıyor...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=selenium_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokSeleniumChatWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok Selenium bağlantısı başlatılıyor (tarayıcı açılıyor)...", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as selenium_err:
                logging.error(f"TikTok Selenium bağlantı hatası: {selenium_err}")
        
        # 1. YÖNTEM: WebSocket direkt bağlantı
        if connection_attempts == 0:
            try:
                if os.path.exists("websocket_chat.py"):
                    # WebSocket bağlantı modülünü yükle
                    spec = importlib.util.spec_from_file_location("websocket_chat", "websocket_chat.py")
                    ws_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(ws_module)
                    
                    # WebSocket bağlantısı kullan
                    logging.info("TikTok için WebSocket bağlantısı kullanılıyor...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=ws_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokWebSocketChatWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı deneniyor...", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as ws_err:
                logging.error(f"TikTok WebSocket bağlantı hatası: {ws_err}")
        
        # 2. YÖNTEM: Doğrudan API bağlantısı
        if connection_attempts == 0:
            try:
                if os.path.exists("direct_tiktok.py"):
                    # Güçlendirilmiş bağlantı modülünü yükle
                    spec = importlib.util.spec_from_file_location("direct_tiktok", "direct_tiktok.py")
                    direct_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(direct_module)
                    
                    # Doğrudan bağlantı kullan
                    logging.info("TikTok için doğrudan API bağlantısı kullanılıyor...")
                    self.tiktok_chat_thread = threading.Thread(
                        target=direct_module.start_tiktok_chat,
                        args=(url, self.tiktok_msg_queue, self.tiktok_stop_event),
                        daemon=True,
                        name="TikTokDirectChatWorker"
                    )
                    self.tiktok_chat_thread.start()
                    connection_attempts += 1
                    
                    # Başarılı bildirim
                    self.message_queue.put(("SISTEM", "TikTok API bağlantısı deneniyor...", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as direct_err:
                logging.error(f"TikTok doğrudan API bağlantı hatası: {direct_err}")
        
        # 3. YÖNTEM: chat-downloader (son çare)
        if connection_attempts == 0:
            try:
                logging.info("TikTok için chat-downloader kullanılıyor (son çare)...")
                self.tiktok_chat_thread = threading.Thread(
                    target=self.chat_worker, 
                    args=(url, "TikTok", self.tiktok_stop_event, self.tiktok_msg_queue), 
                    daemon=True, 
                    name="TikTokChatWorker"
                )
                self.tiktok_chat_thread.start()
                connection_attempts += 1
                
                # Başarılı bildirim
                self.message_queue.put(("SISTEM", "TikTok chat-downloader bağlantısı deneniyor...", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as chat_err:
                logging.error(f"TikTok chat-downloader bağlantı hatası: {chat_err}")
        
        # Hiçbir yöntem çalışmadıysa hata bildir
        if connection_attempts == 0:
            logging.error("TikTok için hiçbir bağlantı yöntemi çalışmadı")
            self.show_notification("Hata", "TikTok bağlantı kurulamadı, hiçbir yöntem çalışmadı", "error")
            self.message_queue.put(("SISTEM", "TikTok bağlantısı kurulamadı, hiçbir yöntem çalışmadı", time.strftime("%H:%M:%S"), "TikTok"))
        
        # Bağlantı başladığında bildirim göster
        self.show_notification("Bağlantı", "TikTok chat başlatıldı", "info")
        
        # Mesajı hemen değil, 5 saniye sonra gönder (chat tam yüklendikten sonra)
        def send_delayed_welcome_message():
            time.sleep(5)  # 5 saniye bekle
            if self.tiktok_chat_thread and self.tiktok_chat_thread.is_alive():  # Thread hala aktif ise
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                self.safe_append_chat("SISTEM", "--- YENİ TIKTOK BAĞLANTISI KURULDU ---", current_time, "TikTok")
        
        # Mesaj gönderme işlemini ayrı bir thread'de başlat
        threading.Thread(target=send_delayed_welcome_message, daemon=True).start()

    # TikTok kaldırıldığından bu fonksiyon artık kullanılmıyor
    def stop_tiktok_stream_removed(self):
        # TikTok chatini durdur
        self.tiktok_stop_event.set()
        
        # Ana TikTok thread'ini durdur
        if self.tiktok_chat_thread and self.tiktok_chat_thread.is_alive():
            try:
                self.tiktok_chat_thread.join(0.5)  # Kısa bir süre bekle
            except:
                pass
                
        # Yedek TikTok thread'ini durdur
        if hasattr(self, 'tiktok_backup_thread') and self.tiktok_backup_thread and self.tiktok_backup_thread.is_alive():
            try:
                self.tiktok_backup_thread.join(0.5)  # Kısa bir süre bekle
            except:
                pass
        
        self.tiktok_chat_thread = None
        if hasattr(self, 'tiktok_backup_thread'):
            self.tiktok_backup_thread = None
            
        self.tiktok_connected = False
        
        # UI durumunu güncelle
        self.tiktok_start_btn.configure(state="normal")
        self.tiktok_stop_btn.configure(state="disabled")
        self.show_notification("Bilgi", "TikTok chat bağlantısı durduruldu", "info")
        
        # Sistem mesajı ekle
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.safe_append_chat("SISTEM", "--- TIKTOK BAĞLANTISI DURDURULDU ---", current_time, "TikTok")

    # Geriye uyumluluk için eski fonksiyonlar
    def start_stream(self):
        # YouTube chat'ini başlat
        self.start_youtube_stream()

    def stop_stream(self):
        # YouTube chat'ini durdur
        self.stop_youtube_stream()

    # ---------- CHAT ----------
    def extract_live_video_id(self, channel_url):
        """Bir YouTube kanalının canlı yayın video ID'sini alır - geliştirilmiş sürüm."""
        try:
            # Gelişmiş HTTP istekleri için session kullan
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            })
            
            # Kanal URL formatını normalize et
            if "@" in channel_url:
                channel_name = channel_url.split('@')[1].split('/')[0]
                base_urls = [f"https://www.youtube.com/@{channel_name}", f"https://www.youtube.com/@{channel_name}/live"]
            elif "/c/" in channel_url:
                channel_name = channel_url.split('/c/')[1].split('/')[0]
                base_urls = [f"https://www.youtube.com/c/{channel_name}", f"https://www.youtube.com/c/{channel_name}/live"]
            elif "/channel/" in channel_url:
                channel_id = channel_url.split('/channel/')[1].split('/')[0]
                base_urls = [f"https://www.youtube.com/channel/{channel_id}", f"https://www.youtube.com/channel/{channel_id}/live"]
            else:
                base_urls = [channel_url, f"{channel_url.rstrip('/')}/live"]
                
            # Daha fazla keşif URL'si ekle - her olasılığı dene
            all_urls = []
            for base in base_urls:
                all_urls.append(base)
                if "/live" not in base:
                    all_urls.append(f"{base.rstrip('/')}/live")
                if "/featured" not in base:
                    all_urls.append(f"{base.rstrip('/')}/featured")
            
            # Tüm olası URL'leri dene
            for url in all_urls:
                logging.info(f"[extract_live] URL kontrol ediliyor: {url}")
                try:
                    # Cookies kabul edilerek daha gerçekçi bir istek yapılır
                    response = session.get(url, timeout=15, allow_redirects=True)
                    
                    # Durum kodu kontrolü
                    if response.status_code != 200:
                        logging.warning(f"[extract_live] URL yanıt kodu: {response.status_code}")
                        continue
                    
                    # Canlı yayın video ID'si için birkaç farklı pattern kontrol et
                    html_content = response.text
                    
                    # Pattern 1: isLiveContent ile işaretlenmiş videoId
                    match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"isLiveContent":true', html_content)
                    if match:
                        logging.info(f"[extract_live] Canlı yayın ID bulundu (isLiveContent): {match.group(1)}")
                        return match.group(1)
                    
                    # Pattern 2: Canlı badge'i olan videoId
                    match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"liveBadgeRenderer"', html_content)
                    if match:
                        logging.info(f"[extract_live] Canlı yayın ID bulundu (liveBadge): {match.group(1)}")
                        return match.group(1)
                    
                    # Pattern 3: Canlı yayın sayfasındaki isLiveNow
                    match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"isLiveNow":true', html_content)
                    if match:
                        logging.info(f"[extract_live] Canlı yayın ID bulundu (isLiveNow): {match.group(1)}")
                        return match.group(1)
                
                except Exception as url_err:
                    logging.error(f"[extract_live] URL hata: {url_err}")
                    continue
            
            # Hiçbir URL'de canlı yayın bulunamadı
            logging.warning(f"[extract_live] Kanal için aktif canlı yayın bulunamadı: {channel_url}")
            return None
            
        except Exception as e:
            logging.exception("[extract_live] Genel hata")
            return None

    def chat_worker(self, url, platform="YouTube", stop_event=None, message_queue=None):
        """Basit ChatDownloader bağlantısı"""
        
        if stop_event is None:
            stop_event = self.stop_event
        if message_queue is None:
            message_queue = self.msg_queue
            
        # ChatDownloader kontrolü
        if ChatDownloader is None:
            logging.error("ChatDownloader modülü bulunamadı")
            message_queue.put(("SISTEM", "ChatDownloader modülü yok! pip install chat-downloader", time.strftime("%H:%M:%S"), platform))
            return
        
        logging.info(f"YouTube chat başlatılıyor: {url}")
        
        # Ana bağlantı döngüsü
        while not stop_event.is_set():
            try:
                message_queue.put(("__STATUS__", "connection_connecting", "yellow", "Sistem"))
                
                # ChatDownloader oluştur
                downloader = ChatDownloader()
                
                # Basit parametreler
                params = {
                    "timeout": 10,
                    "max_attempts": 1
                }
                
                # Chat bağlantısı kur
                chat = downloader.get_chat(url, **params)
                
                # Başarılı bağlantı
                message_queue.put(("__STATUS__", "connection_connected", "#10b981", "Sistem"))
                message_queue.put(("SISTEM", "YouTube chat bağlandı!", time.strftime("%H:%M:%S"), platform))
                logging.info("YouTube chat bağlantısı başarılı")
                
                # Mesajları al
                for message in chat:
                    if stop_event.is_set():
                        break
                        
                    author = message.get("author", {}).get("name", "Anonim")
                    msg_text = message.get("message", "")
                    
                    if msg_text:
                        time_str = datetime.datetime.now().strftime("%H:%M:%S")
                        message_queue.put((author, msg_text, time_str, platform))
                        
            except Exception as e:
                logging.error(f"Chat hatası: {e}")
                message_queue.put(("SISTEM", f"Bağlantı hatası: {str(e)[:30]}...", time.strftime("%H:%M:%S"), platform))
                message_queue.put(("__STATUS__", "connection_error", "red", "Sistem"))
                
                # 3 saniye bekle ve tekrar dene
                time.sleep(3)

    def safe_append_chat(self, author, message, time_str, platform="YouTube"):
        try:
            if not self.root.winfo_exists():
                return
            self.append_chat(author, message, time_str, platform)
            # HEMEN teklif analizi yap - hiç gecikme yok
            self.parse_offer(author, message, time_str)
        except Exception as e:
            logging.exception("safe_append_chat")

    def append_chat(self, author, message, time_str, platform="YouTube"):
        frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        frame.pack(fill="x", pady=1)
        is_paid = author in self.paid_users
        
        # YouTube platform rengi
        platform_color = "#FF0000"  # YouTube kırmızı
        
        # Platform işaretini göster
        platform_frame = ctk.CTkFrame(frame, width=18, height=18, corner_radius=9, fg_color=platform_color)
        platform_frame.pack(side="left", padx=(2, 2))
        platform_frame.pack_propagate(False)
        
        # Y harfi gösteren platform işareti
        platform_letter = "Y"
            
        ctk.CTkLabel(platform_frame, text=platform_letter, font=ctk.CTkFont(size=9, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Ödeme yapmış kullanıcı ikonu
        if is_paid:
            profile = ctk.CTkFrame(frame, width=28, height=28, corner_radius=14, fg_color=self.colors["secondary"])
            profile.pack(side="left", padx=(3, 10))
            profile.pack_propagate(False)
            ctk.CTkLabel(profile, text=author[0].upper(), font=ctk.CTkFont(size=12, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        text_color = "white" if self.appearance_mode == "dark" else "#1e293b"
        font_weight = "bold" if is_paid else "normal"
        ctk.CTkLabel(frame, text=f"{author}: {message[:100]}{'...' if len(message) > 100 else ''}", anchor="w", justify="left", wraplength=320, font=ctk.CTkFont(size=11, weight=font_weight), text_color=text_color).pack(side="left", fill="x", expand=True, padx=5)
        if not is_paid:
            ctk.CTkButton(frame, text="+", command=lambda a=author: self.add_paid_user(a), width=24, height=20, corner_radius=5, fg_color=self.colors["primary"], font=ctk.CTkFont(size=10, weight="bold")).pack(side="right", padx=5)
        
        # Ultra güçlü otomatik scroll - yüksek yoğunluklu mesajlar için geliştirilmiş
        try:
            # İlk yöntem: Anında scroll
            self.chat_container._parent_canvas.yview_moveto(1.0)
            
            # İkinci yöntem: Tüm widget'ları güncelle ve sonra scroll
            self.chat_container.update_idletasks()
            self.chat_container._parent_canvas.update_idletasks()
            self.chat_container._parent_canvas.yview_moveto(1.0)
            
            # Üçüncü yöntem: 1ms sonra tekrar dene
            self.root.after(1, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
            
            # Dördüncü yöntem: 10ms sonra farklı bir yöntem ile dene
            self.root.after(10, lambda: self.chat_container._parent_canvas.yview("end"))
            
            # Beşinci yöntem: 50ms sonra kaydırma algoritmalarını kombinle
            def force_scroll_1():
                try:
                    widget = self.chat_container._parent_canvas
                    widget.update_idletasks()
                    widget.yview_moveto(1.0)
                    widget.yview("end")
                    widget.update()
                except Exception:
                    pass
            
            # Altıncı yöntem: 100ms sonra daha güçlü bir kaydırma algoritması
            def force_scroll_2():
                try:
                    # Tüm widget'ları güncelle
                    self.chat_container.update()
                    self.chat_container._parent_canvas.update()
                    
                    # Scroll'u en alta getir
                    self.chat_container._parent_canvas.yview_moveto(1.0)
                    
                    # Scroll çubuğunu manuel olarak en alta ayarla
                    scrollbar = self.chat_container._parent_canvas.winfo_children()[1]
                    if hasattr(scrollbar, "set"):
                        scrollbar.set(1.0, 1.0)
                except Exception:
                    pass
            
            # Her ihtimale karşı farklı zamanlarda tekrar dene
            self.root.after(50, force_scroll_1)
            self.root.after(100, force_scroll_2)
            
        except Exception as e:
            logging.error(f"Chat scroll hatası: {e}")

    # ---------- TEKLİF ----------
    def parse_offer(self, author, text, time_str):
        """
        Teklif analiz fonksiyonu - hızlı ve güvenilir
        1. Sadece sayı yazıldığında teklif olarak kabul edilir
        2. Sabit ürün modunda ürün adı yazıldığında teklif olarak kabul edilir
        3. Tüm mesajlar anında işlenir
        4. İşlemler hızlı ve doğru şekilde yapılır
        """
        # ADIM 1: İlk kontrollerimiz - mezat aktif mi, kullanıcı yetkili mi
        if not self.is_mezat_active:
            return
            
        if author not in self.paid_users:
            logging.debug(f"Kullanıcı {author} ödeme yapanlar listesinde değil.")
            return
            
        # ADIM 3: İşlem moduna göre teklif analizi
        mode = self.current_mode
        # DEBUG - analiz edilen mesaj
        logging.debug(f"Teklif analiz ediliyor: {author} -> '{text}' ({mode})")
        
        # ADIM 4: Ürün modu için analiz (ürün adı mesajda geçiyor mu?)
        if mode == "product":
            product_name = self.current_product.lower().strip()
            text_lower = text.lower().strip()
            
            # İlk önce sayısal değer ve çarpan kontrolü yap
            quantity = 1
            quantity_match = None
            
            # x ve * operatörleri için arama yapılıyor
            for pattern in [
                r'(\d+)\s*[xX*]\s*(\d+)',  # 2x3, 2 * 3, 2X3 formatları
                r'[xX*]\s*(\d+)',          # x2, X5, *10 formatları
            ]:
                match = re.search(pattern, text_lower)
                if match:
                    quantity_match = match
                    break
            
            # Eğer x2 veya *5 gibi bir format varsa
            if quantity_match:
                try:
                    # Grup sayısına göre işlem yap
                    if len(quantity_match.groups()) == 2:  # "2x3" formatı
                        # İlk grup sabit fiyattır, ikinci grup adet
                        quantity = int(quantity_match.group(2))
                    else:  # "x2" formatı
                        quantity = int(quantity_match.group(1))
                    
                    # Adet sınırlaması
                    if quantity > 100:
                        quantity = 100
                    
                    # Adet bilgisini mesajdan çıkar
                    text_for_product = re.sub(r'[xX*]\s*\d+', '', text_lower).strip()
                    text_for_product = re.sub(r'\d+\s*[xX*]\s*\d+', '', text_for_product).strip()
                except:
                    quantity = 1
                    text_for_product = text_lower
            else:
                text_for_product = text_lower
            
            # Ürün adı için genişletilmiş eşleşme kontrolü
            # 1. Tam eşleşme (örn: "bıçak" == "bıçak")
            # 2. Mesaj ürün adını içeriyor (örn: "bıçak istiyorum" içinde "bıçak" var)
            # 3. Mesaj sadece ürün adını içeriyor (diğer kelimeler yok)
            # 4. Sadece ürün yazılmış ("ürün", "urun")
            # 5. Ürün adının herhangi bir kelimesi mesajda var
            
            # Eğer ürün adı birden fazla kelimeden oluşuyorsa, her bir kelimesi için ayrı kontrol yap
            product_words = [w for w in product_name.split() if len(w) > 2]  # 2 harften kısa kelimeleri atla
            
            product_match = (
                text_for_product == product_name or  # Tam eşleşme
                product_name in text_for_product or  # Ürün adı mesajın bir parçası
                text_for_product == product_name or  # Tam eşleşme tekrar
                text_for_product == "ürün" or text_for_product == "urun" or  # Genel ürün kelimesi
                # Ürün adının anlamlı kelimeleri mesajda geçiyor mu
                any(word in text_for_product for word in product_words)
            )
            
            # Eğer sayısal bir değer içeriyorsa (örn. "250") ve bu değer hedef fiyata eşitse, ürün eşleşmesine bakılmaksızın kabul et
            numbers = re.findall(r'\d+', text_lower)
            price_match = False
            if numbers:
                for num in numbers:
                    if num == self.current_price:
                        price_match = True
                        break
            
            # Ürün eşleşti veya doğru fiyat yazıldıysa işlem yap
            if product_match or price_match:
                logging.info(f"✅ Sabit ürün eşleşmesi: {author} -> {text} (Adet: {quantity})")
                
                # Stok kontrolü
                if self.current_stock > 0 and (self.sold_count + quantity) > self.current_stock:
                    self.show_notification("Stok Yetersiz", f"{self.current_product} için yeterli stok yok! (Kalan: {self.current_stock - self.sold_count})", "warning")
                    return
                
                # Toplam fiyat hesapla
                total_price = float(self.current_price) * quantity
                
                # Teklif verisi oluştur
                offer_data = {
                    "author": author, 
                    "amount": f"{total_price:.0f}", 
                    "unit_price": self.current_price,
                    "quantity": quantity,
                    "time": time_str, 
                    "text": text, 
                    "product": self.current_product
                }
                
                # Listeye ekle ve anında UI güncelle
                self.offers_list.append(offer_data)
                self.add_offer_row(offer_data)
                self.auto_print_product_offer(offer_data)
                
                # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                self.play_sound_effect(str(sound_index))
                
                # Stok ve teklif sayısını güncelle
                self.sold_count += quantity
                self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                
                return  # İşlem tamamlandı, çık
            
            return  # Ürün modunda eşleşme yoksa burada çık
        
        # ADIM 5: Sabit fiyat modu için sadece sayı kontrolü (en yaygın kullanım)
        if mode == "fixed":
            target_price = int(float(self.current_price))
            text_lower = text.lower().strip()
            
            # Basit sayı eşleşmesi - Çok sık kullanılan durum
            # Sadece "250" yazıldığında hemen kabul et - HIZLI İŞLEM
            simple_match = re.search(r'^\s*(\d+)\s*$', text)  # Başı ve sonu boşluk olabilir, sadece sayı
            if simple_match:
                amount = simple_match.group(1)
                amount_int = int(amount)
                
                # Hedef fiyatla eşleşiyor mu?
                if amount_int == target_price:
                    logging.info(f"✅ Basit fiyat eşleşmesi: {author} -> {amount} TL")
                    
                    # Stok kontrolü
                    if self.current_stock > 0 and self.sold_count >= self.current_stock:
                        self.show_notification("Stok Bitti", f"{self.current_product} stokta kalmadı!", "warning")
                        return
                    
                    # Teklif verisi oluştur (tek adet)
                    offer_data = {
                        "author": author, 
                        "amount": amount, 
                        "unit_price": amount,
                        "quantity": 1,
                        "time": time_str, 
                        "text": text, 
                        "product": self.current_product
                    }
                    
                    # Listeye ekle ve anında UI güncelle - HIZLI YANIT
                    self.offers_list.append(offer_data)
                    self.add_offer_row(offer_data)
                    self.auto_print_fixed_offer(offer_data)
                    
                    # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                    sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                    self.play_sound_effect(str(sound_index))
                    
                    # Stok ve teklif sayısını güncelle
                    self.sold_count += 1
                    self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                    
                    return  # Eşleşme bulundu, hemen çık
            
            # Adet operatörü formatı: "250x2", "250*3", vb.
            quantity_match = re.search(r'(\d+)\s*[xX*]\s*(\d+)', text_lower)
            if quantity_match:
                price_part = quantity_match.group(1)
                quantity_part = quantity_match.group(2)
                
                try:
                    price_int = int(price_part)
                    quantity = int(quantity_part)
                    
                    if quantity > 100:  # Maksimum adet sınırı
                        quantity = 100
                        
                    # Fiyat eşleşmesi
                    if price_int == target_price:
                        logging.info(f"✅ Fiyat+Adet eşleşmesi: {author} -> {price_int} TL x {quantity} adet")
                        
                        # Stok kontrolü
                        if self.current_stock > 0 and (self.sold_count + quantity) > self.current_stock:
                            self.show_notification("Stok Yetersiz", f"{self.current_product} için yeterli stok yok! Kalan: {self.current_stock - self.sold_count}", "warning")
                            return
                        
                        # Toplam fiyat
                        total_price = price_int * quantity
                        
                        # Teklif verisi oluştur
                        offer_data = {
                            "author": author, 
                            "amount": f"{total_price}", 
                            "unit_price": str(price_int),
                            "quantity": quantity,
                            "time": time_str, 
                            "text": text, 
                            "product": self.current_product
                        }
                        
                        # Listeye ekle ve anında UI güncelle
                        self.offers_list.append(offer_data)
                        self.add_offer_row(offer_data)
                        self.auto_print_fixed_offer(offer_data)
                        
                        # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                        sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                        self.play_sound_effect(str(sound_index))
                        
                        # Stok ve teklif sayısını güncelle
                        self.sold_count += quantity
                        self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                        
                        return  # Eşleşme bulundu, çık
                except ValueError:
                    pass  # Sayısal dönüşüm hatası
                
            # Diğer sayısal eşleşmeler için daha esnek kontrol (normal mesajlardaki sayıları yakala)
            numbers = re.findall(r'\d+', text_lower)
            if numbers:
                for num_str in numbers:
                    amount_int = int(num_str)
                    if amount_int == target_price:
                        logging.info(f"✅ Mesaj içinde fiyat eşleşmesi: {author} -> {amount_int} TL")
                        
                        # Stok kontrolü
                        if self.current_stock > 0 and self.sold_count >= self.current_stock:
                            self.show_notification("Stok Bitti", f"{self.current_product} stokta kalmadı!", "warning")
                            return
                        
                        # Teklif verisi oluştur (tek adet)
                        offer_data = {
                            "author": author, 
                            "amount": f"{amount_int}", 
                            "unit_price": f"{amount_int}",
                            "quantity": 1,
                            "time": time_str, 
                            "text": text, 
                            "product": self.current_product
                        }
                        
                        # Listeye ekle ve anında UI güncelle
                        self.offers_list.append(offer_data)
                        self.add_offer_row(offer_data)
                        self.auto_print_fixed_offer(offer_data)
                        
                        # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                        sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                        self.play_sound_effect(str(sound_index))
                        
                        # Stok ve teklif sayısını güncelle
                        self.sold_count += 1
                        self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                        
                        return  # İlk eşleşmeyi bul ve çık
        
        # ADIM 6: En yüksek teklif modu
        elif mode == "highest":
            # Basit sayısal değer arama
            numbers = re.findall(r'\d+', text)
            if numbers:
                # En büyük sayıyı bul (birden fazla sayı varsa)
                max_number = max([int(num) for num in numbers])
                amount = str(max_number)
                
                try:
                    offer_float = float(amount)
                    offer_data = {
                        "author": author, 
                        "amount": amount, 
                        "amount_float": offer_float, 
                        "time": time_str, 
                        "text": text, 
                        "product": self.current_product
                    }
                    
                    # Listeye ekle ve sırala
                    self.offers_list.append(offer_data)
                    self.offers_list.sort(key=lambda x: x.get("amount_float", 0), reverse=True)
                    
                    # UI güncelle
                    self.refresh_offers_table()
                    self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                    
                    # En yüksek teklif bildirimi
                    if self.offers_list and offer_float >= self.offers_list[0].get("amount_float", 0):
                        self.show_notification("En Yüksek Teklif", f"{author}: {amount} TL", "success")
                        
                    # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                    sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                    self.play_sound_effect(str(sound_index))
                    
                    logging.info(f"✅ En yüksek teklif eklendi: {author} -> {amount} TL")
                    return  # İşlem başarılı
                except ValueError:
                    pass  # Sayısal dönüşüm hatası
                
        elif mode == "highest":
                try:
                    offer_float = float(amount)
                    offer_data = {"author": author, "amount": amount, "amount_float": offer_float, "time": time_str, "text": text, "product": self.current_product}
                    self.offers_list.append(offer_data)
                    
                    # En yüksek tekliflere göre sırala
                    self.offers_list.sort(key=lambda x: x.get("amount_float", 0), reverse=True)
                    
                    # HEMEN UI güncelle
                    self.refresh_offers_table()
                    self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
                    
                    # En yüksek teklifi bildirme
                    if self.offers_list and offer_float >= self.offers_list[0].get("amount_float", 0):
                        self.show_notification("En Yüksek Teklif", f"{author}: {amount} TL", "success")
                    
                    # Teklif ses efekti çal - ardışık tekliflerde farklı sesler
                    sound_index = (len(self.offers_list) - 1) % 7 + 1  # 1'den 7'ye dönüşümlü sesler
                    self.play_sound_effect(str(sound_index))
                    
                    logging.info(f"✅ En yüksek teklif eklendi: {author} -> {amount} TL")
                    return  # İlk geçerli sayıyı bul ve çık
                except ValueError:
                    pass

    def add_offer_row(self, data):
        if not self.root.winfo_exists():
            return
        row = ctk.CTkFrame(self.offers_container, fg_color="transparent")
        row.pack(fill="x", pady=1)
        is_highest = self.current_mode == "highest" and len(self.offers_list) > 0 and data.get("amount_float", 0) == self.offers_list[0].get("amount_float", 0)
        text_color = "white" if self.appearance_mode == "dark" else "#1e293b"
        font_weight = "bold" if is_highest else "normal"
        ctk.CTkLabel(row, text=data["author"][:12], width=150, anchor="w", font=ctk.CTkFont(size=10, weight=font_weight), text_color=text_color).pack(side="left", padx=3)
        # Adet bilgisi ile teklif gösterimi
        quantity = data.get("quantity", 1)
        unit_price = data.get("unit_price", data["amount"])
        
        if quantity > 1:
            # Adet varsa: "2x200₺=400₺" formatında göster
            offer_text = f"{quantity}x{unit_price}₺={data['amount']}₺"
        else:
            # Tek adet: "200₺" formatında göster
            offer_text = f"{data['amount']}₺"
            
        ctk.CTkLabel(row, text=offer_text, width=120, anchor="w", font=ctk.CTkFont(size=10, weight=font_weight), text_color=text_color).pack(side="left", padx=3)
        ctk.CTkLabel(row, text=data["time"], width=80, anchor="w", font=ctk.CTkFont(size=10, weight=font_weight), text_color=text_color).pack(side="left", padx=3)
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="🗑️", command=lambda d=data: self.delete_offer(d), width=25, height=18, corner_radius=3, fg_color="#e11d48", font=ctk.CTkFont(size=8)).pack(side="left", padx=1)
        if self.current_mode == "highest":
            ctk.CTkButton(btn_frame, text="🖨️", command=lambda d=data: self.print_single_offer(d), width=25, height=18, corner_radius=3, fg_color=self.colors["primary"], font=ctk.CTkFont(size=8)).pack(side="left", padx=1)
        icon = "🏆" if is_highest else "✔"
        ctk.CTkLabel(btn_frame, text=icon, width=15, anchor="w", text_color=self.colors["secondary"] if is_highest else text_color, font=ctk.CTkFont(size=9, weight=font_weight)).pack(side="left", padx=1)

    def delete_offer(self, data):
        try:
            self.offers_list = [o for o in self.offers_list if not (o["author"] == data["author"] and o["amount"] == data["amount"] and o["time"] == data["time"])]
            self.refresh_offers_table()
            self.offer_count_label.configure(text=f"{len(self.offers_list)} teklif")
        except Exception as e:
            logging.exception("delete_offer")

    def refresh_offers_table(self):
        for w in self.offers_container.winfo_children():
            w.destroy()
        for offer in self.offers_list:
            self.add_offer_row(offer)

    # ---------- PRINT ----------
    def auto_print_product_offer(self, data):
        author = data['author']
        # Kullanıcı detaylarını al
        details = self.paid_user_details.get(author, {})
        fullname = details.get("fullname", "")
        phone = details.get("phone", "")
        address = details.get("address", "")
        
        stock = f"\nStok     : {self.current_stock - self.sold_count}/{self.current_stock}" if self.current_stock > 0 else ""
        
        # Thermal yazıcı için optimize edilmiş format (32 karakter genişlik)
        text = "================================\n"
        text += "       SABİT ÜRÜN SATIŞ        \n"
        text += "================================\n"
        text += f"Ürün     : {data['product'][:22]}\n"
        text += f"Kullanıcı: {author[:22]}\n"
        
        # Adet bilgisi ile fiyat gösterimi
        quantity = data.get("quantity", 1)
        unit_price = data.get("unit_price", data["amount"])
        
        if quantity > 1:
            text += f"Adet     : {quantity} adet\n"
            text += f"Birim    : {unit_price} TL\n"
            text += f"Toplam   : {data['amount']} TL\n"
        else:
            text += f"Fiyat    : {data['amount']} TL\n"
            
        text += f"Zaman    : {data['time']}\n"
        text += f"Tarih    : {datetime.datetime.now().strftime('%d.%m.%Y')}\n"
        
        # Kullanıcı detayları varsa ekle
        if fullname or phone or address:
            text += "--------------------------------\n"
            if fullname:
                text += f"Ad Soyad : {fullname[:22]}\n"
            if phone:
                text += f"Telefon  : {phone}\n"
            if address:
                # Adresi satırlara böl (thermal yazıcı için)
                words = address.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 22:
                        current_line += " " + word if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                text += "Adres    :\n"
                for line in lines[:3]:  # Max 3 satır
                    text += f"  {line}\n"
        
        if stock:
            text += stock + "\n"
        text += "================================\n"
        
        self.direct_print(text)

    def auto_print_fixed_offer(self, data):
        author = data['author']
        # Kullanıcı detaylarını al
        details = self.paid_user_details.get(author, {})
        fullname = details.get("fullname", "")
        phone = details.get("phone", "")
        address = details.get("address", "")
        
        stock = f"\nStok     : {self.current_stock - self.sold_count}/{self.current_stock}" if self.current_stock > 0 else ""
        
        # Thermal yazıcı için optimize edilmiş format (32 karakter genişlik)
        text = "================================\n"
        text += "       SABİT FİYAT SATIŞ       \n"
        text += "================================\n"
        text += f"Ürün     : {data['product'][:22]}\n"
        text += f"Kullanıcı: {author[:22]}\n"
        
        # Adet bilgisi ile fiyat gösterimi
        quantity = data.get("quantity", 1)
        unit_price = data.get("unit_price", data["amount"])
        
        if quantity > 1:
            text += f"Adet     : {quantity} adet\n"
            text += f"Birim    : {unit_price} TL\n"
            text += f"Toplam   : {data['amount']} TL\n"
        else:
            text += f"Teklif   : {data['amount']} TL\n"
            
        text += f"Hedef    : {self.current_price} TL\n"
        text += f"Zaman    : {data['time']}\n"
        text += f"Tarih    : {datetime.datetime.now().strftime('%d.%m.%Y')}\n"
        
        # Kullanıcı detayları varsa ekle
        if fullname or phone or address:
            text += "--------------------------------\n"
            if fullname:
                text += f"Ad Soyad : {fullname[:22]}\n"
            if phone:
                text += f"Telefon  : {phone}\n"
            if address:
                # Adresi satırlara böl (thermal yazıcı için)
                words = address.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 22:
                        current_line += " " + word if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                text += "Adres    :\n"
                for line in lines[:3]:  # Max 3 satır
                    text += f"  {line}\n"
        
        if stock:
            text += stock + "\n"
        text += "================================\n"
        
        self.direct_print(text)

    def print_single_offer(self, data):
        author = data['author']
        # Kullanıcı detaylarını al
        details = self.paid_user_details.get(author, {})
        fullname = details.get("fullname", "")
        phone = details.get("phone", "")
        address = details.get("address", "")
        
        text = f"""=====================================
           TEKLİF FİŞİ
=====================================
Ürün     : {data.get('product', 'Ürün')}
Kullanıcı: {author[:20]}
Teklif   : {data['amount']} TL
Zaman    : {data['time']}
Tarih    : {datetime.datetime.now().strftime('%d.%m.%Y')}"""
        
        # Eğer kullanıcı detayları varsa ekle
        if fullname or phone or address:
            text += "\n-------------------------------------"
            if fullname:
                text += f"\nAd Soyad : {fullname}"
            if phone:
                text += f"\nTelefon  : {phone}"
            if address:
                formatted_address = address.replace("\n", " ")
                text += f"\nAdres    : {formatted_address}"
                
        text += "\n=====================================\n"
        self.direct_print(text)

    def print_highest_offer(self, data):
        author = data['author']
        # Kullanıcı detaylarını al
        details = self.paid_user_details.get(author, {})
        fullname = details.get("fullname", "")
        phone = details.get("phone", "")
        address = details.get("address", "")
        
        text = f"""=====================================
       EN YÜKSEK TEKLİF FİŞİ
=====================================
Ürün     : {data.get('product', 'Ürün')}
Kullanıcı: {author[:20]}
Teklif   : {data['amount']} TL
Zaman    : {data['time']}
Tarih    : {datetime.datetime.now().strftime('%d.%m.%Y')}"""
        
        # Eğer kullanıcı detayları varsa ekle
        if fullname or phone or address:
            text += "\n-------------------------------------"
            if fullname:
                text += f"\nAd Soyad : {fullname}"
            if phone:
                text += f"\nTelefon  : {phone}"
            if address:
                formatted_address = address.replace("\n", " ")
                text += f"\nAdres    : {formatted_address}"
                
        text += "\n=====================================\n"
        self.direct_print(text)

    def print_all_offers(self):
        if not self.offers_list:
            self.show_notification("Uyarı", "Yazdırılacak teklif yok!", "warning")
            return
        
        if self.current_mode == "highest":
            # En yüksek teklif için sadece en yüksek teklifi yazdır
            highest_offer = self.offers_list[0] if self.offers_list else None
            if highest_offer:
                self.print_highest_offer(highest_offer)
                return
                
        text = f"""=====================================
         MEZAT TEKLİF LİSTESİ
=====================================
"""
        
        # Ödeme yapanlar için ilave bilgiler
        for i, offer in enumerate(self.offers_list, 1):
            author = offer['author']
            # Kullanıcı detaylarını kontrol et
            details = self.paid_user_details.get(author, {})
            fullname = details.get("fullname", "")
            phone = details.get("phone", "")
            address = details.get("address", "")
            
            # Temel teklif bilgisi
            text += f"""{i}. {author[:15]} - {offer['amount']} TL
   Zaman: {offer['time']}"""
            
            # Eğer kullanıcı detayları varsa ekle
            if fullname or phone or address:
                text += "\n   ----------------------"
                if fullname:
                    text += f"\n   Ad Soyad: {fullname}"
                if phone:
                    text += f"\n   Telefon: {phone}"
                if address:
                    formatted_address = address.replace("\n", " ")
                    text += f"\n   Adres: {formatted_address}"
            
            text += "\n-------------------------------------\n"
            
        text += f"""=====================================
TOPLAM: {len(self.offers_list)} TEKLİF
TARİH: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}
=====================================
"""
        self.direct_print(text)

    def direct_print(self, text):
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(text)
                path = f.name
            os.startfile(path, "print")
            self.root.after(30000, lambda: os.unlink(path))
            self.show_notification("Yazdırıldı", "Fiş yazdırıcıya gönderildi", "success")
        except Exception as e:
            logging.exception("direct_print")
            self.show_notification("Yazdırma Hatası", str(e), "error")

    # ---------- PAID USERS ----------
    def add_paid_user(self, name=None):
        if name is None:
            name = simpledialog.askstring("Kullanıcı Ekle", "YouTube adı:")
        if name and name.strip() and name not in self.paid_users:
            self.paid_users.append(name)
            self.paid_listbox.insert("end", f"• {name}\n")
            self.paid_count_label.configure(text=f"{len(self.paid_users)} kullanıcı")
            self.show_notification("Eklendi", f"{name} listeye eklendi", "success")

    def show_manage_paid_users(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Ödeme Yapanlar Yönetimi")
        popup.geometry("850x600")  # Daha büyük pencere
        popup.configure(fg_color=self.colors["darker"])
        popup.grab_set()
        
        # Başlık
        ctk.CTkLabel(popup, text="👥 Ödeme Yapanlar Yönetimi", 
                    font=ctk.CTkFont(size=22, weight="bold"), 
                    text_color=self.colors["light"]).pack(pady=20)
        
        # Kullanıcı listesi ve detay paneli
        main_frame = ctk.CTkFrame(popup, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sol panel - Kullanıcı listesi
        left_panel = ctk.CTkFrame(main_frame, fg_color=self.colors["dark"], corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Listbox başlığı
        ctk.CTkLabel(left_panel, text="📋 Kullanıcılar", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(pady=10)
        
        # Listbox
        listbox_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar ekle
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Daha büyük listbox
        listbox = tk.Listbox(listbox_frame, 
                            bg=self.colors["dark"], 
                            fg=self.colors["light"],
                            selectbackground=self.colors["primary"], 
                            font=("Arial", 14),  # Daha büyük font 
                            height=20,          # Daha yüksek liste
                            yscrollcommand=scrollbar.set)
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Kullanıcıları ekle
        for user in self.paid_users:
            listbox.insert("end", user)
            # Varsayılan olarak boş detaylar
            if user not in self.paid_user_details:
                self.paid_user_details[user] = {
                    "phone": "",
                    "fullname": "",
                    "address": ""
                }
        
        # Sağ panel - Kullanıcı detayları
        right_panel = ctk.CTkFrame(main_frame, fg_color=self.colors["dark"], corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Detay başlığı
        ctk.CTkLabel(right_panel, text="📝 Kullanıcı Detayları", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(pady=10)
        
        # Detay form - daha geniş alanlar
        form_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Kullanıcı adı
        ctk.CTkLabel(form_frame, text="YouTube Kullanıcı Adı:", 
                    anchor="w", 
                    text_color=self.colors["light"],
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(15, 5))
                    
        username_entry = ctk.CTkEntry(form_frame, 
                                   height=40, 
                                   corner_radius=10,
                                   font=ctk.CTkFont(size=14))
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Ad Soyad
        ctk.CTkLabel(form_frame, text="Ad Soyad:", 
                    anchor="w", 
                    text_color=self.colors["light"],
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(15, 5))
                    
        fullname_entry = ctk.CTkEntry(form_frame, 
                                    height=40, 
                                    corner_radius=10,
                                    font=ctk.CTkFont(size=14))
        fullname_entry.pack(fill="x", pady=(0, 15))
        
        # Telefon
        ctk.CTkLabel(form_frame, text="Telefon:", 
                    anchor="w", 
                    text_color=self.colors["light"],
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(15, 5))
                    
        phone_entry = ctk.CTkEntry(form_frame, 
                                 height=40, 
                                 corner_radius=10,
                                 font=ctk.CTkFont(size=14))
        phone_entry.pack(fill="x", pady=(0, 15))
        
        # Adres
        ctk.CTkLabel(form_frame, text="Adres:", 
                    anchor="w", 
                    text_color=self.colors["light"],
                    font=ctk.CTkFont(size=14)).pack(fill="x", pady=(15, 5))
                    
        address_entry = ctk.CTkTextbox(form_frame, 
                                     height=120, 
                                     corner_radius=10,
                                     font=ctk.CTkFont(size=14))
        address_entry.pack(fill="x", pady=(0, 15))
        
        # Detay butonları
        detail_btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        detail_btn_frame.pack(fill="x", pady=15)
        
        # Kaydet butonu - daha büyük ve belirgin
        save_detail_btn = ctk.CTkButton(detail_btn_frame, 
                                      text="💾 Kaydet", 
                                      fg_color=self.colors["secondary"],
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      height=45,
                                      corner_radius=10,
                                      command=lambda: self.save_user_details(
                                          username_entry.get(),
                                          fullname_entry.get(),
                                          phone_entry.get(),
                                          address_entry.get("1.0", "end-1c")
                                      ))
        save_detail_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # ÜST buton çerçevesi - başlığın hemen altında
        top_btn_frame = ctk.CTkFrame(popup, fg_color="transparent", height=50)
        top_btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        top_btn_frame.pack_propagate(False)
        
        # Üst butonlar - yan yana
        ctk.CTkButton(top_btn_frame, 
                     text="➕ Ekle", 
                     command=lambda: self.popup_add_user(listbox), 
                     width=120,
                     height=40,
                     corner_radius=10,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="#28a745", hover_color="#218838").pack(side="left", padx=5)
                     
        ctk.CTkButton(top_btn_frame, 
                     text="➖ Sil", 
                     command=lambda: self.popup_remove_user(listbox), 
                     width=120,
                     height=40,
                     corner_radius=10,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="#dc3545", hover_color="#c82333").pack(side="left", padx=5)
                     
        ctk.CTkButton(top_btn_frame, 
                     text="📤 Dışa Aktar", 
                     command=self.export_paid_users, 
                     width=130,
                     height=40,
                     corner_radius=10,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="#17a2b8", hover_color="#138496").pack(side="left", padx=5)
                     
        ctk.CTkButton(top_btn_frame, 
                     text="📥 İçe Aktar", 
                     command=self.import_paid_users, 
                     width=130,
                     height=40,
                     corner_radius=10,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="#ffc107", hover_color="#e0a800",
                     text_color="black").pack(side="left", padx=5)
                     
        # ALT buton çerçevesi - Kaydet ve Kapat
        bottom_btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        bottom_btn_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        # Kaydet butonu (sol tarafta)
        save_btn = ctk.CTkButton(bottom_btn_frame, 
                               text="💾 Kaydet", 
                               width=200,
                               height=45,
                               corner_radius=15,
                               font=ctk.CTkFont(size=16, weight="bold"),
                               fg_color="#007bff", hover_color="#0056b3")
        save_btn.pack(side="left")
        
        # Kapat butonu (sağ tarafta)
        ctk.CTkButton(bottom_btn_frame, 
                     text="❌ Kapat", 
                     command=popup.destroy, 
                     width=150,
                     height=45,
                     corner_radius=15,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     fg_color="#6c757d", hover_color="#545b62").pack(side="right")
        
        # Listbox seçim olayı - geliştirilmiş kullanıcı detay yükleme
        def on_select(event):
            try:
                index = listbox.curselection()[0]
                selected_user = listbox.get(index)
                
                # Formu doldur
                username_entry.delete(0, "end")
                username_entry.insert(0, selected_user)
                
                # Kullanıcı detaylarını yükle
                details = self.paid_user_details.get(selected_user, {"phone": "", "fullname": "", "address": ""})
                
                fullname_entry.delete(0, "end")
                fullname_entry.insert(0, details.get("fullname", ""))
                
                phone_entry.delete(0, "end")
                phone_entry.insert(0, details.get("phone", ""))
                
                address_entry.delete("1.0", "end")
                address_entry.insert("1.0", details.get("address", ""))
                
                # Seçilen kullanıcıyı vurgula
                username_entry.configure(border_color=self.colors["secondary"], border_width=2)
                save_detail_btn.configure(text=f"💾 {selected_user} için Kaydet")
                
            except (IndexError, TypeError):
                pass
        
        # Çift tıklama olayı ekle - aynı işi yapacak
        def on_double_click(event):
            on_select(event)
        
        listbox.bind("<<ListboxSelect>>", on_select)
        listbox.bind("<Double-Button-1>", on_double_click)

    def popup_add_user(self, listbox):
        name = simpledialog.askstring("Kullanıcı Ekle", "YouTube adı:")
        if name and name.strip() and name not in self.paid_users:
            self.paid_users.append(name)
            listbox.insert("end", name)
            self.refresh_paid_users_list()

    def popup_remove_user(self, listbox):
        selection = listbox.curselection()
        if selection:
            user = listbox.get(selection[0])
            # Kullanıcıyı hem listeden hem de detaylardan sil
            if user in self.paid_users:
                self.paid_users.remove(user)
            if user in self.paid_user_details:
                del self.paid_user_details[user]
            
            listbox.delete(selection[0])
            self.refresh_paid_users_list()
            
            # Dosyaya kaydet
            self.save_user_details_to_file()
            
            logging.info(f"Kullanıcı silindi: {user}")
            self.show_notification("Silindi", f"{user} kullanıcısı silindi", "info")

    def save_user_details(self, username, fullname, phone, address):
        """Kullanıcı detaylarını kaydet"""
        if not username or username not in self.paid_users:
            self.show_notification("Hata", "Geçerli bir kullanıcı seçin!", "error")
            return
            
        # Kullanıcı detaylarını güncelle
        self.paid_user_details[username] = {
            "fullname": fullname,
            "phone": phone,
            "address": address
        }
        
        # Detayları dosyaya kaydet
        self.save_user_details_to_file()
        
        self.show_notification("Başarılı", f"{username} için bilgiler kaydedildi", "success")
    
    def save_user_details_to_file(self):
        """Tüm kullanıcı detaylarını dosyaya kaydet"""
        try:
            data = {
                "users": self.paid_users,
                "details": self.paid_user_details
            }
            with open("paid_users.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.exception("save_user_details_to_file")
            self.show_notification("Hata", f"Kullanıcı bilgileri kaydedilemedi: {str(e)}", "error")
    
    def load_user_details_from_file(self):
        """Kullanıcı detaylarını dosyadan yükle"""
        try:
            if os.path.exists("paid_users.json"):
                with open("paid_users.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.paid_users = data.get("users", [])
                    self.paid_user_details = data.get("details", {})
                    self.refresh_paid_users_list()
        except Exception as e:
            logging.exception("load_user_details_from_file")
    
    def import_paid_users(self):
        """Kullanıcıları JSON dosyasından içe aktar"""
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Basit liste formatı mı yoksa tam detay formatı mı?
            if isinstance(data, list):
                # Sadece kullanıcı adları listesi
                for user in data:
                    if user not in self.paid_users:
                        self.paid_users.append(user)
                        # Varsayılan boş detaylar
                        self.paid_user_details[user] = {"phone": "", "fullname": "", "address": ""}
            else:
                # Tam detay formatı
                if "users" in data and "details" in data:
                    # Mevcut kullanıcıları ve detayları güncelle
                    for user in data["users"]:
                        if user not in self.paid_users:
                            self.paid_users.append(user)
                    
                    # Detayları güncelle
                    for user, details in data["details"].items():
                        self.paid_user_details[user] = details
            
            # Arayüzü güncelle
            self.refresh_paid_users_list()
            self.save_user_details_to_file()
            self.show_notification("Başarılı", f"{len(data['users'] if isinstance(data, dict) else data)} kullanıcı içe aktarıldı", "success")
            
        except Exception as e:
            logging.exception("import_paid_users")
            self.show_notification("Hata", f"İçe aktarma başarısız: {str(e)}", "error")

    def export_paid_users(self):
        """Kullanıcıları JSON dosyasına dışa aktar"""
        if not self.paid_users:
            self.show_notification("Uyarı", "Dışa aktarılacak kullanıcı yok!", "warning")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
            
        try:
            # Tam detay formatında dışa aktar
            data = {
                "users": self.paid_users,
                "details": self.paid_user_details
            }
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.show_notification("Başarılı", f"Kullanıcılar {path} dosyasına kaydedildi", "success")
        except Exception as e:
            logging.exception("export_paid_users")
            self.show_notification("Hata", f"Dışa aktarma başarısız: {str(e)}", "error")

    def refresh_paid_users_list(self):
        try:
            if hasattr(self, 'paid_listbox') and self.paid_listbox:
                self.paid_listbox.delete("1.0", "end")
                for user in self.paid_users:
                    self.paid_listbox.insert("end", f"• {user}\n")
            if hasattr(self, 'paid_count_label') and self.paid_count_label:
                self.paid_count_label.configure(text=f"{len(self.paid_users)} kullanıcı")
        except Exception as e:
            logging.exception("refresh_paid_users_list error: %s", str(e))

    # ---------- SETTINGS ----------
    def show_settings(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title(self.translate("settings_title"))
        popup.geometry("600x650")  # Genişletilmiş pencere boyutu
        popup.configure(fg_color=self.colors["darker"])
        popup.grab_set()
        
        # Başlık
        ctk.CTkLabel(popup, text="⚙️ " + self.translate("settings_title"), 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=self.colors["light"]).pack(pady=20)
        
        # Ana ayarlar çerçevesi
        frame = ctk.CTkScrollableFrame(popup, fg_color=self.colors["card"], corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Görünüm ayarları
        appearance_section = ctk.CTkFrame(frame, fg_color="transparent")
        appearance_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(appearance_section, 
                    text=self.translate("appearance"), 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        appearance_var = tk.StringVar(value=self.appearance_mode)
        
        appearance_options = ctk.CTkFrame(appearance_section, fg_color="transparent")
        appearance_options.pack(fill="x", padx=20)
        
        ctk.CTkRadioButton(appearance_options, 
                          text=self.translate("dark_mode"), 
                          variable=appearance_var, 
                          value="dark", 
                          text_color=self.colors["light"]).pack(anchor="w", pady=5)
        
        ctk.CTkRadioButton(appearance_options, 
                          text=self.translate("light_mode"), 
                          variable=appearance_var, 
                          value="light", 
                          text_color=self.colors["light"]).pack(anchor="w", pady=5)
        
        # Dil ayarları
        language_section = ctk.CTkFrame(frame, fg_color="transparent")
        language_section.pack(fill="x", pady=20)
        
        ctk.CTkLabel(language_section, 
                    text=self.translate("language"), 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        language_var = tk.StringVar(value=self.language)
        
        language_options = ctk.CTkFrame(language_section, fg_color="transparent")
        language_options.pack(fill="x", padx=20)
        
        langs = [
            ("🇹🇷 Türkçe", "tr"), 
            ("🇬🇧 English", "en"), 
            ("🇩🇪 Deutsch", "de"), 
            ("🇫🇷 Français", "fr"), 
            ("🇪🇸 Español", "es"), 
            ("🇮🇹 Italiano", "it"), 
            ("🇷🇺 Русский", "ru"), 
            ("🇸🇦 العربية", "ar"), 
            ("🇨🇳 中文", "zh")
        ]
        
        # Dil seçeneklerini iki sütunda göster
        for i, (label, code) in enumerate(langs):
            row = i // 2
            col = i % 2
            
            option_frame = ctk.CTkFrame(language_options, fg_color="transparent")
            option_frame.grid(row=row, column=col, sticky="w", pady=5, padx=10)
            
            ctk.CTkRadioButton(option_frame, 
                              text=label, 
                              variable=language_var, 
                              value=code, 
                              text_color=self.colors["light"]).pack(anchor="w")
        
        # Ses Ayarları
        sound_section = ctk.CTkFrame(frame, fg_color="transparent")
        sound_section.pack(fill="x", pady=20)
        
        ctk.CTkLabel(sound_section, 
                    text="Ses Ayarları", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        # Ses ayarları için seçenekler
        sound_options = ctk.CTkFrame(sound_section, fg_color="transparent")
        sound_options.pack(fill="x", padx=20)
        
        # Açma/kapama düğmesi
        sounds_var = tk.BooleanVar(value=self.sounds_enabled)
        ctk.CTkSwitch(sound_options, 
                     text="Ses Efektlerini Etkinleştir", 
                     variable=sounds_var,
                     onvalue=True,
                     offvalue=False,
                     switch_width=50,
                     progress_color=self.colors["secondary"],
                     text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        # Ses teması seçimi
        theme_frame = ctk.CTkFrame(sound_section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(theme_frame, 
                    text="Ses Teması:", 
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["light"]).pack(side="left", padx=(0, 10))
                    
        sound_theme_var = tk.StringVar(value=self.sound_theme)
        
        # Fight teması seçeneği
        fight_btn = ctk.CTkRadioButton(theme_frame, 
                                      text="Fight",
                                      font=ctk.CTkFont(size=14), 
                                      variable=sound_theme_var, 
                                      value="fight",
                                      text_color=self.colors["light"])
        fight_btn.pack(side="left", padx=(0, 20))
        
        # Money teması seçeneği
        money_btn = ctk.CTkRadioButton(theme_frame, 
                                      text="Money",
                                      font=ctk.CTkFont(size=14), 
                                      variable=sound_theme_var, 
                                      value="money",
                                      text_color=self.colors["light"])
        money_btn.pack(side="left")
        
        # Diğer ayarlar (gelecekte eklenebilir)
        other_section = ctk.CTkFrame(frame, fg_color="transparent")
        other_section.pack(fill="x", pady=20)
        
        ctk.CTkLabel(other_section, 
                    text="Diğer Ayarlar", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=self.colors["light"]).pack(anchor="w", pady=10)
        
        # Buton çerçevesi (sabit alt kısımda)
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent", height=60)
        btn_frame.pack(fill="x", padx=20, pady=20)
        btn_frame.pack_propagate(False)  # Sabit yükseklik
        
        # Kaydet ve İptal butonları
        ctk.CTkButton(btn_frame, 
                     text=self.translate("save"), 
                     command=lambda: self.apply_settings(
                         popup, 
                         appearance_var.get(), 
                         language_var.get(), 
                         sounds_var.get(),
                         sound_theme_var.get()
                     ), 
                     fg_color=self.colors["secondary"],
                     height=40,
                     corner_radius=10).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(btn_frame, 
                     text=self.translate("cancel"), 
                     command=popup.destroy, 
                     fg_color=self.colors["gray"],
                     height=40,
                     corner_radius=10).pack(side="left", fill="x", expand=True)

    def apply_settings(self, popup, appearance, language, sounds_enabled=True, sound_theme=None):
        self.appearance_mode = appearance
        self.language = language
        self.sounds_enabled = sounds_enabled
        
        # Ses teması değiştiyse güncelle
        if sound_theme is not None:
            self.sound_theme = sound_theme
            
        self.save_settings()
        ctk.set_appearance_mode(appearance)
        self.colors = DARK if appearance == "dark" else LIGHT
        self.update_ui_colors()
        self.update_ui_texts()
        popup.destroy()
        self.show_notification(self.translate("settings_saved"), self.translate("settings_saved_message"), "success")

    def update_ui_colors(self):
        self.root.configure(fg_color=self.colors["darker"])
        self.update_widget_colors_recursive(self.root)

    def update_widget_colors_recursive(self, parent):
        for w in parent.winfo_children():
            if isinstance(w, ctk.CTkFrame) and w.cget("fg_color") != "transparent":
                w.configure(fg_color=self.colors["card"])
            self.update_widget_colors_recursive(w)

    def update_ui_texts(self):
        self.root.title(self.translate("app_title"))
        self.connection_status.configure(text=self.translate("connection_none"))
        self.live_indicator.configure(text=self.translate("live"))
        self.offer_count_label.configure(text=self.translate("offers_count", 0))
        self.paid_count_label.configure(text=self.translate("paid_users_count", 0))
        self.status_label.configure(text=self.translate("ready"))
        self.mezat_status_label.configure(text=self.translate("mezat_status", self.translate("passive")))
        self.stream_start_btn.configure(text="▶️ " + self.translate("start_chat"))
        self.stream_stop_btn.configure(text="⏹️ " + self.translate("stop_chat"))
        self.start_button.configure(text="▶️ " + self.translate("start"))
        self.stop_button.configure(text="⏹️ " + self.translate("stop"))
        if self.print_all_btn is not None:
            self.print_all_btn.configure(text="🖨️ " + self.translate("print"))

    # ---------- MISC ----------
    def safe_after(self, ms, func, *args):
        """Pencere yoksa çağrıyı iptal et, hata oluşmasın."""
        try:
            if self.root.winfo_exists():
                # Function wrap to prevent callbacks from being called after object is destroyed
                def safe_wrapper():
                    try:
                        if self.root.winfo_exists():
                            func(*args)
                    except Exception as e:
                        logging.exception(f"Error in safe_after callback: {e}")
                
                return self.root.after(ms, safe_wrapper)
        except Exception:
            pass
        return None

    def setup_keyboard_blocking(self):
        def block(event):
            if (event.state == 8 and event.keysym == "F4") or (event.state == 4 and event.keysym in ("w", "q", "p")):
                return "break"
        self.root.bind_all("<Key>", block)

    def start_health_check(self):
        def check():
            try:
                if not self.root.winfo_exists():
                    return
                
                # YouTube thread sağlık kontrolü
                self.check_platform_health("YouTube")
                
                # Geriye uyumluluk için (eski thread kontrolü)
                if self.chat_thread and not self.chat_thread.is_alive() and self.last_url:
                    logging.warning("Ana chat thread ölmüş, yeniden başlatılıyor")
                    self.chat_thread = threading.Thread(target=self.chat_worker, args=(self.last_url,), daemon=True, name="ChatWorker-Auto")
                    self.chat_thread.start()
                
            except Exception as e:
                logging.exception("health_check error")
            
            # Her 15 saniyede bir kontrol et
            self.health_check_job = self.safe_after(15000, check)
        
        # İlk kontrolü başlat
        self.health_check_job = self.safe_after(15000, check)
        
    def check_platform_health(self, platform):
        """
        YouTube thread'inin sağlık kontrolünü yapar.
        """
        thread = self.youtube_chat_thread
        url = self.youtube_last_url
        stop_event = self.youtube_stop_event
        msg_queue = self.youtube_msg_queue
        
        # Thread çökmüş mü kontrol et
        if thread and not thread.is_alive() and url:
            logging.warning("YouTube thread ölmüş, yeniden başlatılıyor")
            
            # Yeni thread başlat
            self.youtube_chat_thread = threading.Thread(target=self.chat_worker, 
                                                   args=(url, platform, stop_event, msg_queue), 
                                                   daemon=True, 
                                                   name="YouTubeChatWorker-Auto")
            self.youtube_chat_thread.start()
                
            # Durum mesajı gönder
            msg_queue.put(("__STATUS__", "connection_connecting", "yellow", platform))
            
            # Geriye uyumluluk
            self.chat_thread = self.youtube_chat_thread
            self.last_url = url

    def start_message_processor(self):
        """
        Ana thread'de çalışacak güvenli bir mesaj işleyici başlatır.
        Bu fonksiyon YouTube'dan gelen chat mesajlarını alıp UI'a güvenli bir şekilde ekler.
        """
        # Eğer zaten çalışıyorsa tekrar başlatmayalım
        if self.queue_processor_active:
            return
            
        self.queue_processor_active = True
        
        def process_messages():
            # Eğer kapat komutu verilmişse, mesaj işlemeyi durdur
            if not self.root.winfo_exists() or self.stop_threads.is_set():
                self.queue_processor_active = False
                return
            
            # YouTube mesaj kuyruğunu işle
            self.process_platform_queue(self.youtube_msg_queue, "YouTube")
            
            # Geriye uyumluluk için varsayılan kuyruğu da kontrol et
            self.process_platform_queue(self.msg_queue, "YouTube")
            
            # 1ms sonra tekrar kontrol et (maksimum hız)
            self.message_processor_job = self.safe_after(1, process_messages)
            
        # İlk çalıştırma
        self.message_processor_job = self.safe_after(1, process_messages)
        
    def process_platform_queue(self, queue, default_platform="YouTube"):
        """
        Belirli bir platformun mesaj kuyruğundaki mesajları işler.
        """
        messages_processed = 0
        while not queue.empty() and messages_processed < 500:  # En fazla 500 mesaj işle
            try:
                # Platform bilgisi içeren 4 elemanlı mesajlar için kontrol
                message_data = queue.get_nowait()
                
                # Mesaj formatını belirle (3 elemanlı eski mesajlar, 4 elemanlı yeni mesajlar)
                if len(message_data) == 4:
                    author, text, time_str, platform = message_data
                else:
                    author, text, time_str = message_data
                    platform = default_platform  # Varsayılan platform
                    
                # Özel durum mesajları
                if author == "__STATUS__":
                    self.process_status_message(text, time_str, platform)
                # Normal chat mesajları - çift mesajları filtrele
                else:
                    # Mesaj için benzersiz bir hash oluştur
                    message_hash = f"{platform}:{author}:{text}"
                        
                    # Bu mesaj daha önce işlenmedi ise ekle
                    if message_hash not in self.processed_message_cache:
                        self.processed_message_cache.add(message_hash)
                        
                        # Eğer bu bir sistem mesajı ise (mezat durdurma mesajı)
                        # ya da mezat başladıktan sonra gelen bir mesaj ise işle
                        current_time = time.mktime(datetime.datetime.strptime(time_str, "%H:%M:%S").replace(
                            year=datetime.datetime.now().year,
                            month=datetime.datetime.now().month,
                            day=datetime.datetime.now().day
                        ).timetuple())
                        
                        # Mezat başladıktan sonra gelen mesaj veya sistem mesajı ise işle
                        if author == "SISTEM" or current_time >= self.mezat_start_time:
                            self.safe_append_chat(author, text, time_str, platform)
                        
                messages_processed += 1
                    
            except Exception as e:
                if str(e).startswith("empty"):
                    # Queue boş
                    break
                logging.exception(f"Mesaj işleme hatası ({default_platform}): {e}")
                
    def process_status_message(self, text, color, platform):
        """
        Durum mesajlarını işler ve ilgili platform için UI'ı günceller.
        """
        # Durum mesajı içeriğini oluştur
        if text == "connection_connecting":
            status_text = "Bağlanıyor..."
            status_color = "yellow"
        elif text == "connection_connected":
            status_text = "Bağlandı"
            status_color = "#10b981"  # Yeşil
        elif text == "connection_error_yayın_bitti":
            status_text = "Yayın Bitti"
            status_color = "red"
        elif text == "connection_error_bağlantı_hatası":
            status_text = "Bağlantı Hatası"
            status_color = "red"
        elif text.startswith("connection_error_"):
            retry = text.split("_")[-1]
            status_text = f"Bağlantı Hatası ({retry}/20)"
            status_color = "red"
            
        # Bağlantı durumu izleyicisine mesajı ilet
        if hasattr(self, "connection_monitor") and self.connection_monitor:
            self.connection_monitor.process_message(("__STATUS__", text, color, platform))
        elif text == "connection_lost":
            status_text = "Bağlantı Kaybedildi"
            status_color = "red"
        else:
            status_text = text
            status_color = color
            
        # YouTube durumu güncelleme
        if platform == "YouTube":
            if text == "connection_connecting":
                self.youtube_start_btn.configure(state="disabled")
                self.youtube_stop_btn.configure(state="normal")
            elif text == "connection_connected":
                self.youtube_connected = True
                self.youtube_start_btn.configure(state="disabled")
                self.youtube_stop_btn.configure(state="normal")
            elif text.startswith("connection_error_") or text == "connection_lost":
                self.youtube_connected = False
                self.youtube_start_btn.configure(state="normal")
                self.youtube_stop_btn.configure(state="disabled")
                
            # YouTube status etiketini güncelle
            self.youtube_status.configure(text=f"{status_text}", text_color=status_color)
            
        # Durum mesajını logla
        logging.info(f"Durum güncellendi ({platform}): {status_text}")

    def on_closing(self):
        if messagebox.askyesno("Kapatma", "Programı kapatmak istiyor musunuz?"):
            try:
                # YouTube thread'in durmasını iste
                self.youtube_stop_event.set()
                self.stop_event.set()
                self.stop_threads.set()
                
                # CustomTkinter tarafından oluşturulan tüm update/check işlerini durdur
                # Uygulama kapatılırken bu after job'ları sorun çıkarıyor
                try:
                    for widget in [self.root] + list(self.root.winfo_children()):
                        widget_str = str(widget)
                        if hasattr(widget, "_check_dpi_scaling"):
                            widget._check_dpi_scaling = lambda *args: None
                        if hasattr(widget, "_update"):
                            widget._update = lambda *args: None
                except:
                    pass
                
                # Tüm after job'larını iptal et (bizim oluşturduğumuz)
                for job in ['poll_job', 'status_job', 'reconnect_job', 'timer_job', 
                        'health_check_job', 'message_processor_job']:
                    if hasattr(self, job) and getattr(self, job):
                        try:
                            self.root.after_cancel(getattr(self, job))
                        except:
                            pass
                
                # Tüm aktif job'ları iptal et (toplu silme)
                try:
                    all_jobs = self.root.tk.call('after', 'info')
                    if all_jobs:
                        for job_id in all_jobs:
                            try:
                                self.root.after_cancel(job_id)
                            except:
                                pass
                except:
                    pass
                
                # Thread'leri temizle
                self.cleanup_threads()
                
                # Pencereyi kapat
                try:
                    self.root.quit()
                    self.root.destroy()
                except:
                    pass
                
                # Yine de kapanmadıysa zorla çık
                import os
                os._exit(0)
            
            except Exception as e:
                logging.critical(f"Kapanma hatası: {e}")
                # Çıkış yapmaya çalış
                try:
                    import os
                    os._exit(0)
                except:
                    pass

    def _setup_global_exception_handler(self):
        """
        Beklenmeyen hataları ele almak için bir küresel hata yakalayıcı ayarla
        """
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # KeyboardInterrupt'ları yok say
                return
            
            # Hatayı logla
            logging.error("Yakalanmamış bir istisna oluştu:", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Program hala çalışıyorsa kullanıcıya bildir
            try:
                if hasattr(self, 'root') and self.root.winfo_exists():
                    messagebox.showerror("Beklenmeyen Hata", 
                                        f"Bir hata oluştu ancak program çalışmaya devam ediyor:\n\n{exc_type.__name__}: {exc_value}")
            except:
                pass
        
        # Varsayılan istisnai durum işleyicisini kaydet
        self._default_exception_handler = sys.excepthook
        # Kendi istisnai durum işleyicimizi kur
        sys.excepthook = handle_exception

    def cleanup_threads(self):
        if self.chat_thread and self.chat_thread.is_alive():
            logging.info("Thread'ler temizleniyor (daemon=True, beklemeye gerek yok)")

    def show_notification(self, title, message, typ="info"):
        popup = ctk.CTkToplevel(self.root)
        popup.title("")
        popup.geometry("350x150")
        popup.configure(fg_color=self.colors["card"])
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        popup.geometry(f"+{x}+{y}")
        icons = {"info": ("ℹ️", self.colors["primary"]), "success": ("✅", self.colors["secondary"]), "error": ("❌", self.colors["danger"]), "warning": ("⚠️", self.colors["accent"])}
        icon, color = icons.get(typ, icons["info"])
        
        # Başlık çerçevesi
        header_frame = ctk.CTkFrame(popup, fg_color=color, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Başlık metni - beyaz renkte
        ctk.CTkLabel(header_frame, text=f"{icon} {title}", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(pady=8)
        
        # Mesaj metni - tema rengine göre
        text_color = "white" if self.appearance_mode == "dark" else self.colors["dark"]
        ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=11), text_color=text_color, wraplength=300).pack(pady=15)
        
        # Tamam butonu
        ctk.CTkButton(popup, text=self.translate("ok"), command=popup.destroy, width=80, height=25, corner_radius=8, fg_color=color).pack(pady=5)
        popup.after(2500, popup.destroy)

    # ---------- RUN ----------
    def run(self):
        self.root.mainloop()

# -------------------- BAŞLATMA --------------------
def start_main_app(authorized_youtube_name):
    try:
        app = ModernYouTubeMezatYardimcisi(authorized_youtube_name)
        app.run()
    except KeyboardInterrupt:
        print("⚠️ Ctrl+C algılandı – GUI kapanma penceresi gösteriliyor...")
        if hasattr(app, 'on_closing') and app.root and app.root.winfo_exists():
            app.on_closing()
        else:
            # GUI yoksa veya artık kapalıysa, doğrudan çık
            print("⚠️ Program kapanıyor...")
            sys.exit(0)

if __name__ == "__main__":
    try:
        if not os.path.exists("license_codes.json"):
            with open("license_codes.json", "w", encoding="utf-8") as f:
                json.dump({"valid_codes": ["DEMO123", "TEST456"], "channel_licenses": {"Test_Hesabi": ["DEMO123"]}}, f, ensure_ascii=False, indent=2)
        if os.path.exists("auth_data.json"):
            try:
                with open("auth_data.json", encoding="utf-8") as f:
                    auth = json.load(f)
                if auth.get("authenticated"):
                    start_main_app(auth["youtube_name"])
                else:
                    raise ValueError("Geçersiz auth_data.json")
            except Exception as e:
                logging.critical(f"Auth hatası: {e}")
                print(f"Auth dosyası hatası: {e}")
                print("Yeni yetkilendirme ekranı açılıyor...")
                AuthScreen(start_main_app).run()
        else:
            AuthScreen(start_main_app).run()
    except KeyboardInterrupt:
        print("⚠️ Ctrl+C algılandı – program kapatılıyor...")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Başlatma hatası: {e}")
        print(f"Başlatma hatası: {e}")
        print("Program 10 saniye içinde kapanacak...")
        time.sleep(10)
        sys.exit(1)