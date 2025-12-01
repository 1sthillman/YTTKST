#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geliştirilmiş ChatDownloader yardımcı modülü
YouTube Mezat Yardımcısı için güvenli ve hızlı chat bağlantısı sağlar
"""

import time
import logging
import threading
import datetime
import requests
import socket
from queue import Queue

# Loglama ayarları
logging.basicConfig(
    filename="mezat.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

class EnhancedChatDownloader:
    def __init__(self):
        """Geliştirilmiş chat indirme yöneticisi başlat"""
        self.stop_event = None
        self.message_queue = None
        self.chat_thread = None
        self.last_url = None
        self.last_error_time = 0
        self.error_count = 0
        self.connected = False
        self.processed_messages = set()  # Tekrarlanan mesajları önlemek için

    def start_chat(self, url, message_queue, stop_event):
        """
        YouTube chat bağlantısını başlatır.
        
        Args:
            url: YouTube canlı yayın URL'si
            message_queue: Mesajların gönderileceği kuyruk
            stop_event: Durdurma işareti (threading.Event)
            
        Returns:
            chat_thread: Başlatılan thread
        """
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.last_url = url
        
        # Önce mevcut thread varsa durdur
        if self.chat_thread and self.chat_thread.is_alive():
            self.stop_event.set()
            try:
                self.chat_thread.join(1.0)  # Kısa bir süre bekle
            except Exception as e:
                logging.error(f"Mevcut thread durdurma hatası: {e}")
        
        # Yeni thread oluştur
        self.stop_event.clear()
        self.chat_thread = threading.Thread(
            target=self._chat_worker,
            args=(url,),
            daemon=True,
            name="EnhancedChatDownloader"
        )
        self.chat_thread.start()
        
        # Bağlantı durumunu güncelle
        self.message_queue.put(("__STATUS__", "connection_connecting", "yellow", "YouTube"))
        
        return self.chat_thread

    def _chat_worker(self, url):
        """
        ChatDownloader ile chat mesajlarını çeken ana işçi thread.
        Bu fonksiyon asla çıkmaz, sürekli bağlantıyı korur.
        
        Args:
            url: YouTube canlı yayın URL'si
        """
        logging.info("[EnhancedChatDownloader] Thread başlatıldı -> %s", url)
        
        # ChatDownloader modülünün yüklü olduğunu kontrol et
        try:
            from chat_downloader import ChatDownloader
        except ImportError:
            try:
                # Otomatik kurulum dene
                import sys
                import subprocess
                logging.info("ChatDownloader modülü yüklü değil, otomatik yükleniyor...")
                self.message_queue.put(("SISTEM", "ChatDownloader modülü yükleniyor, lütfen bekleyin...", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                subprocess.check_call([sys.executable, "-m", "pip", "install", "chat-downloader>=0.1.8"])
                
                # Tekrar içe aktarmayı dene
                try:
                    from chat_downloader import ChatDownloader
                    logging.info("ChatDownloader başarıyla yüklendi")
                    self.message_queue.put(("SISTEM", "ChatDownloader modülü başarıyla yüklendi", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                except ImportError:
                    logging.error("ChatDownloader yüklenemedi")
                    self.message_queue.put(("SISTEM", "ChatDownloader modülü yüklenemedi, bağlantı sağlanamıyor", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                    self.message_queue.put(("__STATUS__", "connection_error_module_missing", "red", "YouTube"))
                    return
            except Exception as e:
                logging.error(f"ChatDownloader otomatik kurulum hatası: {e}")
                self.message_queue.put(("SISTEM", f"ChatDownloader modülü yüklenirken hata: {e}", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                self.message_queue.put(("__STATUS__", "connection_error_module_missing", "red", "YouTube"))
                return
        
        # URL normalizasyonu
        url = self._normalize_url(url)
        if not url:
            self.message_queue.put(("SISTEM", "Geçersiz YouTube URL'si. Lütfen kontrol edin.", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_error_invalid_url", "red", "YouTube"))
            return
            
        # İnternet bağlantısını kontrol et
        if not self._check_internet_connection():
            self.message_queue.put(("SISTEM", "İnternet bağlantısı bulunamadı. Lütfen bağlantınızı kontrol edin.", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_error_no_internet", "red", "YouTube"))
            return
            
        # YouTube bağlantısını kontrol et
        if not self._check_youtube_availability(url):
            self.message_queue.put(("SISTEM", "YouTube'a erişilemiyor veya video mevcut değil. Lütfen URL'yi kontrol edin.", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_error_youtube_unavailable", "red", "YouTube"))
            return

        # Ana bağlantı döngüsü - asla çıkmaz
        retry_count = 0
        max_retries = 20
        while not self.stop_event.is_set():
            try:
                # Bağlantı durumunu güncelle
                self.message_queue.put(("__STATUS__", "connection_connecting", "yellow", "YouTube"))
                
                # Bağlantı parametreleri
                params = {
                    "timeout": 30,                  # Bağlantı zaman aşımı
                    "max_attempts": 999,            # Sürekli deneme
                    "retry_timeout": 1,             # Yeniden deneme zamanı
                    "message_groups": ["messages", "superchat"],  # Mesaj grupları
                    "interruptible": True,          # Kesilebilir
                    "headers": {                    # İstek başlıkları
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
                    }
                }
                
                # ChatDownloader nesnesi oluştur
                downloader = ChatDownloader()
                
                # Chat bağlantısını kur
                logging.info("[EnhancedChatDownloader] Chat bağlantısı kuruluyor...")
                chat = downloader.get_chat(url, **params)
                
                # Bağlantı başarılı - durumu güncelle
                self.connected = True
                retry_count = 0  # Hata sayacını sıfırla
                self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
                self.message_queue.put(("SISTEM", "--- YouTube Chat Bağlantısı Kuruldu ---", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                logging.info("[EnhancedChatDownloader] Bağlantı kuruldu, mesajlar alınıyor...")
                
                # Tekrarlanan mesajları önlemek için kontrol
                last_msg_cache = {}
                
                # Chat mesajlarını al
                for message in chat:
                    # Eğer durdurma işareti gelirse döngüden çık
                    if self.stop_event.is_set():
                        break
                    
                    # Mesaj bilgilerini al
                    author = message.get("author", {}).get("name", "Anonim")
                    msg_text = message.get("message", "")
                    
                    # Boş mesajları atla
                    if not msg_text:
                        continue
                        
                    # Zaman damgası
                    time_str = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Tekrarlanan mesajları kontrol et
                    msg_id = f"{author}:{msg_text}"
                    if msg_id in last_msg_cache:
                        last_time = last_msg_cache[msg_id]
                        if time.time() - last_time < 1.0:  # 1 saniye içinde aynı mesaj geldiyse atla
                            continue
                    
                    # Cache'e ekle
                    last_msg_cache[msg_id] = time.time()
                    
                    # Cache boyutunu kontrol et (en fazla 100 mesaj)
                    if len(last_msg_cache) > 100:
                        # En eski girdiyi sil
                        oldest_key = min(last_msg_cache, key=last_msg_cache.get)
                        del last_msg_cache[oldest_key]
                    
                    # Mesajı işlenmek üzere kuyruğa ekle
                    self.message_queue.put((author, msg_text, time_str, "YouTube"))
                
                # Bağlantı koptu, yeniden bağlan
                logging.info("[EnhancedChatDownloader] Bağlantı koptu, yeniden bağlanılıyor...")
                self.connected = False
                
            except Exception as e:
                # Bağlantı hatası
                self.connected = False
                retry_count += 1
                now = time.time()
                
                # Hataları çok sık loglamayı önle (en az 30 saniye aralıkla)
                if now - self.last_error_time > 30:
                    logging.error(f"[EnhancedChatDownloader] Bağlantı hatası: {e}")
                    self.last_error_time = now
                
                # Hata durumunu ekranda göster
                if retry_count <= max_retries:
                    # Hata türüne göre farklı mesajlar
                    error_type = str(type(e).__name__)
                    if "Timeout" in error_type:
                        self.message_queue.put(("SISTEM", "Bağlantı zaman aşımına uğradı, yeniden deneniyor...", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                    elif "Connection" in error_type:
                        self.message_queue.put(("SISTEM", "Bağlantı sorunu, yeniden deneniyor...", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                    else:
                        self.message_queue.put(("SISTEM", f"Bağlantı hatası: {str(e)[:50]}...", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                    
                    self.message_queue.put(("__STATUS__", f"connection_error_{retry_count}/{max_retries}", "red", "YouTube"))
                    
                    # Artan bekleme süresi (exponential backoff)
                    wait_time = min(2 ** (retry_count - 1), 60)  # En fazla 60 saniye bekle
                    time.sleep(wait_time)
                else:
                    # Maksimum deneme sayısı aşıldı
                    self.message_queue.put(("__STATUS__", "connection_error_max_retries", "red", "YouTube"))
                    self.message_queue.put(("SISTEM", "Maksimum bağlantı deneme sayısı aşıldı. URL doğru mu?", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                    
                    # URL'yi kontrol et ve tekrar dene
                    if self._check_youtube_availability(url):
                        self.message_queue.put(("SISTEM", "YouTube canlı yayın mevcut, yeniden bağlanılıyor...", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                        retry_count = 0  # Sayacı sıfırla
                        time.sleep(10)
                    else:
                        self.message_queue.put(("SISTEM", "YouTube canlı yayın bulunamadı veya erişilemiyor.", datetime.datetime.now().strftime("%H:%M:%S"), "YouTube"))
                        time.sleep(30)
                        retry_count = 0  # Sayacı sıfırla

    def _normalize_url(self, url):
        """YouTube URL'sini normalize eder ve doğrular"""
        if not url:
            return None
            
        # HTTP ekle
        if not url.startswith("http"):
            url = f"https://{url}"
            
        # Kısa URL (youtu.be) kontrolü
        if "youtu.be" in url:
            try:
                video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
                url = f"https://www.youtube.com/watch?v={video_id}"
            except Exception as e:
                logging.error(f"URL dönüştürme hatası: {e}")
                return None
                
        # Video ID'yi kontrol et
        if "watch?v=" in url:
            try:
                video_id = url.split("watch?v=")[1].split("&")[0].split("?")[0]
                if len(video_id) != 11:
                    logging.warning(f"Geçersiz YouTube video ID uzunluğu: {len(video_id)}")
                    return None
                return f"https://www.youtube.com/watch?v={video_id}"
            except Exception as e:
                logging.error(f"Video ID çıkarma hatası: {e}")
                return None
                
        # Diğer URL formatları
        return url

    def _check_internet_connection(self):
        """İnternet bağlantısını kontrol eder"""
        try:
            socket.create_connection(("www.google.com", 443), timeout=5)
            return True
        except Exception as e:
            logging.error(f"İnternet bağlantı kontrolü hatası: {e}")
            return False

    def _check_youtube_availability(self, url):
        """YouTube canlı yayın erişilebilirliğini kontrol eder"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"YouTube erişilebilirlik kontrolü hatası: {e}")
            return False

    def stop(self):
        """Chat bağlantısını durdurur"""
        if self.stop_event:
            self.stop_event.set()
            
# Kolay kullanım için yardımcı fonksiyon
def start_chat(url, message_queue, stop_event):
    """
    YouTube chat bağlantısını başlatmak için kolay kullanım fonksiyonu
    
    Args:
        url: YouTube canlı yayın URL'si
        message_queue: Mesajların gönderileceği kuyruk
        stop_event: Durdurma işareti (threading.Event)
        
    Returns:
        chat_thread: Başlatılan thread
    """
    downloader = EnhancedChatDownloader()
    thread = downloader.start_chat(url, message_queue, stop_event)
    return thread

