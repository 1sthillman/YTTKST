#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatDownloader ve gerekli modülleri otomatik yükleyen yardımcı script
YouTube Mezat Yardımcısı için gerekli modülleri kontrol edip yükler
"""

import os
import sys
import time
import logging
import subprocess
import importlib.util

# Gerekli modüller listesi
REQUIRED_MODULES = {
    "chat_downloader": "chat-downloader>=0.1.8",
    "requests": "requests>=2.25.1",
    "beautifulsoup4": "beautifulsoup4>=4.9.3",
    "websocket": "websocket-client>=1.2.1",
    "customtkinter": "customtkinter>=4.6.3",
    "pygame": "pygame>=2.0.1",
    "pillow": "Pillow>=8.2.0",
    "supabase": "supabase>=2.20.0",
    "websockets": "websockets>=15.0.1",
}

def check_module_installed(module_name):
    """Belirtilen modülün yüklü olup olmadığını kontrol eder."""
    try:
        importlib.util.find_spec(module_name)
        return True
    except ImportError:
        return False

def install_module(module_spec):
    """Belirtilen modülü pip ile yükler."""
    try:
        print(f"Yükleniyor: {module_spec}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", module_spec])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Hata: {module_spec} yüklenemedi! ({e})")
        return False

def check_and_install_modules():
    """Tüm gerekli modülleri kontrol eder ve eksik olanları yükler."""
    print("\n*** YouTube Mezat Yardımcısı - Modül Kontrolü ***\n")
    
    missing_modules = []
    for module_name, module_spec in REQUIRED_MODULES.items():
        print(f"Kontrol ediliyor: {module_name}...")
        if not check_module_installed(module_name):
            missing_modules.append((module_name, module_spec))
    
    if not missing_modules:
        print("\nTüm gerekli modüller zaten yüklü! Hazırız.")
        return True
    
    # Eksik modülleri yüklemeyi dene
    print(f"\n{len(missing_modules)} adet eksik modül bulundu. Şimdi yükleniyor...\n")
    
    success_count = 0
    for module_name, module_spec in missing_modules:
        if install_module(module_spec):
            success_count += 1
    
    print(f"\n{success_count}/{len(missing_modules)} modül başarıyla yüklendi.")
    
    # Tüm modüller yüklendi mi kontrol et
    if success_count == len(missing_modules):
        print("\nTüm modüller yüklendi! Program hazır.")
        return True
    else:
        print("\nBazı modüller yüklenemedi. Program düzgün çalışmayabilir.")
        return False

def main():
    """Ana fonksiyon."""
    try:
        check_and_install_modules()
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
        return False
    
    print("\nProgram başlatılıyor...")
    return True

if __name__ == "__main__":
    main()

