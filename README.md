# YTTKST

# YouTube Mezat Yardımcısı

Bu program YouTube canlı yayınlarında mezat düzenlemeye yardımcı olan, teklifleri toplayan ve yöneten bir uygulamadır.

## Dağıtım Hazırlığı

Bu klasörde program dosyalarının yanı sıra dağıtım için hazırlanmış bazı dosyalar bulunmaktadır:

- `paketleyici.bat` - Uygulamayı çalıştırılabilir .exe dosyası haline getirir
- `kurulum.bat` - Son kullanıcıların uygulamayı bilgisayarına kurmasını sağlar
- `mezatyardimcisi.spec` - PyInstaller için yapılandırma dosyası
- `KURULUM_KILAVUZU.txt` - Son kullanıcılar için kurulum kılavuzu

## Dağıtım Adımları

1. **Paketin Oluşturulması:**
   - `paketleyici.bat` dosyasını çalıştırarak uygulamayı .exe dosyasına dönüştürün
   - Bu işlem sonunda `dist` klasöründe `YouTube Mezat Yardimcisi.exe` dosyası oluşacaktır

2. **Dağıtım için Dosyaları Hazırlama:**
   - `dist` klasöründeki `YouTube Mezat Yardimcisi.exe` dosyasını
   - `LOGO.png`, `LICENSE.txt`, `license_codes.json`, `settings.json` dosyalarını
   - `KURULUM_KILAVUZU.txt` ve `kurulum.bat` dosyalarını
   - ZIP formatında arşivleyin

3. **Son Kullanıcıya Gönderme:**
   - Oluşturduğunuz ZIP dosyasını son kullanıcıya gönderin
   - Kullanıcının ZIP dosyasını çıkarıp `kurulum.bat` dosyasını çalıştırması yeterlidir

## Güvenlik Notları

- Program kaynak kodları .exe içerisinde gizlenmiş olacaktır
- Son kullanıcılar sadece kurulumdan sonra oluşan çalıştırılabilir dosyaya sahip olacaktır
- Lisans doğrulama sistemi, programın yetkisiz kişilerce veya farklı bilgisayarlarda kullanılmasını önler

## Gerekli Dosyalar

Dağıtımdan önce aşağıdaki dosyaların güncel olduğundan emin olun:

- `license_codes.json` - Geçerli lisans kodlarının bulunduğu dosya
- `settings.json` - Varsayılan ayarların bulunduğu dosya

## Ek Bilgi

Program; Windows 7, 8, 10 ve 11 işletim sistemlerinde çalışır. Kullanıcıların sadece ZIP dosyasını indirip kurulum sihirbazını çalıştırması yeterlidir.

## GitHub Pages

Proje GitHub Pages'de yayınlanmaktadır: [https://1sthillman.github.io/YTTKST/](https://1sthillman.github.io/YTTKST/)
