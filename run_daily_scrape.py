import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)

from app import app, save_events_to_db

from scrapers.techcareer_scraper import scrape_techcareer_events
from scrapers.cs_scraper import scrape_coderspace_events
from scrapers.anbean_scraper import scrape_anbean_events
from scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
from scrapers.youthall_scraper import scrape_youthall_events


def scrape_source(scraper_func, source_name):
    print(f"\n--- {source_name} Scraper Başlatılıyor ---")
    try:
        events = scraper_func()
        if events:
            print(f"{source_name}'ten {len(events)} açık etkinlik çekildi.")
            return events
        else:
            print(f"{source_name}'ten etkinlik çekilemedi veya hiç açık etkinlik bulunamadı.")
            return []
    except Exception as e:
        print(f"Hata: {source_name} scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
        return []

def run_scraper_and_save_to_db():
    print(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    scrapers_to_run = [
        (scrape_techcareer_events, "TechCareer.net"),
        (scrape_coderspace_events, "Coderspace"),
        (scrape_anbean_events, "Anbean"),
        (scrape_kodluyoruz_events, "Kodluyoruz"),
        (scrape_youthall_events, "Youthall")
    ]

    with app.app_context():
        
        with ThreadPoolExecutor(max_workers=len(scrapers_to_run)) as executor:
            futures = {executor.submit(scrape_source, func, name): name for func, name in scrapers_to_run}

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    events = future.result()
                    if events:
                        print(f"{source_name} etkinlikleri veritabanına kaydediliyor...")
                        save_events_to_db(events, source_name) 
                except Exception as exc:
                    print(f'{source_name} scraper veritabanına kaydederken bir istisna üretti: {exc}')
                    import traceback
                    traceback.print_exc()
        
        print("\nVeritabanına kaydetme işlemi tamamlandı.")

    print(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")


if __name__ == "__main__":
    run_scraper_and_save_to_db()