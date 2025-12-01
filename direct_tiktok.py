"""
TikTok Doğrudan Bağlantı Modülü - Bypass yöntemi ile TikTok canlı chat bağlantısı kurar
"""

import requests
import json
import time
import logging
import threading
import re
from queue import Queue
import random
import websocket
import ssl
from urllib.parse import urlparse, parse_qs
import sys

# API güncel bilgileri
API_PARAMS = {
    "aid": "1988",
    "app_language": "tr-TR",
    "app_name": "tiktok_web",
    "browser_language": "tr-TR",
    "browser_name": "Mozilla",
    "browser_online": True,
    "browser_platform": "Win32",
    "browser_version": "5.0 (Windows NT 10.0; Win64; x64)",
    "cookie_enabled": True,
    "device_id": str(int(time.time() * 1000)),
    "device_platform": "web",
    "focus_state": True,
    "from_page": "user",
    "history_len": random.randint(1, 5),
    "is_fullscreen": False,
    "is_page_visible": True,
    "os": "windows",
    "priority_region": "TR",
    "referer": "",
    "region": "TR",
    "screen_height": 1080,
    "screen_width": 1920,
    "tz_name": "Europe/Istanbul",
    "webcast_language": "tr-TR",
}

class TikTokDirectConnector:
    """TikTok Live Chat için doğrudan bağlantı sağlayan sınıf"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.room_id = None
        self.room_info = {}
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Origin": "https://www.tiktok.com",
            "Referer": "https://www.tiktok.com/",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        self.last_message_time = time.time()
        self.cursor = "0"
        self.ms_token = ""
        self.device_id = f"{int(time.time() * 1000)}"
        self.internal_ext = ""
        self.connected = False
        self.error_count = 0
        self.max_errors = 10
        
    def _generate_id(self):
        """Benzersiz ID oluşturur"""
        return f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    
    def _generate_signature(self, url):
        """TikTok API imza algoritması basitleştirilmiş hali - gerçek projede gerekirse"""
        timestamp = int(time.time())
        unique_id = f"verify_{timestamp}"
        return unique_id
    
    def extract_username_and_room(self):
        """URL'den kullanıcı adını ve oda bilgilerini çıkartır"""
        if not self.url:
            return None, None
        
        # URL'den username çıkart
        try:
            username = None
            if "@" in self.url:
                username_match = re.search(r"@([A-Za-z0-9_.]+)", self.url)
                if username_match:
                    username = username_match.group(1)
            elif "/user/" in self.url:
                username_match = re.search(r"/user/([A-Za-z0-9_.]+)", self.url)
                if username_match:
                    username = username_match.group(1)
                
            if not username:
                logging.error(f"TikTok URL'sinden kullanıcı adı çıkarılamadı: {self.url}")
                self.message_queue.put(("SISTEM", f"TikTok URL'sinden kullanıcı adı çıkarılamadı", time.strftime("%H:%M:%S"), "TikTok"))
                return None, None
            
            # 1. YÖNTEM: Doğrudan HTML sayfasından Room ID çıkartma
            try:
                logging.info(f"TikTok canlı yayın sayfası açılıyor: {self.url}")
                response = self.session.get(self.url, timeout=15)
                
                if response.status_code == 200:
                    html_content = response.text
                    
                    # HTML içinden room ID'yi bul
                    room_id_match = re.search(r'"roomId":"(\d+)"', html_content)
                    if room_id_match:
                        room_id = room_id_match.group(1)
                        logging.info(f"TikTok Room ID HTML'den bulundu: {room_id}")
                        
                        # Ek bilgileri de çek
                        title_match = re.search(r'"title":"([^"]+)"', html_content)
                        if title_match:
                            title = title_match.group(1)
                            self.room_info["title"] = title
                            
                        return username, room_id
                    else:
                        logging.warning("TikTok HTML'de Room ID bulunamadı, alternatif yöntem deneniyor...")
                else:
                    logging.warning(f"TikTok sayfasına erişilemedi: {response.status_code}, alternatif yöntem deneniyor...")
            except Exception as e:
                logging.error(f"TikTok HTML çözümleme hatası: {str(e)}")
                
            # 2. YÖNTEM: API ile Room ID alma
            try:
                # Room ID almak için API çağrısı yap
                params = {
                    "aid": "1988",
                    "app_name": "tiktok_web",
                    "device_platform": "web",
                    "uniqueId": username,
                    "secUid": "",
                    "msToken": self.ms_token,
                    "device_id": self.device_id,
                }
                
                # Farklı API URL'leri dene
                api_urls = [
                    "https://www.tiktok.com/api/live/detail/",
                    "https://www.tiktok.com/api/user/detail/",
                    "https://www.tiktok.com/api/live/user/online/"
                ]
                
                for api_url in api_urls:
                    try:
                        logging.info(f"TikTok API deneniyor: {api_url}")
                        response = self.session.get(api_url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Farklı API yanıt formatlarını kontrol et
                            if "LiveRoomInfo" in data and data["LiveRoomInfo"].get("roomId"):
                                room_id = data["LiveRoomInfo"]["roomId"]
                                self.room_info = data.get("LiveRoomInfo", {})
                                logging.info(f"TikTok oda bilgileri bulundu (API 1): {username}, Room ID: {room_id}")
                                return username, room_id
                                
                            elif "liveRoom" in data and data["liveRoom"].get("roomId"):
                                room_id = data["liveRoom"]["roomId"]
                                self.room_info = data.get("liveRoom", {})
                                logging.info(f"TikTok oda bilgileri bulundu (API 2): {username}, Room ID: {room_id}")
                                return username, room_id
                                
                            elif "userInfo" in data and data["userInfo"].get("user") and data["userInfo"]["user"].get("roomId"):
                                room_id = data["userInfo"]["user"]["roomId"]
                                self.room_info = {"title": data["userInfo"]["user"].get("nickname", "")}
                                logging.info(f"TikTok oda bilgileri bulundu (API 3): {username}, Room ID: {room_id}")
                                return username, room_id
                                
                            elif "data" in data and "roomId" in str(data):
                                # JSON içinde roomId değerini ara
                                json_str = json.dumps(data)
                                room_match = re.search(r'"roomId":"?(\d+)"?', json_str)
                                if room_match:
                                    room_id = room_match.group(1)
                                    logging.info(f"TikTok oda bilgileri JSON'dan çıkarıldı: {username}, Room ID: {room_id}")
                                    return username, room_id
                    except Exception as api_err:
                        logging.error(f"TikTok API hatası ({api_url}): {str(api_err)}")
                        continue
                
                # Hiçbir API çalışmadıysa, son bir deneme yap
                try:
                    # Doğrudan canlı yayın URL'sine erişmeyi dene
                    live_url = f"https://www.tiktok.com/@{username}/live"
                    response = self.session.get(live_url, timeout=10)
                    
                    if response.status_code == 200:
                        html_content = response.text
                        room_id_match = re.search(r'"roomId":"(\d+)"', html_content)
                        if room_id_match:
                            room_id = room_id_match.group(1)
                            logging.info(f"TikTok Room ID son deneme ile bulundu: {room_id}")
                            return username, room_id
                except Exception as e:
                    logging.error(f"TikTok son deneme hatası: {str(e)}")
                
                # Hala bulunamadıysa, kullanıcıya bildir
                logging.error(f"TikTok Room ID bulunamadı: {username}")
                self.message_queue.put(("SISTEM", f"TikTok canlı yayın bulunamadı: @{username}", time.strftime("%H:%M:%S"), "TikTok"))
            except Exception as e:
                logging.error(f"TikTok kullanıcı bilgilerini alırken hata: {str(e)}")
                self.message_queue.put(("SISTEM", f"TikTok bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
        except Exception as e:
            logging.error(f"TikTok kullanıcı bilgilerini alırken genel hata: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
        
        return None, None
    
    def get_chat_messages(self):
        """Sürekli olarak mesajları çeker"""
        if not self.room_id:
            username, room_id = self.extract_username_and_room()
            if room_id:
                self.room_id = room_id
            else:
                self.message_queue.put(("SISTEM", "TikTok Room ID bulunamadı, bağlantı kurulamıyor", time.strftime("%H:%M:%S"), "TikTok"))
                return False
        
        # Başarılı bağlantı
        self.connected = True
        self.message_queue.put(("SISTEM", f"TikTok canlı yayın bulundu, chat bağlantısı kuruluyor (Room ID: {self.room_id})", time.strftime("%H:%M:%S"), "TikTok"))
        self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
        
        # Mesaj çekme döngüsü
        while not self.stop_event.is_set():
            try:
                if self.error_count >= self.max_errors:
                    self.message_queue.put(("SISTEM", f"Çok fazla TikTok bağlantı hatası oluştu ({self.error_count}), bağlantı sonlandırılıyor", time.strftime("%H:%M:%S"), "TikTok"))
                    break
                
                # 1. YÖNTEM: WebCast API ile chat mesajlarını al
                try:
                    # Chat API bağlantısı
                    chat_params = {
                        "roomID": self.room_id,
                        "cursor": self.cursor,
                        "count": 50,
                        "aid": "1988",
                        "app_language": "tr-TR",
                        "device_platform": "web",
                        "webcast_language": "tr-TR",
                        "device_id": self.device_id,
                        "_signature": self._generate_signature(self.url),
                    }
                    
                    # Farklı API endpoint'lerini dene
                    api_endpoints = [
                        "https://www.tiktok.com/api/live/chat/item/list/",
                        "https://webcast.tiktok.com/webcast/chat/",
                        "https://m.tiktok.com/api/live/chat/item/list/"
                    ]
                    
                    success = False
                    for endpoint in api_endpoints:
                        try:
                            headers = {
                                "User-Agent": self.user_agent,
                                "Referer": self.url,
                                "Origin": "https://www.tiktok.com"
                            }
                            
                            response = self.session.get(endpoint, params=chat_params, headers=headers, timeout=10)
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    
                                    # Cursor güncelleme
                                    if "cursor" in data:
                                        self.cursor = data["cursor"]
                                    
                                    # Mesaj işleme
                                    if "data" in data and "messages" in data["data"]:
                                        messages = data["data"]["messages"]
                                        for msg in messages:
                                            if "content" in msg and "user" in msg:
                                                author = msg["user"].get("uniqueId", "Anonim")
                                                text = msg["content"]
                                                current_time = time.strftime("%H:%M:%S")
                                                self.message_queue.put((author, text, current_time, "TikTok"))
                                                self.last_message_time = time.time()
                                        
                                        if messages:
                                            self.error_count = 0  # Başarılı istek, hata sayacını sıfırla
                                            success = True
                                            break  # Başarılı olduğunda diğer endpoint'leri deneme
                                except Exception as e:
                                    logging.error(f"TikTok mesaj çözümleme hatası ({endpoint}): {str(e)}")
                                    continue
                            elif response.status_code == 400:
                                logging.error(f"TikTok API 400 hatası ({endpoint}): Muhtemelen yanlış Room ID veya canlı yayın sona erdi")
                                self.message_queue.put(("SISTEM", "TikTok API yanıt vermedi: 400 (Canlı yayın bitmiş olabilir)", time.strftime("%H:%M:%S"), "TikTok"))
                            elif response.status_code == 429:
                                logging.error(f"TikTok API rate limit aşıldı ({endpoint}): 429")
                                self.message_queue.put(("SISTEM", "TikTok API rate limit aşıldı, bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                                time.sleep(10)  # Rate limit durumunda daha uzun bekle
                            else:
                                logging.error(f"TikTok chat API hata kodu ({endpoint}): {response.status_code}")
                        except Exception as req_err:
                            logging.error(f"TikTok API istek hatası ({endpoint}): {str(req_err)}")
                            continue
                    
                    if not success:
                        # Hiçbir API çalışmadıysa, Room ID'yi yeniden almayı dene
                        self.error_count += 1
                        if self.error_count % 5 == 0:  # Her 5 hatada bir Room ID'yi yenile
                            logging.info("TikTok Room ID yenileniyor...")
                            username, room_id = self.extract_username_and_room()
                            if room_id and room_id != self.room_id:
                                self.room_id = room_id
                                self.cursor = "0"  # Cursor'ı sıfırla
                                self.message_queue.put(("SISTEM", f"TikTok Room ID yenilendi: {self.room_id}", time.strftime("%H:%M:%S"), "TikTok"))
                                self.error_count = 0  # Hata sayacını sıfırla
                
                # 2. YÖNTEM: Canlı yayın sayfasından HTML çözümleme
                except Exception as api_err:
                    logging.error(f"TikTok API genel hatası: {str(api_err)}")
                    self.error_count += 1
                    
                    # HTML sayfasını yeniden yükle ve mesajları çıkart
                    try:
                        if self.error_count % 3 == 0:  # Her 3 hatada bir HTML'den çekmeyi dene
                            logging.info("TikTok canlı yayın HTML sayfasından mesajlar çekiliyor...")
                            response = self.session.get(self.url, timeout=15)
                            
                            if response.status_code == 200:
                                html_content = response.text
                                
                                # HTML içinden mesajları çıkart
                                chat_messages = re.findall(r'"uniqueId":"([^"]+)","nickname":"[^"]+","text":"([^"]+)"', html_content)
                                for author, text in chat_messages:
                                    current_time = time.strftime("%H:%M:%S")
                                    self.message_queue.put((author, text, current_time, "TikTok"))
                                    self.last_message_time = time.time()
                                
                                if chat_messages:
                                    logging.info(f"TikTok HTML'den {len(chat_messages)} mesaj çekildi")
                                    self.error_count = 0  # Başarılı olduğunda hata sayacını sıfırla
                    except Exception as html_err:
                        logging.error(f"TikTok HTML mesaj çekme hatası: {str(html_err)}")
                
                # Son mesaj kontrolü - uzun süre mesaj gelmemişse bilgi ver
                if time.time() - self.last_message_time > 60:
                    self.message_queue.put(("SISTEM", "TikTok bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    self.last_message_time = time.time()
                    
                    # 60 saniyedir mesaj yoksa Room ID'yi kontrol et
                    username, room_id = self.extract_username_and_room()
                    if room_id and room_id != self.room_id:
                        self.room_id = room_id
                        self.cursor = "0"
                        self.message_queue.put(("SISTEM", f"TikTok Room ID güncellendi: {self.room_id}", time.strftime("%H:%M:%S"), "TikTok"))
                
                # İstek sıklığını düzenle
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"TikTok chat bağlantısı hatası: {str(e)}")
                self.error_count += 1
                time.sleep(5)
        
        # Bağlantı sonlandırıldı
        self.connected = False
        return True
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.connected = False
        self.stop_event.set()
    
    def run(self):
        """Ana çalışma metodu"""
        success = self.get_chat_messages()
        if not success:
            self.message_queue.put(("SISTEM", "TikTok canlı yayın bulunamadı veya erişilemiyor", time.strftime("%H:%M:%S"), "TikTok"))
            self.message_queue.put(("__STATUS__", "connection_error_bağlantı_hatası", "red", "TikTok"))
        self.close()


class YouTubeDirectConnector:
    """YouTube Live Chat için doğrudan bağlantı sağlayan sınıf"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.video_id = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        self.continuation = None
        self.last_message_time = time.time()
        self.connected = False
        self.error_count = 0
        self.max_errors = 10
    
    def extract_video_id(self):
        """URL'den video ID çıkartır"""
        if not self.url:
            return None
        
        try:
            video_id = None
            
            # URL formatına göre video ID çıkart
            if "youtube.com/watch" in self.url:
                query = parse_qs(urlparse(self.url).query)
                video_id = query.get("v", [None])[0]
            elif "youtu.be/" in self.url:
                video_id = self.url.split("youtu.be/")[1].split("?")[0]
            elif "youtube.com/channel" in self.url or "youtube.com/c/" in self.url or "youtube.com/@" in self.url:
                # Kanal URL'si, canlı yayın ID'sini bul
                response = self.session.get(self.url, timeout=10)
                if response.status_code == 200:
                    # Video ID'yi HTML içinden çıkart
                    matches = re.findall(r"\"videoId\":\"([^\"]+)\"", response.text)
                    if matches:
                        for potential_id in matches:
                            # Canlı yayın kontrolü yap
                            live_check_url = f"https://www.youtube.com/watch?v={potential_id}"
                            live_response = self.session.get(live_check_url, timeout=10)
                            if "isLive\":true" in live_response.text:
                                video_id = potential_id
                                break
            
            if not video_id:
                logging.error(f"YouTube URL'sinden video ID çıkarılamadı: {self.url}")
                self.message_queue.put(("SISTEM", f"YouTube URL'sinden video ID çıkarılamadı", time.strftime("%H:%M:%S"), "YouTube"))
                return None
            
            logging.info(f"YouTube video ID: {video_id}")
            return video_id
        except Exception as e:
            logging.error(f"YouTube video ID çıkarma hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"YouTube bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
        
        return None
    
    def get_initial_continuation(self):
        """İlk continuation token'ını alır"""
        if not self.video_id:
            return None
        
        try:
            # YouTube video sayfasını açarak continuation token al
            watch_url = f"https://www.youtube.com/watch?v={self.video_id}"
            response = self.session.get(watch_url, timeout=10)
            
            if response.status_code == 200:
                # Continuation token'ı HTML içinden çıkart
                # İlk olarak ytInitialData'yı bul
                yt_initial_data = re.search(r"ytInitialData\s*=\s*({.+?});", response.text)
                if yt_initial_data:
                    data_str = yt_initial_data.group(1)
                    try:
                        data = json.loads(data_str)
                        # Livechat continuation token'ını bul
                        if "contents" in data and "twoColumnWatchNextResults" in data["contents"]:
                            results = data["contents"]["twoColumnWatchNextResults"]
                            if "conversationBar" in results and "liveChatRenderer" in results["conversationBar"]:
                                continuation = results["conversationBar"]["liveChatRenderer"]["continuations"][0]["reloadContinuationData"]["continuation"]
                                return continuation
                    except json.JSONDecodeError:
                        pass
            
            logging.error("YouTube continuation token bulunamadı")
            return None
        except Exception as e:
            logging.error(f"YouTube continuation token alma hatası: {str(e)}")
            return None
    
    def get_chat_messages(self):
        """Sürekli olarak mesajları çeker"""
        if not self.video_id:
            self.video_id = self.extract_video_id()
            if not self.video_id:
                self.message_queue.put(("SISTEM", "YouTube video ID bulunamadı, bağlantı kurulamıyor", time.strftime("%H:%M:%S"), "YouTube"))
                return False
        
        # İlk continuation token'ı al
        self.continuation = self.get_initial_continuation()
        if not self.continuation:
            self.message_queue.put(("SISTEM", "YouTube chat bağlantısı kurulamadı, token alınamadı", time.strftime("%H:%M:%S"), "YouTube"))
            return False
        
        # Başarılı bağlantı
        self.connected = True
        self.message_queue.put(("SISTEM", f"YouTube canlı yayın bulundu, chat bağlantısı kuruldu", time.strftime("%H:%M:%S"), "YouTube"))
        self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
        
        # Mesaj çekme döngüsü
        while not self.stop_event.is_set():
            try:
                if self.error_count >= self.max_errors:
                    self.message_queue.put(("SISTEM", f"Çok fazla YouTube bağlantı hatası oluştu ({self.error_count}), bağlantı sonlandırılıyor", time.strftime("%H:%M:%S"), "YouTube"))
                    break
                
                # Chat API bağlantısı
                chat_params = {
                    "continuation": self.continuation,
                    "pbj": "1",
                    "ctoken": self.continuation,
                }
                
                response = self.session.get("https://www.youtube.com/live_chat", params=chat_params, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = json.loads(response.text)
                        
                        # Bir sonraki continuation token'ını al
                        if "continuationContents" in data[1]["response"]:
                            contents = data[1]["response"]["continuationContents"]
                            if "liveChatContinuation" in contents:
                                continuations = contents["liveChatContinuation"]["continuations"]
                                if continuations and "invalidationContinuationData" in continuations[0]:
                                    self.continuation = continuations[0]["invalidationContinuationData"]["continuation"]
                                
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
                    
                    if response.status_code == 429:
                        self.message_queue.put(("SISTEM", "YouTube API rate limit aşıldı, bekleniyor...", time.strftime("%H:%M:%S"), "YouTube"))
                        time.sleep(10)  # Rate limit durumunda daha uzun bekle
                    else:
                        time.sleep(5)
                
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
        
        # Bağlantı sonlandırıldı
        self.connected = False
        return True
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.connected = False
        self.stop_event.set()
    
    def run(self):
        """Ana çalışma metodu"""
        success = self.get_chat_messages()
        if not success:
            self.message_queue.put(("SISTEM", "YouTube canlı yayın bulunamadı veya erişilemiyor", time.strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_error_bağlantı_hatası", "red", "YouTube"))
        self.close()


def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok chat bağlantısını başlatır"""
    connector = TikTokDirectConnector(url, message_queue, stop_event)
    connector.run()


def start_youtube_chat(url, message_queue=None, stop_event=None):
    """YouTube chat bağlantısını başlatır"""
    connector = YouTubeDirectConnector(url, message_queue, stop_event)
    connector.run()


# Test ve debug
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = input("TikTok veya YouTube URL'si girin: ")
    
    queue = Queue()
    stop = threading.Event()
    
    if "tiktok" in url.lower():
        threading.Thread(target=start_tiktok_chat, args=(url, queue, stop)).start()
    elif "youtube" in url.lower() or "youtu.be" in url.lower():
        threading.Thread(target=start_youtube_chat, args=(url, queue, stop)).start()
    else:
        print("Geçersiz URL. TikTok veya YouTube URL'si olmalıdır.")
        sys.exit(1)
    
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
