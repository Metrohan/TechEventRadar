
<img width="802" height="420" alt="Başlıksız(1)" src="https://github.com/user-attachments/assets/7528bb63-f02d-48cf-9cb9-f22e822128dd" />

# 🚀 TechEventRadar

Bu proje, çeşitli Türk teknoloji ve kariyer platformlarından güncel etkinlikleri (bootcamp'ler, hackathon'lar, yetenek programları vb.) çekmek, depolamak ve kullanıcı dostu bir web arayüzünde sunmak için geliştirilmiştir. Python, Selenium, BeautifulSoup ve Flask teknolojilerini kullanır.

## ✨ Özellikler

* **Çoklu Kaynak Desteği:** TechCareer.net, Coderspace ve Anbean gibi platformlardan veri çekme yeteneği.
* **Dinamik Veri Çekimi:** Selenium kullanarak JavaScript ile yüklenen dinamik içerikleri sorunsuz bir şekilde işler.
* **Kullanıcı Dostu Web Arayüzü:** Çekilen etkinlikleri kategoriye göre gruplandırılmış, görselliği ön planda tutan modern bir arayüzde sunar.
* **Tek Tıkla Güncelleme:** Web arayüzü üzerinden "Verileri Güncelle" butonu ile en güncel etkinlikleri anında çekme imkanı.
* **Durum Takibi:** Etkinliklerin son güncelleme zamanını ve toplam etkinlik sayısını gösterir.
* **Desteklenen Platformlar:** Coderspace, Youthall, Anbean, Kodluyoruz, Techcareer.

## 🛠️ Teknolojiler

* **Python:** Backend scraping mantığı ve Flask uygulaması için ana dil.
* **Flask:** Hafif ve esnek bir Python web çatısı ile web arayüzünü oluşturur.
* **Selenium:** Dinamik web sitelerinden veri çekmek için kullanılır.
* **BeautifulSoup4:** Çekilen HTML içeriğini ayrıştırmak için kullanılır.
* **WebDriver-Manager:** Selenium WebDriver'ları otomatik olarak yönetir.
* **HTML/CSS/JavaScript:** Web arayüzünün frontend tasarımı ve etkileşimi için.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde kurmak ve çalıştırmak için aşağıdaki adımları izleyin.

### Önkoşullar

* [Python 3.8+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads) (Repoyu klonlamak için)
* [Google Chrome](https://www.google.com/chrome/) (Selenium için tarayıcı)

### Adımlar

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/Metrohan/TechEventRadar.git
    cd TechEventRadar
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Scraper'ları Çalıştırın ve Verileri Çekin (İlk Kez veya Manuel Güncelleme İçin):**
    ```bash
    python main.py
    ```
    Bu komut, tanımlı tüm kaynaklardan etkinlik verilerini çekecek ve `data/all_events.json` dosyasına kaydedecektir. Ayrıca `data/last_update.json` dosyasına son güncelleme zamanını kaydeder.

4.  **Web Arayüzünü Başlatın:**
    ```bash
    python app.py
    ```
    Uygulama başlatıldığında terminalde genellikle `http://127.0.0.1:5000/` gibi bir adres göreceksiniz.

5.  **Tarayıcınızda Açın:**
    `app.py` başlatıldıktan sonra tarayıcınızda otomatik olarak açılacaktır. Etkinlikleri görüntüleyebilir ve "Verileri Güncelle" butonuna tıklayarak verileri web arayüzünden güncelleyebilirsiniz.


## 🚀 Otomatik Çalıştırma Scriptleri

Projeyi daha kolay çalıştırmak için platforma özel scriptleri kullanabilirsiniz. Bu scriptler, önkoşulları kontrol eder ve bağımlılıkları yükler.

**Windows İçin (run_scraper.bat) 💻**

run_scraper.bat dosyasına çift tıklayarak veya Komut İstemi'nden çalıştırabilirsiniz:
```bash
.\run_scraper.bat
```
**Linux / macOS İçin (run_scraper.sh) 🐧🍏**

Terminalden run_scraper.sh dosyasına çalıştırma izni verin ve ardından çalıştırın:

```bash
chmod +x run_scraper.sh
./run_scraper.sh
```

## 📂 Proje Yapısı
```bash
TechEventRadar/
├── main.py                 # Scraper'ları çalıştıran ana dosya
├── data_manager.py         # Çekilen verileri JSON'a kaydeder/yükler
├── app.py                  # Flask web uygulaması
├── run_scraper.sh          # Linux/macOS için otomatik çalıştırma scripti
├── run_scraper.bat         # Windows için otomatik çalıştırma scripti
├── scrapers/               # Web scraper modüllerinin bulunduğu dizin
│   ├── techcareer_scraper.py
│   ├── cs_scraper.py  
│   ├── kodluyoruz_scraper.py  
│   ├── youthall_scraper.py 
│   └── anbean_scraper.py 
├── data/                   # Çekilen verilerin depolandığı dizin
│   ├── all_events.json     # Tüm etkinlik verileri
│   └── last_update.json    # Son güncelleme zamanı bilgisi
├── templates/              # HTML şablonlarının bulunduğu dizin
│   └── index.html          # Ana sayfa HTML şablonu
└── static/                 # CSS, JavaScript, resimler gibi statik dosyalar
    └── style.css           # Uygulamanın stil dosyası
```

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmanızdan mutluluk duyarım! Nasıl katkıda bulunabileceğinizi öğrenmek için lütfen [Katkıda Bulunma Rehberi](CONTRIBUTING.md) dosyasını inceleyin.

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

---
