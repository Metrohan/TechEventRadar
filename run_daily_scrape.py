import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)

from app import app, save_events_to_db, initialize_database 

from scrapers.a_scraper import scrape_a_events
from scrapers.b_scraper import scrape_b_events
from scrapers.c_scraper import scrape_c_events
from scrapers.d_scraper import scrape_d_events
from scrapers.e_scraper import scrape_e_events

SCRAPERS = {
    "Platform A": scrape_a_events,
    "Platform B": scrape_b_events,
    "Platform C": scrape_c_events,
    "Platform D": scrape_d_events,
    "Platform E": scrape_e_events,
}

def scrape_source(scraper_func, source_name):
    print(f"\n--- {source_name} Scraper Başlatılıyor ---")
    try:
        if hasattr(scraper_func, '__name__'):
            print(f"{source_name} etkinlikleri çekiliyor: {scraper_func.__module__}.{scraper_func.__name__}")
        else:
            print(f"{source_name} etkinlikleri çekiliyor.")

        events = scraper_func()
        print(f"{source_name}'ten {len(events)} etkinlik çekildi.")
        return events
    except Exception as e:
        print(f"Hata: {source_name} scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_scraper_and_save_to_db():
    print(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    with app.app_context(): 
        initialize_database() 

        all_scraped_events = [] 

        with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as executor:
            futures = {executor.submit(scrape_source, func, name): name for name, func in SCRAPERS.items()}

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    events = future.result() 
                    if events:
                        all_scraped_events.extend(events) 
                        print(f"{source_name} scraper'ından {len(events)} etkinlik başarıyla çekildi.")
                    else:
                        print(f"{source_name} scraper'ından etkinlik çekilemedi veya bir hata oluştu.")
                except Exception as exc:
                    print(f'{source_name} scraper çalışırken beklenmedik bir hata oluştu (ThreadPoolExecutor): {exc}')

        if all_scraped_events:
            print("\n--- Tüm Çekilen Etkinlikler Veritabanına Kaydediliyor ---")
            save_events_to_db(all_scraped_events, "Tüm Kaynaklar") 
        else:
            print("\nHiçbir etkinlik çekilemedi veya kaydedilecek etkinlik bulunamadı.")
        
        print("\nVeritabanına kaydetme işlemi tamamlandı.")

    print(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")


if __name__ == "__main__":
    run_scraper_and_save_to_db()