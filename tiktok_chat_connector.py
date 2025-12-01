"""
TikTok Chat Connector - TikTok canlı yayın chatlerini çekmek için gelişmiş bir çözüm
Bu modül, chat-downloader çalışmadığında kullanılabilecek alternatif bir TikTok chat bağlantı çözümü sağlar.
"""

import os
import sys
import json
import time
import logging
import threading
import re
from queue import Queue
import random
import websocket
import ssl
import requests
import socket
import json
from urllib.parse import urlparse, parse_qs

# Playwright ve diğer bağımlılıkları kontrol ediyoruz
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright kütüphanesi yüklü değil. TikTok cookie çözümü devre dışı.")

try:
    import pyjwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

class TikTokChatConnector:
    def __init__(self, url, message_queue=None, stop_event=None):
        """
        TikTok canlı yayın chati için alternatif bir bağlantı sağlar.
        
        Args:
            url (str): TikTok canlı yayın URL'si
            message_queue (Queue): Mesaj kuyruğu
            stop_event (threading.Event): Durdurma eventi
        """
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.room_id = None
        self.websocket = None
        self.connected = False
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.last_message_time = time.time()
        self.cookies = {}
        self.ws_url = None
        self.retry_count = 0
        self.max_retries = 5
        
    def extract_username(self):
        """URL'den kullanıcı adını çıkarır."""
        try:
            if '@' in self.url:
                match = re.search(r'@([^/]+)', self.url)
                if match:
                    return match.group(1)
            # Farklı URL formatları için
            parsed_url = urlparse(self.url)
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                if part.startswith('@'):
                    return part[1:]
            
            logging.error(f"TikTok URL'sinden kullanıcı adı çıkarılamadı: {self.url}")
            return None
        except Exception as e:
            logging.error(f"Kullanıcı adı çıkarma hatası: {e}")
            return None
    
    def get_tiktok_cookies(self):
        """Playwright kullanarak TikTok cookie'lerini alır."""
        if not PLAYWRIGHT_AVAILABLE:
            logging.error("Playwright yüklü değil. Cookie alma işlemi yapılamıyor.")
            return {}
            
        logging.info("Playwright ile TikTok oturumu açılıyor...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True, 
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-extensions',
                        '--disable-component-extensions-with-background-pages',
                        '--disable-default-apps',
                        '--no-default-browser-check',
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                )
                
                page = context.new_page()
                
                # TikTok botları tespit eden JS kodlarını manipüle et
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.navigator.chrome = { runtime: {} };
                """)
                
                # TikTok canlı yayın sayfasına git
                logging.info(f"TikTok URL'sine gidiliyor: {self.url}")
                page.goto(self.url, wait_until='networkidle', timeout=15000)
                
                # WebSocket URL'sini yakalamaya çalış
                try:
                    self.ws_url = page.evaluate('''
                        () => {
                            for (let s of document.scripts) {
                                let m = s.textContent.match(/"wss:\\/\\/webcast[^"]+"/);
                                if (m) return JSON.parse(m[0]);
                            }
                            return "";
                        }
                    ''')
                    logging.info(f"WebSocket URL bulundu: {self.ws_url[:50]}...")
                except Exception as e:
                    logging.error(f"WebSocket URL çıkarma hatası: {e}")
                
                # Room ID'yi bulmayı dene
                try:
                    self.room_id = page.evaluate('''
                        () => {
                            try {
                                return window.ROOM_ID || document.querySelector('[data-e2e="room-id"]')?.textContent;
                            } catch (e) {
                                return "";
                            }
                        }
                    ''')
                    if not self.room_id:
                        # HTML içinde room_id arayalım
                        html_content = page.content()
                        room_id_match = re.search(r'"roomId":"(\d+)"', html_content)
                        if room_id_match:
                            self.room_id = room_id_match.group(1)
                    
                    logging.info(f"Room ID: {self.room_id}")
                except Exception as e:
                    logging.error(f"Room ID çıkarma hatası: {e}")
                
                # Cookie'leri al
                cookies = {}
                for c in context.cookies():
                    cookies[c['name']] = c['value']
                
                # x-tt-params değerini bul
                try:
                    # Sayfadan x-tt-params çıkarmaya çalış
                    x_tt_params = page.evaluate('''
                        () => {
                            try {
                                for (let s of document.scripts) {
                                    if (s.textContent.includes('x-tt-params')) {
                                        let m = s.textContent.match(/["']x-tt-params["']\s*:\s*["']([^"']+)["']/);
                                        if (m) return m[1];
                                    }
                                }
                            } catch (e) {}
                            return "";
                        }
                    ''')
                    
                    if x_tt_params:
                        cookies["x-tt-params"] = x_tt_params
                except Exception as e:
                    logging.error(f"x-tt-params çıkarma hatası: {e}")
                
                browser.close()
                return cookies
                
        except Exception as e:
            logging.error(f"Cookie alma işleminde hata: {e}")
            return {}

    def extract_room_id(self):
        """TikTok URL'sinden room_id çıkartır."""
        try:
            # URL'den kullanıcı adını çıkar
            username = self.extract_username()
            if not username:
                return None
            
            # AJAX isteği ile canlı yayın ID'sini al
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Origin': 'https://www.tiktok.com',
                'Referer': f'https://www.tiktok.com/@{username}/live',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin'
            }
            
            # Cookie'leri header'a ekle
            for name, value in self.cookies.items():
                if name.lower() not in ['x-tt-params', 'user-agent', 'referer', 'origin']:
                    headers[name] = value
            
            # TikTok live API isteği
            api_url = f'https://www.tiktok.com/api/live/detail/?aid=1988&uniqueId={username}'
            
            response = requests.get(
                api_url, 
                headers=headers, 
                cookies=self.cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'liveRoom' in data:
                    room_id = data['liveRoom'].get('roomId')
                    if room_id:
                        logging.info(f"TikTok room_id API'den bulundu: {room_id}")
                        return room_id
            
            logging.error(f"TikTok room_id bulunamadı. API yanıtı: {response.text[:200]}...")
            return self.room_id  # Playwright'ten aldıysak onu kullan
        
        except Exception as e:
            logging.error(f"TikTok room_id çıkarma hatası: {e}")
            return self.room_id  # Playwright'ten aldıysak onu kullan

    def connect_websocket(self):
        """WebSocket URL'sine bağlanır."""
        if not self.ws_url:
            logging.error("WebSocket URL bulunamadı")
            return False
            
        try:
            logging.info(f"WebSocket bağlantısı kuruluyor: {self.ws_url[:50]}...")
            
            # WebSocket bağlantısı
            def on_message(ws, message):
                try:
                    msg_data = json.loads(message)
                    if 'msg' in msg_data:
                        author = msg_data.get('nickname', 'Anonim')
                        text = msg_data['msg']
                        self.last_message_time = time.time()
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put((author, text, current_time, "TikTok"))
                except Exception as e:
                    logging.error(f"WebSocket mesaj işleme hatası: {e}")
            
            def on_error(ws, error):
                logging.error(f"WebSocket hatası: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logging.info(f"WebSocket bağlantısı kapandı: {close_status_code} - {close_msg}")
            
            def on_open(ws):
                logging.info("WebSocket bağlantısı açıldı!")
                self.message_queue.put(("SISTEM", "TikTok WebSocket bağlantısı kuruldu", time.strftime("%H:%M:%S"), "TikTok"))
            
            # WebSocket bağlantısını oluştur
            self.websocket = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open,
                header={
                    'User-Agent': self.user_agent,
                    'Origin': 'https://www.tiktok.com',
                }
            )
            
            # WebSocket thread'ini başlat
            wst = threading.Thread(target=self.websocket.run_forever, kwargs={
                'sslopt': {"cert_reqs": ssl.CERT_NONE},
                'ping_interval': 30,
                'ping_timeout': 10
            })
            wst.daemon = True
            wst.start()
            
            return True
            
        except Exception as e:
            logging.error(f"WebSocket bağlantı hatası: {e}")
            return False

    def connect(self):
        """TikTok canlı yayın chatine bağlanır."""
        try:
            # Ekranı bilgilendir
            self.message_queue.put(("__STATUS__", "connection_connecting", "yellow", "TikTok"))
            self.message_queue.put(("SISTEM", "TikTok bağlantısı kuruluyor...", time.strftime("%H:%M:%S"), "TikTok"))
            
            # Playwright ile cookie ve WebSocket URL al
            if PLAYWRIGHT_AVAILABLE:
                self.cookies = self.get_tiktok_cookies()
                if self.cookies:
                    self.message_queue.put(("SISTEM", "TikTok oturum bilgileri alındı", time.strftime("%H:%M:%S"), "TikTok"))
                else:
                    self.message_queue.put(("SISTEM", "TikTok oturum bilgileri alınamadı, misafir modunda devam ediliyor", time.strftime("%H:%M:%S"), "TikTok"))
            
            # Room ID bulamadıysak API'den almaya çalış
            if not self.room_id:
                self.room_id = self.extract_room_id()
                
            if self.room_id:
                self.message_queue.put(("SISTEM", f"TikTok Room ID: {self.room_id}", time.strftime("%H:%M:%S"), "TikTok"))
            else:
                self.message_queue.put(("__STATUS__", "connection_error_room_id_bulunamadı", "red", "TikTok"))
                return False
            
            # WebSocket bağlantısı
            if self.ws_url and self.connect_websocket():
                self.connected = True
                self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
                return True
            
            # Başarılı bağlantı
            self.connected = True
            self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
            return True
            
        except Exception as e:
            logging.error(f"TikTok chat bağlantı hatası: {e}")
            self.message_queue.put(("__STATUS__", "connection_error_bağlantı_hatası", "red", "TikTok"))
            return False

    def get_chat_messages(self):
        """Mesajları periyodik olarak alır."""
        if not self.room_id and not self.ws_url:
            return
        
        self.message_queue.put(("SISTEM", "TikTok mesajları alınıyor...", time.strftime("%H:%M:%S"), "TikTok"))
        
        # WebSocket çalışmıyorsa, HTTP polling yapalım
        if not self.ws_url or not hasattr(self, 'websocket') or not self.websocket:
            self._http_polling()
        else:
            # WebSocket aktif, sadece bekle
            while not self.stop_event.is_set():
                time.sleep(1)
                
                # Uzun süre mesaj gelmemişse uyar
                if time.time() - self.last_message_time > 60:
                    self.message_queue.put(("SISTEM", "TikTok bağlantısı aktif, ancak 60 saniyedir mesaj yok", time.strftime("%H:%M:%S"), "TikTok"))
                    self.last_message_time = time.time()  # Sıfırla

    def _http_polling(self):
        """WebSocket bağlantısı olmadığında HTTP polling yapar."""
        if not self.room_id:
            self.message_queue.put(("SISTEM", "TikTok Room ID bulunamadığından chat alınamıyor", time.strftime("%H:%M:%S"), "TikTok"))
            return
            
        # TikTok HTTP API ile polling
        poll_url = f"https://www.tiktok.com/api/live/chat/item/list/?aid=1988&roomID={self.room_id}"
        cursor = 0
        retry_count = 0
        
        self.message_queue.put(("SISTEM", f"TikTok chat akışı başlatıldı (Room ID: {self.room_id})", time.strftime("%H:%M:%S"), "TikTok"))
        
        while not self.stop_event.is_set():
            try:
                # TikTok HTTP API'si ile mesaj alma
                headers = {
                    "User-Agent": self.user_agent,
                    "Referer": self.url,
                    "Origin": "https://www.tiktok.com"
                }
                
                # Cookie'leri ekle
                cookies = {k: v for k, v in self.cookies.items() if k not in ["x-tt-params"]}
                
                response = requests.get(
                    f"{poll_url}&cursor={cursor}",
                    headers=headers,
                    cookies=cookies,
                    timeout=5
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("data") and data["data"].get("messages"):
                            messages = data["data"]["messages"]
                            for msg in messages:
                                if msg.get("user") and msg.get("content"):
                                    author = msg["user"].get("uniqueId", "Anonim")
                                    text = msg["content"]
                                    current_time = time.strftime("%H:%M:%S")
                                    self.message_queue.put((author, text, current_time, "TikTok"))
                                    self.last_message_time = time.time()
                            
                            # Cursor güncelle
                            if data["data"].get("cursor"):
                                cursor = data["data"]["cursor"]
                            
                            # Başarılı istek, retry sayacını sıfırla
                            retry_count = 0
                        else:
                            # Boş mesaj listesi
                            time.sleep(2)
                    except Exception as json_err:
                        logging.error(f"TikTok API yanıt çözümleme hatası: {json_err}")
                        time.sleep(2)
                else:
                    retry_count += 1
                    if retry_count >= 5:
                        self.message_queue.put(("SISTEM", f"TikTok API hatası: {response.status_code}", time.strftime("%H:%M:%S"), "TikTok"))
                        time.sleep(10)
                        retry_count = 0
                    else:
                        time.sleep(5)
                
                # Son mesaj alındıktan uzun süre geçtiyse bilgi ver
                if time.time() - self.last_message_time > 60:
                    self.message_queue.put(("SISTEM", "TikTok bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    self.last_message_time = time.time()
                
                # CPU kullanımını azaltmak için kısa bir uyku
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"TikTok mesaj alma hatası: {e}")
                time.sleep(5)  # Hata durumunda biraz bekle

    def close(self):
        """Bağlantıyı kapatır."""
        try:
            if hasattr(self, 'websocket') and self.websocket:
                self.websocket.close()
                
            self.connected = False
            logging.info("TikTok bağlantısı kapatıldı")
        except Exception as e:
            logging.error(f"TikTok bağlantı kapatma hatası: {e}")

    def run(self):
        """Ana çalıştırma metodu."""
        success = False
        while self.retry_count < self.max_retries and not self.stop_event.is_set():
            if self.connect():
                success = True
                break
            else:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    wait_time = min(5 * self.retry_count, 30)
                    self.message_queue.put(("SISTEM", f"TikTok bağlantısı başarısız, {wait_time} saniye sonra yeniden deneniyor ({self.retry_count}/{self.max_retries})", time.strftime("%H:%M:%S"), "TikTok"))
                    time.sleep(wait_time)
        
        if success:
            self.message_queue.put(("SISTEM", "TikTok bağlantısı kuruldu, chat mesajları alınıyor", time.strftime("%H:%M:%S"), "TikTok"))
            self.get_chat_messages()
        else:
            self.message_queue.put(("SISTEM", "TikTok chat bağlantısı kurulamadı, daha fazla deneme yapılmayacak", time.strftime("%H:%M:%S"), "TikTok"))
            logging.error("TikTok chat bağlantısı kurulamadı")
        
        self.close()

def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok chat bağlantısını başlatır."""
    connector = TikTokChatConnector(url, message_queue, stop_event)
    connector.run()