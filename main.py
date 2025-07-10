import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)

from scrapers.techcareer_scraper import scrape_techcareer_events
from scrapers.cs_scraper import scrape_coderspace_events
from scrapers.anbean_scraper import scrape_anbean_events

from data_manager import save_events_to_json, load_events_from_json

def scrape_all_sources():
    all_scraped_events = []

    print("\n--- 1. Scraper Başlatılıyor ---")
    try:
        techcareer_events = scrape_techcareer_events()
        if techcareer_events:
            print(f"TechCareer.net'ten {len(techcareer_events)} açık etkinlik çekildi.")
            all_scraped_events.extend(techcareer_events)
        else:
            print("TechCareer.net'ten etkinlik çekilemedi veya hiç açık etkinlik bulunamadı.")
    except Exception as e:
        print(f"Hata: 1. scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- 2. Scraper Başlatılıyor ---")
    try:
        coderspace_events = scrape_coderspace_events()
        if coderspace_events:
            print(f"Coderspace'ten {len(coderspace_events)} açık etkinlik çekildi.")
            all_scraped_events.extend(coderspace_events)
        else:
            print("Coderspace'ten etkinlik çekilemedi veya hiç açık etkinlik bulunamadı.")
    except Exception as e:
        print(f"Hata: 2. scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- 3. Scraper Başlatılıyor ---")
    try:
        anbean_events = scrape_anbean_events()
        if anbean_events:
            print(f"Anbean'dan {len(anbean_events)} açık etkinlik çekildi.")
            all_scraped_events.extend(anbean_events)
        else:
            print("Anbean'dan etkinlik çekilemedi veya hiç açık etkinlik bulunamadı.")
    except Exception as e:
        print(f"Hata: 3. scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()

    return all_scraped_events

def run_scraper_and_save():
    print(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    scraped_events = scrape_all_sources()

    if scraped_events:
        print(f"\nToplam {len(scraped_events)} açık etkinlik çekildi tüm kaynaklardan.")
        save_events_to_json(scraped_events, "all_events.json")
    else:
        print("\nHiç açık etkinlik bulunamadı veya çekilemedi tüm kaynaklardan.")
    print(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    return scraped_events

if __name__ == "__main__":
    run_scraper_and_save()
