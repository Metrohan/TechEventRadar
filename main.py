import os
import sys
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)


from scrapers.techcareer_scraper import scrape_techcareer_events
from scrapers.cs_scraper import scrape_coderspace_events
from scrapers.anbean_scraper import scrape_anbean_events
from scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
from scrapers.youthall_scraper import scrape_youthall_events

from data_manager import save_events_to_json, load_events_from_json, DATA_DIR


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

def run_scraper_and_save():
    print(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    all_scraped_events = []
    
    scrapers_to_run = [
        (scrape_techcareer_events, "TechCareer.net"),
        (scrape_coderspace_events, "Coderspace"),
        (scrape_anbean_events, "Anbean"),
        (scrape_kodluyoruz_events, "Kodluyoruz"),
        (scrape_youthall_events, "Youthall")
    ]
    with ThreadPoolExecutor(max_workers=5) as executor:

        futures = {executor.submit(scrape_source, func, name): name for func, name in scrapers_to_run}

        for future in as_completed(futures):
            source_name = futures[future]
            try:
                events = future.result()
                all_scraped_events.extend(events)
            except Exception as exc:
                print(f'{source_name} scraper bir istisna üretti: {exc}')
                import traceback
                traceback.print_exc()

    if all_scraped_events:
        print(f"\nToplam {len(all_scraped_events)} açık etkinlik çekildi tüm kaynaklardan.")
        save_events_to_json(all_scraped_events, "all_events.json")
    else:
        print("\nHiç açık etkinlik bulunamadı veya çekilemedi tüm kaynaklardan.")
    
    print(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    return all_scraped_events

if __name__ == "__main__":
    run_scraper_and_save()
