"""
Bağlantı durumu gösterici modülü
"""

import time
import threading
import logging
from queue import Queue

class ConnectionStatusMonitor:
    """Bağlantı durumu izleyici sınıfı"""
    
    def __init__(self, message_queue=None, update_interval=5):
        self.message_queue = message_queue or Queue()
        self.update_interval = update_interval
        self.stop_event = threading.Event()
        self.platform_status = {
            "YouTube": {
                "connected": False,
                "last_message_time": 0,
                "error_count": 0,
                "status_text": "Bağlantı Yok",
                "status_color": "#ff0000"  # Kırmızı
            },
            "TikTok": {
                "connected": False,
                "last_message_time": 0,
                "error_count": 0,
                "status_text": "Bağlantı Yok",
                "status_color": "#ff0000"  # Kırmızı
            }
        }
        self.monitor_thread = None
    
    def start(self):
        """İzleme işlemini başlatır"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.stop_event.clear()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop(self):
        """İzleme işlemini durdurur"""
        self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(1.0)
    
    def update_status(self, platform, status_type, value):
        """Belirli bir platformun durumunu günceller"""
        if platform in self.platform_status:
            if status_type == "connection_connected":
                self.platform_status[platform]["connected"] = True
                self.platform_status[platform]["status_text"] = "Bağlı"
                self.platform_status[platform]["status_color"] = "#10b981"  # Yeşil
                self.platform_status[platform]["last_message_time"] = time.time()
                self.platform_status[platform]["error_count"] = 0
            elif status_type == "connection_disconnected":
                self.platform_status[platform]["connected"] = False
                self.platform_status[platform]["status_text"] = "Bağlantı Kesildi"
                self.platform_status[platform]["status_color"] = "#f97316"  # Turuncu
            elif status_type == "connection_error":
                self.platform_status[platform]["error_count"] += 1
                if self.platform_status[platform]["error_count"] > 3:
                    self.platform_status[platform]["status_text"] = "Bağlantı Hatası"
                    self.platform_status[platform]["status_color"] = "#ef4444"  # Kırmızı
            elif status_type == "message_received":
                self.platform_status[platform]["last_message_time"] = time.time()
                if self.platform_status[platform]["connected"]:
                    self.platform_status[platform]["status_text"] = "Aktif"
                    self.platform_status[platform]["status_color"] = "#10b981"  # Yeşil
    
    def _monitor_loop(self):
        """Bağlantı durumunu sürekli izler"""
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Her platform için durumu kontrol et
            for platform, status in self.platform_status.items():
                if status["connected"]:
                    # Son mesaj alındığından beri geçen süre
                    time_since_last_message = current_time - status["last_message_time"]
                    
                    # 60 saniyeden fazla mesaj alınmadıysa uyarı ver
                    if time_since_last_message > 60:
                        status["status_text"] = "Bağlı (Sessiz)"
                        status["status_color"] = "#eab308"  # Sarı
                        
                        # 180 saniyeden fazla mesaj alınmadıysa bağlantı problemi olabilir
                        if time_since_last_message > 180:
                            status["status_text"] = "Bağlantı Problemi"
                            status["status_color"] = "#f97316"  # Turuncu
                            
                            # 300 saniyeden fazla mesaj alınmadıysa bağlantı kesilmiş olabilir
                            if time_since_last_message > 300:
                                status["status_text"] = "Bağlantı Kesilmiş Olabilir"
                                status["status_color"] = "#ef4444"  # Kırmızı
                                
                                # Kullanıcıya bildirim gönder
                                self.message_queue.put(("SISTEM", f"{platform} bağlantısı uzun süredir sessiz, kontrol edilmeli", time.strftime("%H:%M:%S"), platform))
                    
                    # Durum mesajı gönder
                    self.message_queue.put(("__STATUS__", status["status_text"], status["status_color"], platform))
            
            # Belirli aralıklarla kontrol et
            time.sleep(self.update_interval)
    
    def process_message(self, message):
        """Mesajı işler ve durumu günceller"""
        if len(message) >= 4:
            username, content, timestamp, platform = message
            
            # Özel durum mesajları
            if username == "__STATUS__":
                self.update_status(platform, content, timestamp)
            # Normal mesajlar
            elif platform in self.platform_status:
                self.update_status(platform, "message_received", None)


# Örnek kullanım
if __name__ == "__main__":
    monitor = ConnectionStatusMonitor()
    monitor.start()
    
    # Test mesajları
    monitor.process_message(("__STATUS__", "connection_connected", "#10b981", "YouTube"))
    monitor.process_message(("Kullanıcı1", "Merhaba", time.strftime("%H:%M:%S"), "YouTube"))
    
    time.sleep(2)
    
    monitor.process_message(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
    monitor.process_message(("Kullanıcı2", "Selam", time.strftime("%H:%M:%S"), "TikTok"))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()

