import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Proje kök dizinini Python yoluna ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)

# app.py'den Flask uygulaması örneğini, save_events_to_db ve initialize_database fonksiyonunu import et
# db ve Event modellerini doğrudan kullanmayacağımız için sadece app, save_events_to_db ve initialize_database'i import ediyoruz.
from app import app, save_events_to_db, initialize_database 

# Tüm scraper fonksiyonlarını import et
from scrapers.techcareer_scraper import scrape_techcareer_events
from scrapers.cs_scraper import scrape_coderspace_events
from scrapers.anbean_scraper import scrape_anbean_events
from scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
from scrapers.youthall_scraper import scrape_youthall_events

# Scraper ve kaynak adlarını eşleştiren bir sözlük
SCRAPERS = {
    "TechCareer.net": scrape_techcareer_events,
    "Coderspace": scrape_coderspace_events,
    "Anbean": scrape_anbean_events,
    "Kodluyoruz": scrape_kodluyoruz_events,
    "Youthall": scrape_youthall_events,
}

def scrape_source(scraper_func, source_name):
    """Belirli bir kaynaktan etkinlikleri çeker ve döndürür."""
    print(f"\n--- {source_name} Scraper Başlatılıyor ---")
    try:
        if hasattr(scraper_func, '__name__'): # Fonksiyon adını daha güvenli al
            print(f"{source_name} etkinlikleri çekiliyor: {scraper_func.__module__}.{scraper_func.__name__}")
        else:
            print(f"{source_name} etkinlikleri çekiliyor.")

        events = scraper_func()
        print(f"{source_name}'ten {len(events)} etkinlik çekildi.")
        return events
    except Exception as e:
        print(f"Hata: {source_name} scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc() # Hatanın detaylarını yazdır
        return None # Hata durumunda boş liste yerine None döndür

def run_scraper_and_save_to_db():
    """Tüm scraper'ları çalıştırır ve verileri veritabanına kaydeder."""
    print(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # Flask uygulama bağlamı içinde çalıştır
    # Bu blok, Flask'ın veritabanı bağlantılarını ve diğer uzantılarını düzgün şekilde kullanabilmesi için önemlidir.
    with app.app_context(): 
        initialize_database() # <-- Veritabanı tablolarını burada oluşturuyoruz/kontrol ediyoruz

        all_scraped_events = [] # Tüm scraper'lardan gelen etkinlikleri tutmak için

        # ThreadPoolExecutor kullanarak scraper'ları eşzamanlı çalıştır
        with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as executor:
            # Her bir scraper fonksiyonu için bir future (gelecek) oluştur
            futures = {executor.submit(scrape_source, func, name): name for name, func in SCRAPERS.items()}

            # Futures tamamlandıkça sonuçları işle
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    events = future.result() # Scraper'dan gelen etkinlikleri al
                    if events:
                        all_scraped_events.extend(events) # Etkinlikleri ana listeye ekle
                        print(f"{source_name} scraper'ından {len(events)} etkinlik başarıyla çekildi.")
                    else:
                        print(f"{source_name} scraper'ından etkinlik çekilemedi veya bir hata oluştu.")
                except Exception as exc:
                    # scrape_source içinde zaten hata basıldığı için burada tekrar basmaya gerek yok
                    print(f'{source_name} scraper çalışırken beklenmedik bir hata oluştu (ThreadPoolExecutor): {exc}')
                    # traceback.print_exc() # Detaylı hata için açılabilir

        # Tüm etkinlikler toplandıktan sonra veritabanına kaydet
        if all_scraped_events:
            print("\n--- Tüm Çekilen Etkinlikler Veritabanına Kaydediliyor ---")
            save_events_to_db(all_scraped_events, "Tüm Kaynaklar") # Tüm etkinlikleri tek seferde kaydet
        else:
            print("\nHiçbir etkinlik çekilemedi veya kaydedilecek etkinlik bulunamadı.")
        
        print("\nVeritabanına kaydetme işlemi tamamlandı.")

    print(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")


if __name__ == "__main__":
    run_scraper_and_save_to_db()