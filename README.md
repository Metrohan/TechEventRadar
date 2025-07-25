<img width="802" height="420" alt="Başlıksız(1)" src="https://github.com/user-attachments/assets/7528bb63-f02d-48cf-9cb9-f22e822128dd" />

# 🚀 TechEventRadar

Bu proje, çeşitli Türk teknoloji ve kariyer platformlarından güncel etkinlikleri (bootcamp'ler, hackathon'lar, yetenek programları vb.) çekmek, **PostgreSQL veritabanında** depolamak ve kullanıcı dostu bir web arayüzünde sunmak için geliştirilmiştir. Python, Selenium, BeautifulSoup, Flask, **PostgreSQL, Nginx ve uWSGI** teknolojilerini kullanır.

## ✨ Özellikler

* **Çoklu Kaynak Desteği:** TechCareer.net, Coderspace, Anbean, Kodluyoruz, Youthall gibi platformlardan veri çekme yeteneği.
* **Dinamik Veri Çekimi:** Selenium kullanarak JavaScript ile yüklenen dinamik içerikleri sorunsuz bir şekilde işler.
* **Sağlam Veri Depolama:** Etkinlik verilerini **PostgreSQL veritabanında** güvenli ve ölçeklenebilir bir şekilde depolar.
* **Kullanıcı Dostu Web Arayüzü:** Çekilen etkinlikleri kategoriye göre gruplandırılmış, görselliği ön planda tutan modern ve **tam responsive bir arayüzde** sunar.
* **Tek Tıkla Güncelleme:** Web arayüzü üzerinden "Verileri Güncelle" butonu ile en güncel etkinlikleri anında çekme imkanı.
* **Durum Takibi:** Etkinliklerin son güncelleme zamanını ve toplam etkinlik sayısını gösterir.
* **Üretim Ortamı İçin Yapılandırma:** **Docker, Nginx ve uWSGI** entegrasyonu ile hızlı ve güvenilir dağıtım.

## 🛠️ Teknolojiler

* **Python:** Backend scraping mantığı ve Flask uygulaması için ana dil.
* **Flask:** Hafif ve esnek bir Python web çatısı ile web arayüzünü oluşturur.
* **PostgreSQL:** Etkinlik verilerini depolamak için kullanılan ilişkisel veritabanı.
* **SQLAlchemy:** Flask uygulamasını PostgreSQL veritabanına bağlamak için kullanılan ORM (Object Relational Mapper).
* **Selenium:** Dinamik web sitelerinden veri çekmek için kullanılır.
* **BeautifulSoup4:** Çekilen HTML içeriğini ayrıştırmak için kullanılır.
* **WebDriver-Manager:** Selenium WebDriver'ları otomatik olarak yönetir.
* **Docker:** Uygulamanın ve veritabanının kapsayıcılı (containerized) ortamda çalışması için.
* **Nginx:** Web sunucusu ve ters proxy olarak görev yapar, statik dosyaları servis eder ve Flask uygulamasına gelen istekleri yönlendirir.
* **uWSGI:** Flask uygulamasını Nginx ile entegre etmek için kullanılan bir uygulama sunucusu arayüzü.
* **HTML/CSS/JavaScript:** Web arayüzünün frontend tasarımı ve etkileşimi için.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde kurmak ve çalıştırmak için veya üretim ortamında dağıtmak için aşağıdaki adımları izleyin.

**Önemli Not:** Bu depoda, platformların Hizmet Şartları ve etik nedenlerle web scraper kodları (`scrapers/` dizini) bulunmamaktadır. Eğer scraper'ları çalıştırmak istiyorsanız, bu modülleri kendi özel deponuzdan veya yerel olarak projenize eklemeniz gerekmektedir.

### Önkoşullar

* [Git](https://git-scm.com/downloads) (Repoyu klonlamak için)
* [Docker](https://www.docker.com/get-started/) ve [Docker Compose](https://docs.docker.com/compose/install/)
* [Google Chrome](https://www.google.com/chrome/) (Selenium için tarayıcı - **sadece yerel geliştirme için gerekli, Docker'da genellikle tarayıcı kapsayıcıda yüklüdür**)

### Adımlar

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/Metrohan/TechEventRadar.git
    cd TechEventRadar
    ```

2.  **Docker Ortamını Başlatın (Uygulama ve PostgreSQL):**
    ```bash
    docker-compose up --build -d
    ```
    Bu komut, `Dockerfile`'ı kullanarak Flask uygulamasını oluşturacak, `docker-compose.yml`'deki servisleri (Flask uygulaması ve PostgreSQL) başlatacak ve arka planda çalıştıracaktır.

3.  **Veritabanı Tablolarını Oluşturun (İlk Kez Çalıştırıldığında):**
    Flask uygulamanız ilk kez ayağa kalktığında otomatik olarak tabloları oluşturacaktır (`db.create_all()` sayesinde).

4.  **Scraper'ları Çalıştırın ve Verileri Çekin (İlk Kez Veritabanını Doldurmak veya Manuel Güncelleme İçin):**
    Flask uygulamasının kapsayıcısına bağlanarak scraper'ları çalıştırın:

    ```bash
    docker-compose exec app python main.py
    ```


    Bu komut, tanımlı tüm kaynaklardan etkinlik verilerini çekecek ve PostgreSQL veritabanına kaydedecektir.

5.  **Nginx Kurulumu (Üretim Ortamı İçin):**
    Üretim ortamında `eventradar.dev` gibi bir alan adı üzerinden erişim sağlamak için Nginx yapılandırması gereklidir.
    * `/etc/nginx/sites-available/` dizininde `eventradar.dev` adında bir Nginx yapılandırma dosyası oluşturun (veya düzenleyin).
    * İçine aşağıdaki örnek yapılandırmayı yapıştırın ve **kendi alan adınız ile proje yolunuzu (`/home/username/TechEventRadar/` gibi)** güncelleyin.

    ```nginx
    server {
        listen 80;
        server_name eventradar.dev www.eventradar.dev; # Kendi alan adlarını buraya ekle

        location / {
            return 301 https://$host$request_uri; # HTTP isteklerini HTTPS'ye yönlendir
        }
    }

    server {
        listen 443 ssl;
        server_name eventradar.dev www.eventradar.dev; # Kendi alan adlarını buraya ekle

        ssl_certificate /etc/letsencrypt/live/eventradar.dev/fullchain.pem; # Sertifika yolu (Let's Encrypt sonrası)
        ssl_key /etc/letsencrypt/live/eventradar.dev/privkey.pem;         # Anahtar yolu (Let's Encrypt sonrası)

        include /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

        root /home/username/TechEventRadar/; # Flask projenin ANA dizini (app.py, static, templates'ın olduğu dizin)

        location / {
            try_files $uri @app;
        }

        location @app {
            include uwsgi_params;
            uwsgi_pass unix:/home/username/TechEventRadar/eventradar.sock; # uWSGI socket yolunu kontrol et
        }

        location /static/ {
            root /home/username/TechEventRadar/; # Burası /home/username/TechEventRadar/static/ olmalı
            expires 30d;
            add_header Cache-Control "public";
            try_files $uri =404;
        }
    }
    ```
    * Bu yapılandırma dosyasına sembolik link oluşturun:
        ```bash
        sudo ln -s /etc/nginx/sites-available/eventradar.dev /etc/nginx/sites-enabled/
        ```
    * Nginx'in statik dosyalara ve ana dizine erişebilmesi için gerekli izinleri verin:
        ```bash
        sudo chmod o+x /home/username/
        sudo find /home/username/TechEventRadar/static -type d -exec chmod 755 {} +
        sudo find /home/username/TechEventRadar/static -type f -exec chmod 644 {} +
        ```
    * Nginx yapılandırmasını test edin ve yeniden yükleyin:
        ```bash
        sudo nginx -t
        sudo systemctl reload nginx
        ```

6.  **Tarayıcınızda Açın:**
    Nginx ve Docker Compose düzgün çalıştığında, tarayıcınızda yapılandırdığınız alan adı (örn: `https://eventradar.dev/`) üzerinden uygulamaya erişebilirsiniz. Etkinlikleri görüntüleyebilir ve "Verileri Güncelle" butonuna tıklayarak verileri web arayüzünden güncelleyebilirsiniz.

## 📂 Proje Yapısı

```bash
TechEventRadar/
├── main.py                 # Scraper'ları çalıştıran ana dosya (PostgreSQL'e yazar)
├── app.py                  # Flask web uygulaması (PostgreSQL'den okur)
├── docker-compose.yml      # Docker Compose yapılandırması (Uygulama ve PostgreSQL)
├── Dockerfile              # Flask uygulamasının Docker imajı tanımı
├── run_daily_scrape.py     # Otomatik günlük veri çekme scripti (cronjob için ideal)
├── scrapers/               # Etik sebepler gereği sizin yazmanız gerekmekte
├── templates/              # HTML şablonlarının bulunduğu dizin
│   └── index.html          # Ana sayfa HTML şablonu
└── static/                 # CSS, JavaScript, resimler gibi statik dosyalar
    ├── css/                # CSS dosyaları
    │   └── style.css
    └── images/             # Resim dosyaları
        └── default-event.jpg # veya placeholder-image.jpeg
```

🤝 Katkıda Bulunma

Projeye katkıda bulunmanızdan mutluluk duyarım! Nasıl katkıda bulunabileceğinizi öğrenmek için lütfen Katkıda Bulunma Rehberi dosyasını inceleyin.

📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için LICENSE dosyasına bakın.
