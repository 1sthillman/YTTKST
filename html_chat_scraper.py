#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import json
import logging
import requests
import threading
from datetime import datetime
from bs4 import BeautifulSoup

# YouTube chat için HTML tabanlı scraper
class HTMLChatScraper:
    def __init__(self, url, message_queue, stop_event):
        self.url = url
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.session = requests.Session()
        self.video_id = None
        self.continuation = None
        self.last_timestamp = time.time()
        self.processed_messages = set()  # İşlenmiş mesajları tutmak için set
        self.client_version = "2.20230731.01.00"
        self.api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"  # YouTube genel API anahtarı
        
        # Gerçek bir tarayıcı gibi davran
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/'
        })
    
    def extract_video_id(self, url):
        """URL'den video ID'sini çıkarır."""
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
            r"(?:embed\/|v\/|youtu.be\/)([0-9A-Za-z_-]{11})",
            r"^([0-9A-Za-z_-]{11})$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        logging.error(f"Video ID bulunamadı: {url}")
        self.message_queue.put(("SISTEM", "Geçersiz YouTube URL'si. Video ID bulunamadı.", time.strftime("%H:%M:%S"), "YouTube"))
        return None
    
    def get_initial_page(self):
        """İlk sayfa verisini çeker ve gerekli bilgileri çıkarır."""
        try:
            video_url = f"https://www.youtube.com/watch?v={self.video_id}"
            response = self.session.get(video_url, timeout=15)
            
            if response.status_code != 200:
                logging.error(f"Video sayfası alınamadı: {response.status_code}")
                self.message_queue.put(("SISTEM", f"Video sayfasına erişilemiyor (HTTP {response.status_code}).", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            html = response.text
            
            # Canlı yayın bilgilerini çıkar
            is_live_broadcast = False
            if '"isLiveBroadcast":true' in html or '"isLiveContent":true' in html:
                is_live_broadcast = True
            
            if not is_live_broadcast:
                logging.error("Bu bir canlı yayın değil.")
                self.message_queue.put(("SISTEM", "Bu bir canlı yayın değil. Sadece canlı yayınlar desteklenir.", time.strftime("%H:%M:%S"), "YouTube"))
                return False
            
            # Chat continuation token'ını çıkar
            # Hem yeni hem eski format için arama yap
            match = re.search(r'"continuation":"([^"]+)"', html)
            if not match:
                match = re.search(r'continuation":"([^"]+)', html)
                
            if match:
                self.continuation = match.group(1)
                logging.info(f"Chat continuation bulundu: {self.continuation[:20]}...")
                return True
            else:
                # Sayfa içinde chat mevcut mu kontrol et
                if "liveChatRenderer" not in html:
                    logging.error("Bu videoda canlı chat bulunmuyor.")
                    self.message_queue.put(("SISTEM", "Bu videoda canlı chat bulunmuyor veya devre dışı bırakılmış.", time.strftime("%H:%M:%S"), "YouTube"))
                    return False
                
                logging.error("Chat continuation token bulunamadı.")
                self.message_queue.put(("SISTEM", "Chat verileri alınamıyor. Sayfayı yeniden yüklemeyi deneyin.", time.strftime("%H:%M:%S"), "YouTube"))
                return False
            
        except Exception as e:
            logging.exception(f"İlk sayfa alımı hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"Bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
            return False
    
    def get_chat_data(self):
        """YouTube chat verilerini çeker."""
        if not self.continuation:
            return []
    
        try:
            # Chat API endpoint URL'si
            chat_url = f"https://www.youtube.com/youtubei/v1/live_chat/get_live_chat?key={self.api_key}"
            
            # API isteği için gerekli veri
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": self.client_version,
                    }
                },
                "continuation": self.continuation
            }
            
            # API isteği gönder
            response = self.session.post(chat_url, json=payload, timeout=15)
            
            if response.status_code != 200:
                logging.error(f"Chat API hatası: {response.status_code}")
                return []
                
            try:
                return response.json()
                    except json.JSONDecodeError:
                logging.error("JSON decode hatası")
                return []
            
        except Exception as e:
            logging.exception(f"Chat veri alımı hatası: {str(e)}")
            # Bağlantı hatası durumunda continuation token'ı sıfırla
            self.continuation = None
            return []
    
    def process_chat_data(self, data):
        """Chat verilerini işleyip mesajlara dönüştürür."""
        messages = []
        
        if not data:
            return messages
            
        # Yeni continuation token'ı güncelle
        try:
            continuations = data.get("continuationContents", {}).get("liveChatContinuation", {}).get("continuations", [])
            if continuations and len(continuations) > 0:
                if "invalidationContinuationData" in continuations[0]:
                    self.continuation = continuations[0]["invalidationContinuationData"]["continuation"]
                elif "timedContinuationData" in continuations[0]:
                    self.continuation = continuations[0]["timedContinuationData"]["continuation"]
                elif "reloadContinuationData" in continuations[0]:
                    self.continuation = continuations[0]["reloadContinuationData"]["continuation"]
                elif "liveChatReplayContinuationData" in continuations[0]:
                    self.continuation = continuations[0]["liveChatReplayContinuationData"]["continuation"]
        except Exception as e:
            logging.error(f"Continuation token güncelleme hatası: {str(e)}")
        
        # Mesajları çıkar
        try:
            actions = data.get("continuationContents", {}).get("liveChatContinuation", {}).get("actions", [])
            
            for action in actions:
                if "addChatItemAction" in action:
                    item = action["addChatItemAction"]["item"]
                    
                    # Benzersiz mesaj ID'si
                    item_id = item.get("liveChatTextMessageRenderer", {}).get("id", "")
                    if not item_id:
                        item_id = item.get("liveChatPaidMessageRenderer", {}).get("id", "")
                    
                    # Daha önce işlenmiş mesajları atla
                    if item_id in self.processed_messages:
                        continue
                        
                    # Mesaj ID'sini kaydet
                    if item_id:
                        self.processed_messages.add(item_id)
                    
                    # Normal mesaj
                    if "liveChatTextMessageRenderer" in item:
                        renderer = item["liveChatTextMessageRenderer"]
                        author_name = renderer.get("authorName", {}).get("simpleText", "Anonim")
                        
                        # Mesaj içeriğini birleştir
                        message_runs = renderer.get("message", {}).get("runs", [])
                        message_text = ""
                        
                        for run in message_runs:
                            if "text" in run:
                                message_text += run["text"]
                            elif "emoji" in run:
                                message_text += run["emoji"].get("shortcuts", [""])[0]
                                
                        messages.append({
                            "author": author_name,
                            "message": message_text,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                    
                    # SuperChat/Paid mesaj
                    elif "liveChatPaidMessageRenderer" in item:
                        renderer = item["liveChatPaidMessageRenderer"]
                        author_name = renderer.get("authorName", {}).get("simpleText", "Anonim") + " [SuperChat]"
                        
                        # Mesaj içeriğini birleştir
                        message_runs = renderer.get("message", {}).get("runs", [])
                        message_text = ""
                        
                        for run in message_runs:
                            if "text" in run:
                                message_text += run["text"]
                                
                        messages.append({
                            "author": author_name,
                            "message": message_text,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
        except Exception as e:
            logging.error(f"Mesaj işleme hatası: {str(e)}")
        
        return messages
    
    def run(self):
        """Ana çalıştırma fonksiyonu."""
        self.video_id = self.extract_video_id(self.url)
        if not self.video_id:
            return
        
        # Bağlantı başlıyor
        self.message_queue.put(("__STATUS__", "connection_connecting", "yellow", "YouTube"))
        logging.info(f"HTML Chat Scraper başlatılıyor: {self.video_id}")
        
        connection_retries = 0
        max_retries = 20
        
        while not self.stop_event.is_set():
            try:
                # İlk sayfa verisini al
                if not self.continuation:
                    success = self.get_initial_page()
                    if not success:
                        connection_retries += 1
                        if connection_retries > max_retries:
                            self.message_queue.put(("SISTEM", f"Maksimum bağlantı deneme sayısı aşıldı ({max_retries}). Bağlantı kesildi.", time.strftime("%H:%M:%S"), "YouTube"))
                            self.message_queue.put(("__STATUS__", "connection_error_max_retries", "red", "YouTube"))
                            break
                            
                        # Bekleme süresi (artan)
                        wait_time = min(2 * connection_retries, 30)
                        logging.info(f"Yeniden bağlanmadan önce {wait_time} saniye bekleniyor...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Bağlantı başarılı
                        connection_retries = 0
                        self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
                        self.message_queue.put(("SISTEM", f"YouTube Chat bağlantısı kuruldu: {self.video_id}", time.strftime("%H:%M:%S"), "YouTube"))
                
                # Chat verilerini al
                chat_data = self.get_chat_data()
                
                # Chat verilerini işle
                messages = self.process_chat_data(chat_data)
                
                # Mesajları gönder
                for msg in messages:
                    if self.stop_event.is_set():
                        break
                        
                    author = msg["author"]
                    message = msg["message"]
                    timestamp = msg["timestamp"]
                    
                    # Mesajı gönder
                    self.message_queue.put((author, message, timestamp, "YouTube"))
                
                # Son aktif zamanı güncelle
                self.last_timestamp = time.time()
                
                # Çok fazla istek göndermemek için bekleme
                time.sleep(0.5)
            except Exception as e:
                logging.exception(f"HTML Chat Scraper genel hatası: {str(e)}")
                # Bağlantı hatası, continuation token'ı sıfırla ve tekrar dene
                self.continuation = None
                    time.sleep(5)
                    
        # Thread durduruldu
        logging.info("HTML Chat Scraper durduruldu.")

def start_youtube_chat(url, message_queue, stop_event):
    """YouTube chat bağlantısını başlatır."""
    try:
        scraper = HTMLChatScraper(url, message_queue, stop_event)
        chat_thread = threading.Thread(target=scraper.run, daemon=True, name="HTMLChatScraperWorker")
        chat_thread.start()
        return chat_thread
    except Exception as e:
        logging.exception(f"HTML Chat Scraper başlatma hatası: {str(e)}")
        message_queue.put(("SISTEM", f"YouTube bağlantısı başlatılamadı: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
        message_queue.put(("__STATUS__", "connection_error", "red", "YouTube"))
        return None