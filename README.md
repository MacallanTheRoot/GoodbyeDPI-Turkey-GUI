# GoodbyeDPI-Turkey GUI

Bu proje, Türkiye'deki internet kısıtlamalarını ve DPI (Deep Packet Inspection) engellemelerini aşmak için kullanılan araçlar için **herkesin kullanabileceği kadar basit**, modern bir arayüzdür.

**Amacımız:** Teknik bilgisi olmayan, komut satırlarıyla yada karmaşık ayarlarla uğraşmak istemeyen kullanıcıların tek bir tuşla özgür internete erişmesini sağlamaktır.

![Ekran Görüntüsü](https://i.imgur.com/example.png)

## Özellikler

-   **Tek Tıkla Erişim:** "ACTIVATE" butonuna basarak servisi başlatın.
-   **Kullanıcı Dostu Arayüz:** Karmaşık ayarlar yok, her şey anlaşılır ve basit.
-   **Otomatik Başlatma:** İsterseniz bilgisayarınız açıldığında otomatik olarak başlar ve kendini gizler. (Görev Yöneticisi Başlangıç sekmesinde "GoodbyeDPI-Turkey GUI" olarak görünür)
-   **Sistem Tepsisine Küçülme:** Uygulamayı kapattığınızda kapanmaz, saatin yanına gizlenir ve arka planda çalışmaya devam eder.
-   **DNS Seçenekleri:** Türkiye için özel ayarlanmış modun yanı sıra Google, Cloudflare gibi popüler DNS servislerini de seçebilirsiniz.

## Teşekkür ve Kaynaklar

Bu proje geliştirilirken, Türkiye'deki kısıtlamalar için en güncel ayarları sağlayan **[cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/GoodbyeDPI-Turkey)** projesinden ve kaynaklarından faydalanılmıştır. Bu değerli çalışma için teşekkür ederiz.

Bu arayüz, arka planda Windows'ta `GoodbyeDPI`, Linux'ta ise `SpoofDPI` araçlarını kullanır.

## Kurulum ve Kullanım

### Hazır Sürüm (Windows .exe)
1.  `dist` klasöründeki veya Releases kısmındaki `.exe` dosyasını indirin.
2.  Dosyaya sağ tıklayıp "Yönetici olarak çalıştır" demeniz önerilir (Program bunu otomatik de isteyecektir).
3.  Açılan ekranda **ACTIVATE** butonuna basın.
4.  Durum **SECURE** olduğunda işlem tamamdır.

### Geliştiriciler İçin (Python)

Eğer kaynak koddan çalıştırmak isterseniz:

1.  Python 3.10+ sürümünü kurun.
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı başlatın:
    ```bash
    # Yöntem 1: Konsol olmadan (Önerilen)
    run.cmd
    
    # Yöntem 2: Manuel
    pythonw src/main.py
    
    # Yöntem 3: Debug için (konsol ile)
    python src/main.py
    ```

## Yasal Uyarı
Bu yazılım sadece internet sansürünü aşmak ve bilgiye erişim özgürlüğü içindir. Yasa dışı amaçlarla kullanılması kullanıcının sorumluluğundadır.
