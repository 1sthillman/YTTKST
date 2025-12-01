#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Canlı Chat – Real-Time, Tek Dosya
> python tiktok_chat.py @kullaniciadi
"""

import argparse
import asyncio
import logging
import threading
import time
from queue import Queue

from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, GiftEvent, LikeEvent, FollowEvent, ViewerCountUpdateEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def parse():
    parser = argparse.ArgumentParser(description="TikTok canlı-yayın chat okuyucu")
    parser.add_argument("username", help="TikTok kullanıcı adı (@ olmadan)")
    return parser.parse_args()

async def run_client(username, message_queue=None, stop_event=None):
    """TikTokLive istemcisini çalıştırır"""
    # @ işaretini kaldır (eğer varsa)
    if username.startswith('@'):
        username = username[1:]
    
    # Mesaj kuyruğu ve durdurma olayı oluştur (eğer verilmemişse)
    if message_queue is None:
        message_queue = Queue()
    if stop_event is None:
        stop_event = threading.Event()
    
    # TikTok Live Client'ı oluştur
    client = TikTokLiveClient(unique_id=username)
    
    @client.on("connect")
    async def on_connect(_):
        logging.info(f"TikTok Live bağlantısı kuruldu: @{username}")
        message_queue.put(("SISTEM", f"TikTok Live bağlantısı kuruldu: @{username}", time.strftime("%H:%M:%S"), "TikTok"))
        message_queue.put(("__STATUS__", "connection_connected", "#10b981", "TikTok"))
    
    @client.on("disconnect")
    async def on_disconnect(_):
        logging.info(f"TikTok Live bağlantısı kesildi: @{username}")
        message_queue.put(("SISTEM", f"TikTok Live bağlantısı kesildi: @{username}", time.strftime("%H:%M:%S"), "TikTok"))
        message_queue.put(("__STATUS__", "connection_disconnected", "#f97316", "TikTok"))
    
    @client.on("comment")
    async def on_comment(event: CommentEvent):
        try:
            username = event.user.nickname
            comment = event.comment
            current_time = time.strftime("%H:%M:%S")
            message_queue.put((username, comment, current_time, "TikTok"))
            logging.debug(f"TikTok yorumu alındı: {username}: {comment}")
        except Exception as e:
            logging.error(f"Yorum işlenirken hata: {e}")
    
    @client.on("gift")
    async def on_gift(event: GiftEvent):
        try:
            username = event.user.nickname
            gift_name = event.gift.name
            gift_count = event.gift.count
            gift_info = f"{gift_name} x{gift_count} 🎁"
            current_time = time.strftime("%H:%M:%S")
            message_queue.put((username, gift_info, current_time, "TikTok"))
            logging.debug(f"TikTok hediyesi alındı: {username}: {gift_info}")
        except Exception as e:
            logging.error(f"Hediye işlenirken hata: {e}")
    
    @client.on("like")
    async def on_like(event: LikeEvent):
        try:
            if event.total_likes % 100 == 0:  # Her 100 beğenide bir bildirim
                username = event.user.nickname
                like_info = f"{event.total_likes} beğeni ❤️"
                current_time = time.strftime("%H:%M:%S")
                message_queue.put((username, like_info, current_time, "TikTok"))
                logging.debug(f"TikTok beğenisi alındı: {username}: {like_info}")
        except Exception as e:
            logging.error(f"Beğeni işlenirken hata: {e}")
    
    @client.on("follow")
    async def on_follow(event: FollowEvent):
        try:
            username = event.user.nickname
            follow_info = "Takip etti ✅"
            current_time = time.strftime("%H:%M:%S")
            message_queue.put((username, follow_info, current_time, "TikTok"))
            logging.debug(f"TikTok takibi alındı: {username}: {follow_info}")
        except Exception as e:
            logging.error(f"Takip işlenirken hata: {e}")
    
    @client.on("viewer_count_update")
    async def on_viewer_count_update(event: ViewerCountUpdateEvent):
        try:
            if event.viewer_count % 100 == 0:  # Her 100 izleyicide bir bildirim
                viewer_info = f"{event.viewer_count} izleyici 👁️"
                current_time = time.strftime("%H:%M:%S")
                message_queue.put(("SISTEM", viewer_info, current_time, "TikTok"))
                logging.debug(f"TikTok izleyici sayısı güncellendi: {viewer_info}")
        except Exception as e:
            logging.error(f"İzleyici sayısı güncellenirken hata: {e}")
    
    # Bağlantıyı başlat
    logging.info(f"TikTok Live bağlantısı kuruluyor: @{username}")
    message_queue.put(("SISTEM", f"TikTok Live bağlantısı kuruluyor: @{username}...", time.strftime("%H:%M:%S"), "TikTok"))
    
    try:
        await client.start()
    except Exception as e:
        logging.error(f"TikTok Live bağlantı hatası: {e}")
        message_queue.put(("SISTEM", f"TikTok Live bağlantı hatası: {str(e)[:50]}...", time.strftime("%H:%M:%S"), "TikTok"))
    
    # Durdurma olayını bekle
    while not stop_event.is_set():
        await asyncio.sleep(1)
    
    # Bağlantıyı kapat
    await client.stop()

def start_tiktok_chat(url, message_queue=None, stop_event=None):
    """TikTok chat bağlantısını başlatan fonksiyon (mezaxx.py için)"""
    # URL'den kullanıcı adını çıkar
    username = url
    if "@" in url:
        parts = url.split("@")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
    else:
        parts = url.split("/")
        for part in parts:
            if part and part != "www.tiktok.com" and part != "tiktok.com" and part != "live":
                username = part
                break
    
    if not username:
        logging.error(f"Kullanıcı adı çıkarılamadı: {url}")
        if message_queue:
            message_queue.put(("SISTEM", f"TikTok kullanıcı adı çıkarılamadı: {url}", time.strftime("%H:%M:%S"), "TikTok"))
        return
    
    # Async fonksiyonu thread içinde çalıştır
    def run_async_client():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_client(username, message_queue, stop_event))
        finally:
            loop.close()
    
    # Thread'i başlat
    thread = threading.Thread(target=run_async_client, daemon=True)
    thread.start()
    return thread

if __name__ == '__main__':
    args = parse()
    message_queue = Queue()
    stop_event = threading.Event()
    
    # Thread içinde async fonksiyonu çalıştır
    client_thread = start_tiktok_chat(args.username, message_queue, stop_event)
    
    try:
        # Ana thread'de mesajları yazdır
        while True:
            if not message_queue.empty():
                message = message_queue.get()
                if len(message) >= 4 and message[0] != "__STATUS__":
                    print(f"{message[2]} | {message[0]}: {message[1]}")
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Çıkış yapılıyor...")
        stop_event.set()
        client_thread.join(timeout=2)
        logging.info("Çıkış yapıldı.")

