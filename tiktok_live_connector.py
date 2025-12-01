"""
TikTok Live Chat Connector
API olmadan doğrudan TikTok canlı yayın sohbetine bağlanır
TikTokLive kütüphanesini kullanır
"""

import asyncio
import logging
import time
import threading
import traceback
from queue import Queue
from TikTokLive import TikTokLiveClient

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TikTokLiveConnector:
    """TikTok Live Chat Connector sınıfı"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.client = None
        self.username = self._extract_username(url)
        self.connected = False
        self.last_message_time = time.time()
        self.error_count = 0
        self.max_errors = 5
        self.retry_count = 0
        self.max_retries = 3
    
    def _extract_username(self, url):
        """URL'den kullanıcı adını çıkarır"""
        # URL'den @ işaretini içeren kullanıcı adını çıkar
        if "@" in url:
            parts = url.split("@")
            if len(parts) > 1:
                username = parts[1].split("/")[0].split("?")[0]
                return username
        
        # URL'de @ yoksa, son kısmı kullanıcı adı olarak kabul et
        parts = url.split("/")
        for part in parts:
            if part and part != "www.tiktok.com" and part != "tiktok.com" and part != "live":
                return part
        
        return None
    
    def _get_safe_attribute(self, obj, attr_name, default=None):
        """Nesnenin bir özelliğini güvenli bir şekilde alır"""
        if obj is None:
            return default
        
        # Nesne bir sözlük ise
        if isinstance(obj, dict):
            return obj.get(attr_name, default)
        
        # Nesne bir nesne ise
        try:
            return getattr(obj, attr_name, default)
        except (AttributeError, TypeError):
            return default
    
    def _get_username_from_event(self, event):
        """Event nesnesinden kullanıcı adını güvenli bir şekilde alır"""
        try:
            # Kullanıcı nesnesi kontrolü
            user = getattr(event, "user", None)
            
            # Kullanıcı nesnesi bir sözlük olabilir
            if isinstance(user, dict):
                return user.get("unique_id", user.get("nickname", "Anonim"))
            
            # Kullanıcı nesnesi bir nesne olabilir
            if user is not None:
                unique_id = self._get_safe_attribute(user, "unique_id")
                if unique_id:
                    return unique_id
                
                nickname = self._get_safe_attribute(user, "nickname")
                if nickname:
                    return nickname
            
            # Doğrudan event nesnesinden almayı dene
            unique_id = self._get_safe_attribute(event, "unique_id")
            if unique_id:
                return unique_id
            
            nickname = self._get_safe_attribute(event, "nickname")
            if nickname:
                return nickname
            
            return "Anonim"
        except Exception:
            return "Anonim"
    
    async def _connect(self):
        """TikTok canlı yayınına bağlanır"""
        if not self.username:
            logging.error("Kullanıcı adı çıkarılamadı: %s", self.url)
            self.message_queue.put(("SISTEM", f"TikTok kullanıcı adı çıkarılamadı: {self.url}", time.strftime("%H:%M:%S"), "TikTok"))
            return False
        
        try:
            # TikTok Live Client'ı oluştur
            logging.info(f"TikTok Live bağlantısı kuruluyor: @{self.username}")
            self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı kuruluyor: @{self.username}...", time.strftime("%H:%M:%S"), "TikTok"))
            
            # Client'ı yapılandır - parametreleri azaltarak basitleştir
            self.client = TikTokLiveClient(unique_id=f"@{self.username}")
            
            # Olay dinleyicilerini ekle
            @self.client.on("connect")
            async def on_connect(_):
                logging.info(f"TikTok Live bağlantısı kuruldu: @{self.username}")
                self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı kuruldu: @{self.username}", time.strftime("%H:%M:%S"), "TikTok"))
                self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
                self.connected = True
                self.last_message_time = time.time()
                self.error_count = 0
                self.retry_count = 0
            
            @self.client.on("disconnect")
            async def on_disconnect(_):
                logging.info(f"TikTok Live bağlantısı kesildi: @{self.username}")
                self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı kesildi: @{self.username}", time.strftime("%H:%M:%S"), "TikTok"))
                self.connected = False
                
                # Bağlantı kesildiğinde ve yeniden deneme sayısı aşılmadıysa tekrar dene
                if not self.stop_event.is_set() and self.retry_count < self.max_retries:
                    self.retry_count += 1
                    logging.info(f"TikTok Live bağlantısı yeniden deneniyor ({self.retry_count}/{self.max_retries})...")
                    self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı yeniden deneniyor ({self.retry_count}/{self.max_retries})...", time.strftime("%H:%M:%S"), "TikTok"))
                    await asyncio.sleep(2)  # Kısa bir bekleme
                    await self._connect()  # Yeniden bağlan
            
            @self.client.on("error")
            async def on_error(error):
                logging.error(f"TikTok Live hatası: {error}")
                self.message_queue.put(("SISTEM", f"TikTok Live hatası: {str(error)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
                self.error_count += 1
                
                # Hata çok fazlaysa bağlantıyı yeniden kur
                if self.error_count >= self.max_errors:
                    logging.info("Çok fazla hata, bağlantı yeniden kuruluyor...")
                    self.message_queue.put(("SISTEM", "Çok fazla hata, bağlantı yeniden kuruluyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                    await asyncio.sleep(2)
                    await self._connect()
            
            @self.client.on("comment")
            async def on_comment(event):
                try:
                    username = self._get_username_from_event(event)
                    comment = self._get_safe_attribute(event, "comment", "")
                    current_time = time.strftime("%H:%M:%S")
                    self.message_queue.put((username, comment, current_time, "TikTok"))
                    self.last_message_time = time.time()
                    logging.debug(f"TikTok yorumu alındı: {username}: {comment}")
                except Exception as e:
                    logging.error(f"Yorum işlenirken hata: {e}")
            
            @self.client.on("gift")
            async def on_gift(event):
                try:
                    username = self._get_username_from_event(event)
                    
                    # Hediye nesnesini güvenli bir şekilde al
                    gift = self._get_safe_attribute(event, "gift")
                    gift_name = self._get_safe_attribute(gift, "name", "Hediye")
                    gift_count = self._get_safe_attribute(gift, "count", 1)
                    
                    gift_info = f"{gift_name} x{gift_count} 🎁"
                    current_time = time.strftime("%H:%M:%S")
                    self.message_queue.put((username, gift_info, current_time, "TikTok"))
                    self.last_message_time = time.time()
                    logging.debug(f"TikTok hediyesi alındı: {username}: {gift_info}")
                except Exception as e:
                    logging.error(f"Hediye işlenirken hata: {e}")
            
            @self.client.on("like")
            async def on_like(event):
                try:
                    # total_likes özelliğini güvenli bir şekilde al
                    total_likes = self._get_safe_attribute(event, "total_likes", 0)
                    
                    if total_likes % 100 == 0 and total_likes > 0:  # Her 100 beğenide bir bildirim
                        username = self._get_username_from_event(event)
                        like_info = f"{total_likes} beğeni ❤️"
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put((username, like_info, current_time, "TikTok"))
                        self.last_message_time = time.time()
                        logging.debug(f"TikTok beğenisi alındı: {username}: {like_info}")
                except Exception as e:
                    logging.error(f"Beğeni işlenirken hata: {e}")
            
            @self.client.on("share")
            async def on_share(event):
                try:
                    username = self._get_username_from_event(event)
                    share_info = "Yayını paylaştı 🔄"
                    current_time = time.strftime("%H:%M:%S")
                    self.message_queue.put((username, share_info, current_time, "TikTok"))
                    self.last_message_time = time.time()
                    logging.debug(f"TikTok paylaşımı alındı: {username}: {share_info}")
                except Exception as e:
                    logging.error(f"Paylaşım işlenirken hata: {e}")
            
            @self.client.on("follow")
            async def on_follow(event):
                try:
                    username = self._get_username_from_event(event)
                    follow_info = "Takip etti ✅"
                    current_time = time.strftime("%H:%M:%S")
                    self.message_queue.put((username, follow_info, current_time, "TikTok"))
                    self.last_message_time = time.time()
                    logging.debug(f"TikTok takibi alındı: {username}: {follow_info}")
                except Exception as e:
                    logging.error(f"Takip işlenirken hata: {e}")
            
            @self.client.on("viewer_count_update")
            async def on_viewer_count_update(event):
                try:
                    # viewer_count özelliğini güvenli bir şekilde al
                    viewer_count = self._get_safe_attribute(event, "viewer_count", 0)
                    
                    if viewer_count % 100 == 0 and viewer_count > 0:  # Her 100 izleyicide bir bildirim
                        viewer_info = f"{viewer_count} izleyici 👁️"
                        current_time = time.strftime("%H:%M:%S")
                        self.message_queue.put(("SISTEM", viewer_info, current_time, "TikTok"))
                        self.last_message_time = time.time()
                        logging.debug(f"TikTok izleyici sayısı güncellendi: {viewer_info}")
                except Exception as e:
                    logging.error(f"İzleyici sayısı güncellenirken hata: {e}")
            
            # Bağlantıyı başlat
            try:
                await self.client.connect()
                return True
            except Exception as connect_err:
                logging.error(f"TikTok Live bağlantısı başlatılırken hata: {connect_err}")
                self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı başlatılırken hata: {str(connect_err)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
                return False
            
        except Exception as e:
            logging.error(f"TikTok Live bağlantısı kurulurken hata: {str(e)}")
            logging.error(traceback.format_exc())  # Tam hata izini logla
            self.message_queue.put(("SISTEM", f"TikTok Live bağlantısı kurulurken hata: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
    
    async def _run_async(self):
        """Asenkron çalışma metodu"""
        try:
            # Bağlantıyı kur
            if not await self._connect():
                return False
            
            # Bağlantı durumunu kontrol et
            while not self.stop_event.is_set():
                # Belirli aralıklarla bildirim
                if time.time() - self.last_message_time > 60:
                    self.message_queue.put(("SISTEM", "TikTok Live bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                    self.last_message_time = time.time()
                
                # Kısa bir bekleme
                await asyncio.sleep(5)
            
            # Bağlantıyı kapat
            try:
                await self.client.disconnect()
            except:
                pass
            return True
            
        except Exception as e:
            logging.error(f"TikTok Live genel hatası: {str(e)}")
            logging.error(traceback.format_exc())  # Tam hata izini logla
            self.message_queue.put(("SISTEM", f"TikTok Live hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
    
    def run(self):
        """Ana çalışma metodu"""
        # Asenkron çalışma metodunu çalıştır
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_async())
        except Exception as e:
            logging.error(f"TikTok Live thread hatası: {str(e)}")
            logging.error(traceback.format_exc())  # Tam hata izini logla
            self.message_queue.put(("SISTEM", f"TikTok Live thread hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
        finally:
            loop.close()
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.stop_event.set()


def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok Live bağlantısını başlatır"""
    connector = TikTokLiveConnector(url, message_queue, stop_event)
    connector.run()


# Test ve debug
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = input("TikTok URL'si girin: ")
    
    queue = Queue()
    stop = threading.Event()
    
    connector = TikTokLiveConnector(url, queue, stop)
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