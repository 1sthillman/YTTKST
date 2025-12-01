"""
WebSocket Tabanlı Chat Bağlantı Modülü
API kullanmadan doğrudan WebSocket bağlantısı ile chat mesajlarını çeker
"""

import json
import time
import logging
import threading
import re
import websocket
import requests
import random
from queue import Queue
import ssl
import sys

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebSocketChatConnector:
    """WebSocket tabanlı chat bağlantı sınıfı"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.ws = None
        self.connected = False
        self.last_message_time = time.time()
        self.error_count = 0
        self.max_errors = 10
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Origin": "https://www.tiktok.com",
            "Referer": "https://www.tiktok.com/",
        })
        self.room_id = None
        self.device_id = f"{int(time.time() * 1000)}"
        
    def extract_tiktok_info(self):
        """TikTok URL'sinden gerekli bilgileri çıkartır"""
        if "tiktok.com" not in self.url.lower():
            return False
            
        try:
            # URL'den username çıkart
            username = None
            if "@" in self.url:
                username_match = re.search(r"@([A-Za-z0-9_.]+)", self.url)
                if username_match:
                    username = username_match.group(1)
            
            if not username:
                logging.error(f"TikTok kullanıcı adı çıkarılamadı: {self.url}")
                self.message_queue.put(("SISTEM", f"TikTok kullanıcı adı çıkarılamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            # Canlı yayın sayfasını aç
            live_url = f"https://www.tiktok.com/@{username}/live"
            logging.info(f"TikTok canlı yayın sayfası açılıyor: {live_url}")
            
            response = self.session.get(live_url, timeout=15)
            if response.status_code != 200:
                logging.error(f"TikTok sayfasına erişilemedi: {response.status_code}")
                self.message_queue.put(("SISTEM", f"TikTok sayfasına erişilemedi: {response.status_code}", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            html_content = response.text
            
            # WebSocket URL'sini bul
            ws_match = re.search(r'"wss://([^"]+)"', html_content)
            if not ws_match:
                logging.error("TikTok WebSocket URL'si bulunamadı")
                self.message_queue.put(("SISTEM", "TikTok WebSocket URL'si bulunamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            # Room ID'yi bul
            room_id_match = re.search(r'"roomId":"(\d+)"', html_content)
            if not room_id_match:
                logging.error("TikTok Room ID bulunamadı")
                self.message_queue.put(("SISTEM", "TikTok Room ID bulunamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            self.room_id = room_id_match.group(1)
            ws_url = f"wss://{ws_match.group(1)}"
            
            # Başlık bilgisini al
            title_match = re.search(r'"title":"([^"]+)"', html_content)
            title = title_match.group(1) if title_match else username
            
            logging.info(f"TikTok WebSocket URL'si bulundu: {ws_url[:30]}...")
            logging.info(f"TikTok Room ID: {self.room_id}")
            
            self.message_queue.put(("SISTEM", f"TikTok canlı yayın bulundu: {title}", time.strftime("%H:%M:%S"), "TikTok"))
            
            return ws_url
        except Exception as e:
            logging.error(f"TikTok bilgileri çıkartılırken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
            
    def extract_youtube_info(self):
        """YouTube URL'sinden gerekli bilgileri çıkartır"""
        if "youtube.com" not in self.url.lower() and "youtu.be" not in self.url.lower():
            return False
            
        try:
            # Video ID'yi çıkart
            video_id = None
            if "youtube.com/watch" in self.url:
                video_id_match = re.search(r"v=([^&]+)", self.url)
                if video_id_match:
                    video_id = video_id_match.group(1)
            elif "youtu.be/" in self.url:
                video_id_match = re.search(r"youtu\.be/([^?&]+)", self.url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    
            if not video_id:
                logging.error(f"YouTube video ID çıkarılamadı: {self.url}")
                self.message_queue.put(("SISTEM", f"YouTube video ID çıkarılamadı", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            # Video sayfasını aç
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            logging.info(f"YouTube video sayfası açılıyor: {watch_url}")
            
            response = self.session.get(watch_url, timeout=15)
            if response.status_code != 200:
                logging.error(f"YouTube sayfasına erişilemedi: {response.status_code}")
                self.message_queue.put(("SISTEM", f"YouTube sayfasına erişilemedi: {response.status_code}", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            html_content = response.text
            
            # Chat için continuation token'ı bul
            continuation_match = re.search(r'"continuation":"([^"]+)"', html_content)
            if not continuation_match:
                logging.error("YouTube continuation token bulunamadı")
                self.message_queue.put(("SISTEM", "YouTube chat bilgisi bulunamadı", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            continuation = continuation_match.group(1)
            
            # Video başlığını al
            title_match = re.search(r'"title":"([^"]+)"', html_content)
            title = title_match.group(1) if title_match else video_id
            
            logging.info(f"YouTube continuation token bulundu: {continuation[:30]}...")
            
            self.message_queue.put(("SISTEM", f"YouTube canlı yayın bulundu: {title}", time.strftime("%H:%M:%S"), "YouTube"))
            
            # YouTube için WebSocket URL'si değil, continuation token döndürüyoruz
            return continuation
        except Exception as e:
            logging.error(f"YouTube bilgileri çıkartılırken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"YouTube bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
            return False
    
    def connect_tiktok(self):
        """TikTok WebSocket bağlantısı kurar"""
        ws_url = self.extract_tiktok_info()
        if not ws_url:
            return False
            
        try:
            # WebSocket bağlantısı kur
            def on_message(ws, message):
                try:
                    # WebSocket mesajını işle
                    data = json.loads(message)
                    if "msg" in data:
                        msg_type = data.get("type", "")
                        if msg_type == "chat":
                            user = data["msg"].get("user", {}).get("uniqueId", "Anonim")
                            text = data["msg"].get("content", "")
                            current_time = time.strftime("%H:%M:%S")
                            self.message_queue.put((user, text, current_time, "TikTok"))
                            self.last_message_time = time.time()
                except Exception as e:
                    logging.error(f"TikTok mesaj işleme hatası: {str(e)}")
                    
            def on_error(ws, error):
                logging.error(f"TikTok WebSocket hatası: {str(error)}")
                self.error_count += 1
                
            def on_close(ws, close_status_code, close_msg):
                logging.info("TikTok WebSocket bağlantısı kapatıldı")
                self.connected = False
                
            def on_open(ws):
                logging.info("TikTok WebSocket bağlantısı açıldı")
                self.connected = True
                self.message_queue.put(("SISTEM", "TikTok chat bağlantısı kuruldu", time.strftime("%H:%M:%S"), "TikTok"))
                self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
                
                # Giriş mesajı gönder
                join_msg = {
                    "type": "join",
                    "roomId": self.room_id,
                    "deviceId": self.device_id
                }
                ws.send(json.dumps(join_msg))
                
            # WebSocket bağlantısını başlat
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(ws_url,
                                            on_message=on_message,
                                            on_error=on_error,
                                            on_close=on_close,
                                            on_open=on_open,
                                            header={"User-Agent": self.user_agent})
            
            # WebSocket bağlantısını ayrı bir thread'de başlat
            wst = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            wst.daemon = True
            wst.start()
            
            # Bağlantı kurulana kadar bekle
            wait_time = 0
            while not self.connected and wait_time < 10 and not self.stop_event.is_set():
                time.sleep(0.5)
                wait_time += 0.5
                
            if not self.connected:
                logging.error("TikTok WebSocket bağlantısı kurulamadı")
                self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı kurulamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            return True
        except Exception as e:
            logging.error(f"TikTok WebSocket bağlantısı kurulurken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
    
    def connect_youtube(self):
        """YouTube chat bağlantısı kurar"""
        continuation = self.extract_youtube_info()
        if not continuation:
            return False
            
        try:
            self.connected = True
            self.message_queue.put(("SISTEM", "YouTube chat bağlantısı kuruldu", time.strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
            
            # Chat mesajlarını çekme döngüsü
            while not self.stop_event.is_set() and self.connected:
                try:
                    # Chat API bağlantısı
                    chat_params = {
                        "continuation": continuation,
                        "pbj": "1",
                    }
                    
                    response = self.session.get("https://www.youtube.com/live_chat", params=chat_params, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Bir sonraki continuation token'ını al
                            if isinstance(data, list) and len(data) > 1 and "response" in data[1]:
                                if "continuationContents" in data[1]["response"]:
                                    contents = data[1]["response"]["continuationContents"]
                                    if "liveChatContinuation" in contents:
                                        continuations = contents["liveChatContinuation"]["continuations"]
                                        if continuations and "invalidationContinuationData" in continuations[0]:
                                            continuation = continuations[0]["invalidationContinuationData"]["continuation"]
                                        
                                        # Mesajları işle
                                        if "actions" in contents["liveChatContinuation"]:
                                            actions = contents["liveChatContinuation"]["actions"]
                                            for action in actions:
                                                if "addChatItemAction" in action and "item" in action["addChatItemAction"]:
                                                    item = action["addChatItemAction"]["item"]
                                                    if "liveChatTextMessageRenderer" in item:
                                                        renderer = item["liveChatTextMessageRenderer"]
                                                        author = renderer["authorName"]["simpleText"] if "authorName" in renderer else "Anonim"
                                                        
                                                        # Mesaj metnini al
                                                        message = ""
                                                        if "message" in renderer and "runs" in renderer["message"]:
                                                            for run in renderer["message"]["runs"]:
                                                                if "text" in run:
                                                                    message += run["text"]
                                                        
                                                        if message:
                                                            current_time = time.strftime("%H:%M:%S")
                                                            self.message_queue.put((author, message, current_time, "YouTube"))
                                                            self.last_message_time = time.time()
                            
                            self.error_count = 0  # Başarılı istek, hata sayacını sıfırla
                        except Exception as e:
                            logging.error(f"YouTube mesaj çözümleme hatası: {str(e)}")
                            self.error_count += 1
                    else:
                        logging.error(f"YouTube chat API hata kodu: {response.status_code}")
                        self.error_count += 1
                        
                    # Hata sayacı kontrolü
                    if self.error_count >= self.max_errors:
                        logging.error(f"Çok fazla YouTube bağlantı hatası: {self.error_count}")
                        self.message_queue.put(("SISTEM", f"Çok fazla YouTube bağlantı hatası ({self.error_count}), bağlantı yenileniyor", time.strftime("%H:%M:%S"), "YouTube"))
                        
                        # Bağlantıyı yenile
                        new_continuation = self.extract_youtube_info()
                        if new_continuation:
                            continuation = new_continuation
                            self.error_count = 0
                        else:
                            self.connected = False
                            break
                    
                    # Son mesaj kontrolü
                    if time.time() - self.last_message_time > 60:
                        self.message_queue.put(("SISTEM", "YouTube bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "YouTube"))
                        self.last_message_time = time.time()
                    
                    # İstek sıklığını düzenle
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"YouTube chat bağlantısı hatası: {str(e)}")
                    self.error_count += 1
                    time.sleep(5)
            
            return True
        except Exception as e:
            logging.error(f"YouTube bağlantısı kurulurken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"YouTube bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
            return False
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.connected = False
        self.stop_event.set()
        
        if self.ws:
            self.ws.close()
    
    def run(self):
        """Ana çalışma metodu"""
        if "tiktok.com" in self.url.lower():
            return self.connect_tiktok()
        elif "youtube.com" in self.url.lower() or "youtu.be" in self.url.lower():
            return self.connect_youtube()
        else:
            logging.error(f"Desteklenmeyen URL: {self.url}")
            self.message_queue.put(("SISTEM", "Desteklenmeyen URL formatı", time.strftime("%H:%M:%S"), "Sistem"))
            return False


def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok chat bağlantısını başlatır"""
    connector = WebSocketChatConnector(url, message_queue, stop_event)
    connector.run()


def start_youtube_chat(url, message_queue=None, stop_event=None):
    """YouTube chat bağlantısını başlatır"""
    connector = WebSocketChatConnector(url, message_queue, stop_event)
    connector.run()


# Test ve debug
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = input("TikTok veya YouTube URL'si girin: ")
    
    queue = Queue()
    stop = threading.Event()
    
    connector = WebSocketChatConnector(url, queue, stop)
    threading.Thread(target=connector.run, daemon=True).start()
    
    try:
        while True:
            if not queue.empty():
                message = queue.get()
                print(f"{message[3]} | {message[2]} | {message[0]}: {message[1]}")
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        connector.close()
        print("Bağlantı kapatıldı.")

