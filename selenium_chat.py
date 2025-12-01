"""
Selenium tabanlı TikTok ve YouTube chat bağlantı modülü
Tarayıcı otomasyonu kullanarak doğrudan chat mesajlarını çeker
"""

import time
import logging
import threading
import re
import json
from queue import Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SeleniumChatConnector:
    """Selenium tabanlı chat bağlantı sınıfı"""
    
    def __init__(self, url, message_queue=None, stop_event=None):
        self.url = url
        self.message_queue = message_queue or Queue()
        self.stop_event = stop_event or threading.Event()
        self.driver = None
        self.connected = False
        self.last_message_time = time.time()
        self.error_count = 0
        self.max_errors = 10
        self.platform = "TikTok" if "tiktok.com" in url.lower() else "YouTube" if "youtube.com" in url.lower() or "youtu.be" in url.lower() else "Unknown"
        self.processed_messages = set()  # İşlenmiş mesajları takip etmek için
        
    def initialize_driver(self):
        """Selenium WebDriver'ı başlatır"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Başsız modda çalıştır
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--mute-audio")  # Sesi kapat
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            
            # WebDriver'ı başlat
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)  # Sayfa yükleme zaman aşımı
            
            logging.info(f"Selenium WebDriver başlatıldı ({self.platform})")
            return True
        except Exception as e:
            logging.error(f"Selenium WebDriver başlatma hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"Tarayıcı başlatılamadı: {str(e)[:50]}...", time.strftime("%H:%M:%S"), self.platform))
            return False
    
    def connect_tiktok(self):
        """TikTok chat bağlantısı kurar"""
        try:
            if not self.initialize_driver():
                return False
                
            # TikTok canlı yayın sayfasını aç
            logging.info(f"TikTok sayfası açılıyor: {self.url}")
            self.driver.get(self.url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(5)
            
            # Canlı yayın kontrolü
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-e2e='chat-message'], div[data-e2e='message-item']"))
                )
                logging.info("TikTok chat alanı bulundu")
            except TimeoutException:
                logging.error("TikTok chat alanı bulunamadı")
                self.message_queue.put(("SISTEM", "TikTok chat alanı bulunamadı veya canlı yayın aktif değil", time.strftime("%H:%M:%S"), "TikTok"))
                return False
                
            # Bağlantı başarılı
            self.connected = True
            self.message_queue.put(("SISTEM", "TikTok chat bağlantısı kuruldu (Selenium)", time.strftime("%H:%M:%S"), "TikTok"))
            self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
            
            # Chat mesajlarını çekme döngüsü
            while not self.stop_event.is_set() and self.connected:
                try:
                    # Chat mesajlarını bul
                    chat_messages = self.driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='chat-message'], div[data-e2e='message-item']")
                    
                    if chat_messages:
                        for message in chat_messages[-10:]:  # Son 10 mesajı işle (performans için)
                            try:
                                # Mesaj içeriğini çıkart
                                message_html = message.get_attribute('outerHTML')
                                
                                # Mesaj ID'si oluştur (tekrar işlemeyi önlemek için)
                                message_id = hash(message_html)
                                
                                # Daha önce işlenmiş mi kontrol et
                                if message_id in self.processed_messages:
                                    continue
                                    
                                self.processed_messages.add(message_id)
                                
                                # Kullanıcı adı ve mesaj içeriğini çıkart
                                username_match = re.search(r'data-e2e="chat-message-user-name"[^>]*>([^<]+)', message_html)
                                message_match = re.search(r'data-e2e="chat-message-text"[^>]*>([^<]+)', message_html)
                                
                                if not username_match or not message_match:
                                    # Alternatif format dene
                                    username_match = re.search(r'data-e2e="message-owner-name"[^>]*>([^<]+)', message_html)
                                    message_match = re.search(r'data-e2e="message-text"[^>]*>([^<]+)', message_html)
                                
                                if username_match and message_match:
                                    username = username_match.group(1).strip()
                                    text = message_match.group(1).strip()
                                    
                                    # Mesajı gönder
                                    current_time = time.strftime("%H:%M:%S")
                                    self.message_queue.put((username, text, current_time, "TikTok"))
                                    self.last_message_time = time.time()
                            except Exception as msg_err:
                                logging.error(f"TikTok mesaj işleme hatası: {str(msg_err)}")
                                continue
                                
                        # Hata sayacını sıfırla
                        self.error_count = 0
                    
                    # Belirli aralıklarla bildirim
                    if time.time() - self.last_message_time > 30:
                        self.message_queue.put(("SISTEM", "TikTok bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "TikTok"))
                        self.last_message_time = time.time()
                    
                    # Sayfayı kaydır (yeni mesajları görmek için)
                    try:
                        self.driver.execute_script("document.querySelector('.tiktok-1n0ni8r-DivChatRoomContainer').scrollTop = document.querySelector('.tiktok-1n0ni8r-DivChatRoomContainer').scrollHeight;")
                    except:
                        pass
                        
                    # Kısa bir bekleme
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"TikTok mesaj çekme hatası: {str(e)}")
                    self.error_count += 1
                    
                    if self.error_count >= self.max_errors:
                        logging.error("Çok fazla TikTok bağlantı hatası, bağlantı kesiliyor")
                        self.message_queue.put(("SISTEM", "Çok fazla TikTok bağlantı hatası, yeniden bağlanılıyor...", time.strftime("%H:%M:%S"), "TikTok"))
                        
                        # Sayfayı yenile
                        try:
                            self.driver.refresh()
                            time.sleep(5)
                            self.error_count = 0
                        except:
                            break
            
            return True
        except Exception as e:
            logging.error(f"TikTok bağlantı hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"TikTok bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def connect_youtube(self):
        """YouTube chat bağlantısı kurar"""
        try:
            if not self.initialize_driver():
                return False
                
            # YouTube canlı yayın sayfasını aç
            logging.info(f"YouTube sayfası açılıyor: {self.url}")
            self.driver.get(self.url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(5)
            
            # Chat iframe'ini bul
            try:
                # Chat iframe'ini bekle
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#chatframe"))
                )
                
                # iframe'e geç
                chat_frame = self.driver.find_element(By.CSS_SELECTOR, "iframe#chatframe")
                self.driver.switch_to.frame(chat_frame)
                
                # Chat mesajlarının yüklenmesini bekle
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "yt-live-chat-text-message-renderer"))
                )
                
                logging.info("YouTube chat alanı bulundu")
            except TimeoutException:
                logging.error("YouTube chat alanı bulunamadı")
                self.message_queue.put(("SISTEM", "YouTube chat alanı bulunamadı veya canlı yayın aktif değil", time.strftime("%H:%M:%S"), "YouTube"))
                return False
                
            # Bağlantı başarılı
            self.connected = True
            self.message_queue.put(("SISTEM", "YouTube chat bağlantısı kuruldu (Selenium)", time.strftime("%H:%M:%S"), "YouTube"))
            self.message_queue.put(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
            
            # Chat mesajlarını çekme döngüsü
            while not self.stop_event.is_set() and self.connected:
                try:
                    # Chat mesajlarını bul
                    chat_messages = self.driver.find_elements(By.CSS_SELECTOR, "yt-live-chat-text-message-renderer")
                    
                    if chat_messages:
                        for message in chat_messages[-15:]:  # Son 15 mesajı işle (performans için)
                            try:
                                # Mesaj içeriğini çıkart
                                message_html = message.get_attribute('outerHTML')
                                
                                # Mesaj ID'si oluştur (tekrar işlemeyi önlemek için)
                                message_id = hash(message_html)
                                
                                # Daha önce işlenmiş mi kontrol et
                                if message_id in self.processed_messages:
                                    continue
                                    
                                self.processed_messages.add(message_id)
                                
                                # Kullanıcı adı
                                try:
                                    author_element = message.find_element(By.CSS_SELECTOR, "#author-name")
                                    username = author_element.text.strip()
                                except:
                                    username = "Anonim"
                                
                                # Mesaj metni
                                try:
                                    message_element = message.find_element(By.CSS_SELECTOR, "#message")
                                    text = message_element.text.strip()
                                except:
                                    text = ""
                                
                                if username and text:
                                    # Mesajı gönder
                                    current_time = time.strftime("%H:%M:%S")
                                    self.message_queue.put((username, text, current_time, "YouTube"))
                                    self.last_message_time = time.time()
                            except Exception as msg_err:
                                logging.error(f"YouTube mesaj işleme hatası: {str(msg_err)}")
                                continue
                                
                        # Hata sayacını sıfırla
                        self.error_count = 0
                    
                    # Belirli aralıklarla bildirim
                    if time.time() - self.last_message_time > 30:
                        self.message_queue.put(("SISTEM", "YouTube bağlantısı aktif, mesaj bekleniyor...", time.strftime("%H:%M:%S"), "YouTube"))
                        self.last_message_time = time.time()
                    
                    # Sayfayı kaydır (yeni mesajları görmek için)
                    try:
                        self.driver.execute_script("document.querySelector('#item-list').scrollTop = document.querySelector('#item-list').scrollHeight;")
                    except:
                        pass
                        
                    # Kısa bir bekleme
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"YouTube mesaj çekme hatası: {str(e)}")
                    self.error_count += 1
                    
                    if self.error_count >= self.max_errors:
                        logging.error("Çok fazla YouTube bağlantı hatası, bağlantı kesiliyor")
                        self.message_queue.put(("SISTEM", "Çok fazla YouTube bağlantı hatası, yeniden bağlanılıyor...", time.strftime("%H:%M:%S"), "YouTube"))
                        
                        # Ana frame'e geri dön
                        try:
                            self.driver.switch_to.default_content()
                            # Sayfayı yenile
                            self.driver.refresh()
                            time.sleep(5)
                            
                            # Chat iframe'ini tekrar bul
                            chat_frame = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#chatframe"))
                            )
                            self.driver.switch_to.frame(chat_frame)
                            self.error_count = 0
                        except:
                            break
            
            return True
        except Exception as e:
            logging.error(f"YouTube bağlantı hatası: {str(e)}")
            self.message_queue.put(("SISTEM", f"YouTube bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "YouTube"))
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def close(self):
        """Bağlantıyı kapatır"""
        self.connected = False
        self.stop_event.set()
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def run(self):
        """Ana çalışma metodu"""
        if self.platform == "TikTok":
            return self.connect_tiktok()
        elif self.platform == "YouTube":
            return self.connect_youtube()
        else:
            logging.error(f"Desteklenmeyen platform: {self.platform}")
            self.message_queue.put(("SISTEM", f"Desteklenmeyen platform: {self.platform}", time.strftime("%H:%M:%S"), "Sistem"))
            return False


def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok chat bağlantısını başlatır"""
    connector = SeleniumChatConnector(url, message_queue, stop_event)
    connector.run()


def start_youtube_chat(url, message_queue=None, stop_event=None):
    """YouTube chat bağlantısını başlatır"""
    connector = SeleniumChatConnector(url, message_queue, stop_event)
    connector.run()


# Test ve debug
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = input("TikTok veya YouTube URL'si girin: ")
    
    queue = Queue()
    stop = threading.Event()
    
    connector = SeleniumChatConnector(url, queue, stop)
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

