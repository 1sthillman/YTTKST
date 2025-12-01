"""
mezaxx.py için müşteri bilgilerini Supabase'e kaydetme fonksiyonu ekleyen dosya
Bu dosya mezaxx.py dosyasına eklenecek kodları içerir
"""

# save_user_details fonksiyonuna eklenecek kod
SAVE_USER_DETAILS_UPDATE = """
def save_user_details(self, username, fullname, phone, address):
    """Kullanıcı detaylarını kaydet ve Supabase'e gönder"""
    if not username or username not in self.paid_users:
        self.show_notification("Hata", "Geçerli bir kullanıcı seçin!", "error")
        return
        
    # Kullanıcı detaylarını güncelle
    self.paid_user_details[username] = {
        "fullname": fullname,
        "phone": phone,
        "address": address
    }
    
    # Detayları dosyaya kaydet
    self.save_user_details_to_file()
    
    # Supabase'e kaydet
    try:
        from save_customer_to_supabase import save_customer_to_supabase
        
        # auth_data.json dosyasından Supabase kullanıcı ID'sini al
        user_id = None
        if os.path.exists("auth_data.json"):
            with open("auth_data.json", "r", encoding="utf-8") as f:
                auth_data = json.load(f)
                user_id = auth_data.get("supabase_user_id")
        
        if user_id:
            success, message = save_customer_to_supabase(
                user_id=user_id,
                youtube_channel=username,
                fullname=fullname,
                phone=phone,
                address=address
            )
            
            if success:
                self.show_notification("Başarılı", f"{username} için bilgiler kaydedildi ve Supabase'e gönderildi", "success")
            else:
                self.show_notification("Uyarı", f"Bilgiler yerel olarak kaydedildi ancak Supabase'e gönderilemedi: {message}", "warning")
                logging.warning(f"Supabase kayıt hatası: {message}")
        else:
            self.show_notification("Başarılı", f"{username} için bilgiler kaydedildi", "success")
            logging.warning("Supabase kullanıcı ID bulunamadı")
    except Exception as e:
        self.show_notification("Başarılı", f"{username} için bilgiler kaydedildi", "success")
        logging.exception(f"Supabase kayıt hatası: {str(e)}")
"""

# show_manage_paid_users fonksiyonunda save_detail_btn için güncellenmiş kod
SAVE_BUTTON_UPDATE = """
        # Kaydet butonu - daha büyük ve belirgin
        save_detail_btn = ctk.CTkButton(detail_btn_frame, 
                                      text="💾 Kaydet", 
                                      fg_color=self.colors["secondary"],
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      height=45,
                                      corner_radius=10,
                                      command=lambda: self.save_user_details(
                                          username_entry.get(),
                                          fullname_entry.get(),
                                          phone_entry.get(),
                                          address_entry.get("1.0", "end-1c")
                                      ))
"""

# ModernYouTubeMezatYardimcisi.__init__ fonksiyonuna eklenecek kod
INIT_UPDATE = """
        # Müşteri bilgilerini yükle
        self.load_user_details_from_file()
"""

# load_user_details_from_file fonksiyonuna eklenecek kod (Supabase'den veri çekme)
LOAD_USER_DETAILS_UPDATE = """
def load_user_details_from_file(self):
    """Kullanıcı detaylarını dosyadan ve Supabase'den yükle"""
    try:
        # Yerel dosyadan yükle
        if os.path.exists("paid_users.json"):
            with open("paid_users.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.paid_users = data.get("users", [])
                self.paid_user_details = data.get("details", {})
                
        # Supabase'den müşteri bilgilerini çekmeyi dene
        try:
            from save_customer_to_supabase import get_supabase_client
            
            supabase = get_supabase_client()
            if supabase:
                # Tüm müşteri kayıtlarını çek
                response = supabase.table("customers").select("*").execute()
                
                if response.data:
                    for customer in response.data:
                        youtube_channel = customer.get("youtube_channel")
                        
                        # Kullanıcı listede yoksa ekle
                        if youtube_channel and youtube_channel not in self.paid_users:
                            self.paid_users.append(youtube_channel)
                        
                        # Kullanıcı detaylarını güncelle
                        self.paid_user_details[youtube_channel] = {
                            "fullname": customer.get("fullname", ""),
                            "phone": customer.get("phone", ""),
                            "address": customer.get("address", "")
                        }
                    
                    logging.info(f"Supabase'den {len(response.data)} müşteri bilgisi yüklendi")
        except Exception as e:
            logging.exception(f"Supabase'den müşteri bilgileri yüklenirken hata: {str(e)}")
        
        # Arayüzü güncelle
        self.refresh_paid_users_list()
        
    except Exception as e:
        logging.exception("load_user_details_from_file")
"""

