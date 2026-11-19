# orlex-monitor

ORLEX ürün etiketlerindeki QR kodlarının açtığı sayfaları her gün kontrol eder. Bu kontrol Claude veya başka bir yapay zekâ kullanmaz.

**Her gün 07:17'de (İstanbul saati):**

- 1.384 QR sayfasının (`orlexglobal.com/01/<GTIN>/10/<LOT>/`) ve `/etiket/` aracının açılıp açılmadığına bakar. Açılan her sayfanın içeriği `baseline.sha256` dosyasındaki kayıtla birebir aynı olmalıdır.
- Ana sayfanın açıldığını kontrol eder.
- orlexglobal.com alan adının bitiş tarihine bakar. Bitişe **90 günden az** kaldıysa alarm verir.

**Sorun çıkarsa:** "ALARM" başlıklı bir issue açılır ve GitHub depo sahibine e-posta gönderir. Sorun sürerse aynı issue'ya her gün yorum eklenir.

**Son kontrolün sonucu:** [last-check.md](last-check.md)

**Bilerek bir QR sayfası değiştirilirse ya da yeni etiket sayfası eklenirse:** `baseline.sha256` dosyası güncellenmelidir. Güncellenmezse kontrol bunu sorun sayar ve alarm verir.
