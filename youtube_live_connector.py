#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import logging
import requests
import threading
from datetime import datetime

# YouTube Live Chat için optimize edilmiş bağlantı sınıfı
class YouTubeLiveChat:
    def __init__(self, url, message_queue, stop_event):
        self.url = url
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.session = requests.Session()
        self.video_id = None
        self.continuation = None
        self.client_version = "2.20230731.01.00"
        self.api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"  # YouTube'un genel API anahtarı
        self.last_timestamp = time.time()
        
        # Sağlam header'lar
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Content-Type': 'application/json',
            'X-YouTube-Client-Name': '1',
            'X-YouTube-Client-Version': self.client_version
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
    
    def get_initial_data(self):
        """İlk sayfa verisini çeker ve continuation token'ı çıkarır."""
        try:
            video_url = f"https://www.youtube.com/watch?v={self.video_id}"
            response = self.session.get(video_url, timeout=15)
            
            if response.status_code != 200:
                logging.error(f"Video sayfası alınamadı: {response.status_code}")
                self.message_queue.put(("SISTEM", f"Video sayfasına erişilemiyor (HTTP {response.status_code}).", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            html = response.text
            
            # Sayfa içeriğinde live chat continuation değerini bul
            match = re.search(r'"continuation":"([^"]+)"', html)
            if not match:
                match = re.search(r'continuation":"([^"]+)', html)
                
            if match:
                self.continuation = match.group(1)
                logging.info(f"Chat continuation bulundu: {self.continuation[:20]}...")
                return True
            else:
                # Canlı yayın kontrolü yap
                if "isLiveBroadcast" not in html and "isLiveContent" not in html:
                    logging.error("Bu bir canlı yayın değil veya chat devre dışı.")
                    self.message_queue.put(("SISTEM", "Bu bir canlı yayın değil veya chat devre dışı bırakılmış.", time.strftime("%H:%M:%S"), "YouTube"))
                    return False
                
                logging.error("Chat continuation token bulunamadı.")
                self.message_queue.put(("SISTEM", "Chat verileri alınamıyor. Canlı yayın devam ediyor mu?", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
        except Exception as e:
            logging.exception(f"İlk veri alımı hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"Bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
            return False
    
    def get_chat_messages(self):
        """YouTube Live Chat API'sini kullanarak mesajları alır."""
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
                
            data = response.json()
            
            # Yeni continuation token'ı güncelle
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
            
            # Mesajları çıkar
            messages = []
            actions = data.get("continuationContents", {}).get("liveChatContinuation", {}).get("actions", [])
            
            for action in actions:
                if "addChatItemAction" in action:
                    item = action["addChatItemAction"]["item"]
                    
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
            
            return messages
            
        except Exception as e:
            logging.exception(f"Chat API hatası: {str(e)}")
            # Continuation token sıfırlama - tekrar ilk veriyi alma sürecine dön
            self.continuation = None
            return []
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.video_id = self.extract_video_id(self.url)
        if not self.video_id:
            return
        
        connection_retries = 0
        max_retries = 10
        
        # Bağlantı kurulmaya çalışılıyor
        self.message_queue.put(("__STATUS__", "connection_connecting", "yellow", "YouTube"))
        logging.info(f"YouTube Live Chat bağlantısı başlatılıyor: {self.video_id}")
        
        while not self.stop_event.is_set():
            try:
                # İlk veriyi al (continuation token'ı çıkar)
                if not self.continuation:
                    success = self.get_initial_data()
                    if not success:
                        connection_retries += 1
                        if connection_retries > max_retries:
                            self.message_queue.put(("SISTEM", f"Maksimum bağlantı deneme sayısı aşıldı ({max_retries}). Bağlantı kesildi.", time.strftime("%H:%M:%S"), "YouTube"))
                            self.message_queue.put(("__STATUS__", "connection_error_max_retries", "red", "YouTube"))
                            break
                            
                        # Bekleme süresi (artan)
                        wait_time = min(5 * connection_retries, 30)
                        logging.info(f"Yeniden bağlanmadan önce {wait_time} saniye bekleniyor...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Bağlantı başarılı
                        connection_retries = 0
                        self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
                        self.message_queue.put(("SISTEM", f"YouTube Live Chat bağlantısı kuruldu: {self.video_id}", time.strftime("%H:%M:%S"), "YouTube"))
                
                # Chat mesajlarını al
                messages = self.get_chat_messages()
                
                # Mesajları işle
                for msg in messages:
                    if self.stop_event.is_set():
                        break
                    
                    author = msg["author"]
                    message = msg["message"]
                    timestamp = msg["timestamp"]
                    
                    # Mesajı gönder
                    self.message_queue.put((author, message, timestamp, "YouTube"))
                    
                # Her mesaj alımından sonra son aktif zamanı güncelle
                self.last_timestamp = time.time()
                
                # Çok fazla istek göndermemek için bekleme
                time.sleep(1)
                
            except Exception as e:
                logging.exception(f"YouTube Live Chat genel hata: {str(e)}")
                # Bağlantı hatası, continuation token'ı sıfırla ve tekrar dene
                self.continuation = None
                time.sleep(5)
                
        # Thread durduruldu
        logging.info("YouTube Live Chat thread durduruldu.")

def start_youtube_chat(url, message_queue, stop_event):
    """YouTube chat bağlantısını başlatır"""
    try:
        chat = YouTubeLiveChat(url, message_queue, stop_event)
        # Thread içinde değil, doğrudan olarak çalıştır - böylece thread kontrolü dışarıda kalır
        chat_thread = threading.Thread(target=chat.run, daemon=True, name="YouTubeLiveConnectorWorker")
        chat_thread.start()
        return chat_thread
    except Exception as e:
        logging.exception(f"YouTube chat başlatma hatası: {str(e)}")
        message_queue.put(("SISTEM", f"YouTube bağlantısı başlatılamadı: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
        message_queue.put(("__STATUS__", "connection_error", "red", "YouTube"))
        return None