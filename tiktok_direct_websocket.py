"""
TikTok WebSocket Doğrudan Bağlantı Modülü
API kullanmadan doğrudan WebSocket bağlantısı ile chat mesajlarını çeker
"""

import requests
import re
import time
import logging
import threading
import json
import websocket
import ssl
from queue import Queue
import random

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TikTokWebSocketConnector:
    """TikTok WebSocket bağlantı sınıfı"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.ws = None
        self.connected = False
        self.last_message_time = time.time()
        self.error_count = 0
        self.max_errors = 5
        self.room_id = None
        self.ws_url = None
        self.backup_ws_urls = []
        self.current_url_index = 0
        self.retry_count = 0
        self.max_retries = 3
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com"
        })
        
    def extract_websocket_info(self):
        """TikTok URL'sinden WebSocket bilgilerini çıkartır"""
        try:
            # URL'yi düzelt
            if not "/live" in self.url and "@" in self.url:
                self.url = self.url.rstrip("/") + "/live"
                logging.info(f"TikTok URL düzeltildi: {self.url}")
            
            # TikTok sayfasını al
            logging.info(f"TikTok sayfası çekiliyor: {self.url}")
            
            # Farklı tarayıcı kimliklerini dene
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
            
            # Özel header'lar
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.tiktok.com/",
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            }
            
            # Farklı header kombinasyonları
            for attempt in range(3):
                try:
                    headers["User-Agent"] = random.choice(user_agents)
                    response = self.session.get(self.url, headers=headers, timeout=15)
                    logging.info(f"TikTok yanıt kodu: {response.status_code}")
                    
                    if response.status_code == 200:
                        break
                    else:
                        logging.warning(f"TikTok yanıt kodu {response.status_code}, yeniden deneniyor...")
                        time.sleep(1)
                except Exception as e:
                    logging.warning(f"TikTok sayfası çekilirken hata: {str(e)}, yeniden deneniyor...")
                    time.sleep(1)
            
            if response.status_code != 200:
                logging.error(f"TikTok sayfasına erişilemedi: {response.status_code}")
                self.message_queue.put(("SISTEM", f"TikTok sayfasına erişilemedi: {response.status_code}", time.strftime("%H:%M:%S"), "TikTok"))
                return False
            
            html_content = response.text
            
            # Debug için HTML içeriğini kaydet
            with open("tiktok_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Room ID'yi bul - Yöntem 1: roomId
            room_id_patterns = [
                r'"roomId":"?(\d+)"?',
                r'"room_id":"?(\d+)"?',
                r'"id":"?(\d+)"?',
                r'roomId=(\d+)',
                r'room_id=(\d+)',
                r'"roomId":(\d+)',
                r'"liveId":"?(\d+)"?',
                r'"live_id":"?(\d+)"?'
            ]
            
            for pattern in room_id_patterns:
                room_id_match = re.search(pattern, html_content)
                if room_id_match:
                    self.room_id = room_id_match.group(1)
                    logging.info(f"TikTok Room ID bulundu: {self.room_id}")
                    break
            
            # WebSocket URL'sini bul - Yöntem 1: Doğrudan WebSocket URL'si
            ws_url_patterns = [
                r'"wss://([^"]+)"',
                r"'wss://([^']+)'",
                r'wss://([^\s"\']+)',
                r'webSocketUrl:"([^"]+)"'
            ]
            
            for pattern in ws_url_patterns:
                ws_url_match = re.search(pattern, html_content)
                if ws_url_match:
                    self.ws_url = f"wss://{ws_url_match.group(1)}"
                    logging.info(f"TikTok WebSocket URL'si bulundu: {self.ws_url[:30]}...")
                    break
            
            # WebSocket URL'sini bul - Yöntem 2: WebCast URL
            if not self.ws_url:
                webcast_patterns = [
                    r'"webcastId":"([^"]+)"',
                    r'"webcast_id":"([^"]+)"',
                    r'webcastId=([^&"]+)',
                    r'webcast_id=([^&"]+)'
                ]
                
                for pattern in webcast_patterns:
                    webcast_match = re.search(pattern, html_content)
                    if webcast_match:
                        webcast_id = webcast_match.group(1)
                        self.ws_url = f"wss://webcast.tiktok.com/im/push/v2/?app_name=tiktok_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&device_platform=web&device_type=web&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=tr-TR&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F122.0.0.0+Safari%2F537.36&browser_online=true&tz_name=Europe%2FIstanbul&cursor=r-1&internal_ext=&webcast_language=tr-TR&msToken=&host=www.tiktok.com&aid=1988&live_id={webcast_id}&did=7318358362599261699&room_id={webcast_id}&signature=_02B4Z6wo00001bTdQIgAAIDAJJNOGtRFjPCQiPsAAHDY5c"
                        logging.info(f"TikTok WebCast URL'si oluşturuldu: {self.ws_url[:30]}...")
                        break
            
            # WebSocket URL'si veya Room ID bulunamadıysa
            if not self.ws_url and not self.room_id:
                logging.error("TikTok WebSocket URL'si ve Room ID bulunamadı")
                self.message_queue.put(("SISTEM", "TikTok WebSocket URL'si ve Room ID bulunamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
            
            # Room ID varsa ama WebSocket URL'si yoksa, varsayılan URL oluştur
            if self.room_id and not self.ws_url:
                # Farklı WebSocket URL formatları dene
                ws_urls = [
                    # Format 1: Standart WebCast URL
                    f"wss://webcast.tiktok.com/im/push/v2/?app_name=tiktok_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&device_platform=web&device_type=web&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=tr-TR&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F122.0.0.0+Safari%2F537.36&browser_online=true&tz_name=Europe%2FIstanbul&cursor=r-1&internal_ext=&webcast_language=tr-TR&msToken=&host=www.tiktok.com&aid=1988&live_id={self.room_id}&did=7318358362599261699&room_id={self.room_id}&signature=_02B4Z6wo00001bTdQIgAAIDAJJNOGtRFjPCQiPsAAHDY5c",
                    
                    # Format 2: Basitleştirilmiş WebCast URL
                    f"wss://webcast.tiktok.com/im/push/v2/?aid=1988&room_id={self.room_id}",
                    
                    # Format 3: Alternatif WebCast URL
                    f"wss://webcast16-normal-c-useast1a.tiktokv.com/webcast/im/push/v2/?app_name=tiktok_web&version_code=180800&live_id={self.room_id}&room_id={self.room_id}"
                ]
                
                # İlk URL'yi kullan, diğerlerini yedekle
                self.ws_url = ws_urls[0]
                self.backup_ws_urls = ws_urls[1:]
                logging.info(f"TikTok WebSocket URL'si oluşturuldu: {self.ws_url[:30]}... (+ {len(self.backup_ws_urls)} yedek URL)")
            
            return True
        except Exception as e:
            logging.error(f"TikTok WebSocket bilgileri çıkarılırken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok WebSocket bilgileri çıkarılırken hata: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
    
    def connect(self):
        """WebSocket bağlantısı kurar"""
        if not self.extract_websocket_info():
            return False
        
        try:
            # WebSocket bağlantısı için callback fonksiyonları
            def on_message(ws, message):
                try:
                    # Mesajı işle
                    self._process_message(message)
                    # Başarılı mesaj alındı, hata sayacını sıfırla
                    self.error_count = 0
                    self.retry_count = 0
                except Exception as e:
                    logging.error(f"WebSocket mesaj işleme hatası: {str(e)}")
            
            def on_error(ws, error):
                logging.error(f"WebSocket hatası: {str(error)}")
                self.error_count += 1
                
                # Hata çok fazlaysa yedek URL'ye geç
                if self.error_count >= self.max_errors and self.backup_ws_urls and self.current_url_index < len(self.backup_ws_urls):
                    self.current_url_index += 1
                    self.ws_url = self.backup_ws_urls[self.current_url_index - 1]
                    logging.info(f"Yedek WebSocket URL'sine geçiliyor: {self.ws_url[:30]}...")
                    self.message_queue.put(("SISTEM", "TikTok bağlantı hatası, alternatif bağlantı deneniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    self.error_count = 0
                    
                    # Mevcut bağlantıyı kapat ve yenisini oluştur
                    if self.ws:
                        self.ws.close()
                    self.connected = False
            
            def on_close(ws, close_status_code, close_msg):
                logging.info(f"WebSocket bağlantısı kapandı: {close_status_code} - {close_msg}")
                self.connected = False
                
                # Bağlantı kapandıysa ve yeniden deneme sayısı aşılmadıysa tekrar dene
                if not self.stop_event.is_set() and self.retry_count < self.max_retries:
                    self.retry_count += 1
                    logging.info(f"WebSocket bağlantısı yeniden deneniyor ({self.retry_count}/{self.max_retries})...")
                    self.message_queue.put(("SISTEM", f"TikTok bağlantısı yeniden deneniyor ({self.retry_count}/{self.max_retries})...", time.strftime("%H:%M:%S"), "TikTok"))
                    time.sleep(2)  # Kısa bir bekleme
                    self.connect()  # Yeniden bağlan
            
            def on_open(ws):
                logging.info("WebSocket bağlantısı açıldı")
                self.connected = True
                self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı kuruldu", time.strftime("%H:%M:%S"), "TikTok"))
                self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
                
                # Giriş mesajı gönder
                if self.room_id:
                    # Farklı giriş mesajı formatlarını dene
                    join_msgs = [
                        {
                            "type": "join",
                            "roomId": self.room_id
                        },
                        {
                            "cmd": "joinRoom",
                            "roomId": self.room_id
                        },
                        {
                            "type": "subscribe",
                            "room_id": self.room_id,
                            "live_id": self.room_id
                        }
                    ]
                    
                    # Tüm formatları dene
                    for join_msg in join_msgs:
                        try:
                            ws.send(json.dumps(join_msg))
                            time.sleep(0.5)  # Kısa bir bekleme
                        except Exception as e:
                            logging.error(f"Giriş mesajı gönderme hatası: {str(e)}")
            
            # WebSocket bağlantısını başlat
            logging.info(f"WebSocket bağlantısı kuruluyor: {self.ws_url[:30]}...")
            self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı kuruluyor...", time.strftime("%H:%M:%S"), "TikTok"))
            
            # Farklı header kombinasyonları
            headers = [
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Origin": "https://www.tiktok.com",
                    "Referer": self.url
                },
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Origin": "https://www.tiktok.com",
                    "Referer": self.url,
                    "Cookie": f"room_id={self.room_id}"
                }
            ]
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open,
                header=headers[0]
            )
            
            # WebSocket bağlantısını ayrı bir thread'de başlat
            wst = threading.Thread(target=self.ws.run_forever, kwargs={
                "sslopt": {"cert_reqs": ssl.CERT_NONE},
                "ping_interval": 30,
                "ping_timeout": 10,
                "skip_utf8_validation": True
            })
            wst.daemon = True
            wst.start()
            
            # Bağlantı kurulana kadar bekle
            wait_time = 0
            while not self.connected and wait_time < 20 and not self.stop_event.is_set():
                time.sleep(0.5)
                wait_time += 0.5
                logging.info(f"WebSocket bağlantısı bekleniyor... ({wait_time}s)")
            
            if not self.connected:
                logging.error("WebSocket bağlantısı kurulamadı")
                self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı kurulamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return False
            
            return True
        except Exception as e:
            logging.error(f"WebSocket bağlantısı kurulurken hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok WebSocket bağlantısı kurulurken hata: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
    
    def _process_message(self, message):
        """WebSocket mesajlarını işler"""
        try:
            # Mesaj içeriği debug için logla
            logging.debug(f"WebSocket mesajı alındı: {message[:200]}...")
            
            # Mesajı JSON olarak parse et
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                logging.warning(f"JSON parse hatası, mesaj: {message[:50]}...")
                return
            
            # Mesaj içeriğini debug için logla
            logging.debug(f"Parse edilmiş mesaj: {str(data)[:200]}...")
            
            # Bağlantı onay mesajı
            if "type" in data and data["type"] in ["connected", "connection", "welcome"]:
                logging.info("TikTok WebSocket bağlantısı onaylandı")
                self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı onaylandı", time.strftime("%H:%M:%S"), "TikTok"))
                return
            
            # Mesaj tipine göre işle - Format 1
            if "type" in data:
                if data["type"] in ["message", "chat", "comment"]:
                    if "user" in data and ("text" in data or "content" in data):
                        username = data["user"].get("uniqueId", data["user"].get("nickname", "Anonim"))
                        text = data.get("text", data.get("content", ""))
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put((username, text, current_time, "TikTok"))
                        self.last_message_time = time.time()
                        logging.info(f"TikTok mesajı alındı: {username}: {text}")
                        return
            
            # TikTok WebCast formatı - Format 2
            if "cmd" in data:
                if data["cmd"] in ["WebcastChatMessage", "ChatMessage", "Comment"]:
                    if "user" in data and ("content" in data or "comment" in data):
                        username = data["user"].get("uniqueId", data["user"].get("nickname", "Anonim"))
                        text = data.get("content", data.get("comment", ""))
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put((username, text, current_time, "TikTok"))
                        self.last_message_time = time.time()
                        logging.info(f"TikTok mesajı alındı: {username}: {text}")
                        return
            
            # Alternatif format - Format 3
            if "data" in data:
                if isinstance(data["data"], list):
                    for item in data["data"]:
                        if isinstance(item, dict) and "user" in item and ("text" in item or "content" in item or "comment" in item):
                            username = item["user"].get("uniqueId", item["user"].get("nickname", "Anonim"))
                            text = item.get("text", item.get("content", item.get("comment", "")))
                            current_time = time.strftime("%H:%M:%S")
                            self.message_queue.put((username, text, current_time, "TikTok"))
                            self.last_message_time = time.time()
                            logging.info(f"TikTok mesajı alındı: {username}: {text}")
                            return
                elif isinstance(data["data"], dict):
                    if "user" in data["data"] and ("text" in data["data"] or "content" in data["data"] or "comment" in data["data"]):
                        username = data["data"]["user"].get("uniqueId", data["data"]["user"].get("nickname", "Anonim"))
                        text = data["data"].get("text", data["data"].get("content", data["data"].get("comment", "")))
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put((username, text, current_time, "TikTok"))
                        self.last_message_time = time.time()
                        logging.info(f"TikTok mesajı alındı: {username}: {text}")
                        return
            
            # TikTok özel formatı - Format 4
            if "common" in data and "method" in data:
                if data["method"] == "WebcastChatMessage" and "payload" in data:
                    payload = data["payload"]
                    if isinstance(payload, list) and len(payload) > 0:
                        for item in payload:
                            if "user" in item and "content" in item:
                                username = item["user"].get("uniqueId", item["user"].get("nickname", "Anonim"))
                                text = item["content"]
                                current_time = time.strftime("%H:%M:%S")
                                self.message_queue.put((username, text, current_time, "TikTok"))
                                self.last_message_time = time.time()
                                logging.info(f"TikTok mesajı alındı: {username}: {text}")
                                return
            
            # TikTok özel formatı - Format 5 (mesajlar)
            if "messages" in data:
                messages = data["messages"]
                if isinstance(messages, list):
                    for msg in messages:
                        if isinstance(msg, dict) and "user" in msg and ("text" in msg or "content" in msg):
                            username = msg["user"].get("uniqueId", msg["user"].get("nickname", "Anonim"))
                            text = msg.get("text", msg.get("content", ""))
                            current_time = time.strftime("%H:%M:%S")
                            self.message_queue.put((username, text, current_time, "TikTok"))
                            self.last_message_time = time.time()
                            logging.info(f"TikTok mesajı alındı: {username}: {text}")
                            return
            
            # Hiçbir format eşleşmedi
            logging.debug(f"Bilinmeyen mesaj formatı: {str(data)[:200]}...")
        except Exception as e:
            logging.error(f"WebSocket mesajı işlenirken hata: {str(e)}")
    
    def run(self):
        """Ana çalışma metodu"""
        try:
            # WebSocket bağlantısı kur
            if not self.connect():
                return False
            
            # Bağlantı durumunu kontrol et
            while not self.stop_event.is_set() and self.connected:
                # Hata sayacı kontrolü
                if self.error_count >= self.max_errors:
                    logging.error("Çok fazla WebSocket hatası, yeniden bağlanılıyor")
                    self.message_queue.put(("SISTEM", "TikTok WebSocket hatası, yeniden bağlanılıyor", time.strftime("%H:%M:%S"), "TikTok"))
                    
                    # WebSocket bağlantısını kapat
                    if self.ws:
                        self.ws.close()
                    
                    # Yeniden bağlan
                    self.connected = False
                    self.error_count = 0
                    if not self.connect():
                        break
                
                # Belirli aralıklarla bildirim
                if time.time() - self.last_message_time > 30:
                    self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    self.last_message_time = time.time()
                
                # Kısa bir bekleme
                time.sleep(5)
            
            return True
        except Exception as e:
            logging.error(f"TikTok WebSocket genel hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok WebSocket hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
        finally:
            # Bağlantıyı kapat
            self.close()
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass


def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok WebSocket bağlantısını başlatır"""
    connector = TikTokWebSocketConnector(url, message_queue, stop_event)
    connector.run()


# Test ve debug
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = input("TikTok URL'si girin: ")
    
    queue = Queue()
    stop = threading.Event()
    
    connector = TikTokWebSocketConnector(url, queue, stop)
    threading.Thread(target=connector.run, daemon=True).start()
    
    try:
        while True:
            if not queue.empty():
                message = queue.get()
                print(f"{message[3]} | {message[2]} | {message[0]}: {message[1]}")
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        stop.set()
        print("Bağlantı kapatıldı.")
