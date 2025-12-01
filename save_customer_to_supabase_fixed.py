"""
Supabase müşteri kayıt fonksiyonları (Düzeltilmiş versiyon)
"""
import os
import json
import logging
import uuid
from supabase import create_client

# Loglama ayarları
logging.basicConfig(
    filename="mezat.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def get_supabase_client():
    """Supabase istemcisini oluşturur"""
    try:
        with open("supabase_config.json", encoding="utf-8") as f:
            config = json.load(f)
        return create_client(config["url"], config["key"])
    except Exception as e:
        logging.exception("supabase_client")
        return None

def save_customer_to_supabase(user_id, youtube_channel, fullname, phone, address):
    """Müşteri bilgilerini Supabase'e kaydeder"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            logging.error("Supabase bağlantısı kurulamadı")
            return False, "Supabase bağlantısı kurulamadı"
            
        # Önce bu YouTube kanalı için kayıt var mı kontrol et
        response = supabase.table("customers").select("*").eq("youtube_channel", youtube_channel).execute()
        
        # Foreign key hatası nedeniyle user_id referansını kaldırıyoruz
        # User ID yerine özel bir ID kullanacağız
        customer_data = {
            "youtube_channel": youtube_channel,
            "fullname": fullname,
            "phone": phone,
            "address": address,
            "external_id": user_id  # user_id'yi external_id olarak kaydedelim
        }
        
        if response.data:
            # Kayıt varsa güncelle
            customer_id = response.data[0]["id"]
            response = supabase.table("customers").update(customer_data).eq("id", customer_id).execute()
            
            if response.data:
                logging.info(f"Müşteri güncellendi: {youtube_channel}")
                return True, "Müşteri bilgileri başarıyla güncellendi"
            else:
                logging.error(f"Müşteri güncellenemedi: {youtube_channel}")
                return False, "Müşteri bilgileri güncellenemedi"
        else:
            # Kayıt yoksa yeni ekle
            response = supabase.table("customers").insert(customer_data).execute()
            
            if response.data:
                logging.info(f"Yeni müşteri eklendi: {youtube_channel}")
                return True, "Müşteri bilgileri başarıyla kaydedildi"
            else:
                logging.error(f"Müşteri eklenemedi: {youtube_channel}")
                return False, "Müşteri bilgileri kaydedilemedi"
                
    except Exception as e:
        logging.exception(f"save_customer_to_supabase: {str(e)}")
        return False, f"Hata: {str(e)}"

def get_customer_from_supabase(youtube_channel):
    """Müşteri bilgilerini Supabase'den getirir"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
            
        response = supabase.table("customers").select("*").eq("youtube_channel", youtube_channel).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logging.exception(f"get_customer_from_supabase: {str(e)}")
        return None