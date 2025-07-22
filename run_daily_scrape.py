from app import app, save_events_to_db
from scrapers.youthall_scraper import scrape_youthall_events

print("Scraper calismaya basladi...")

with app.app_context():
    print("Youthall etkinlikleri cekiliyor...")
    youthall_events = scrape_youthall_events()
    save_events_to_db(youthall_events, "Youthall")
    print("Youthall scraper calismasi tamamlandi.")

print("Tum scraper islemleri tamamlandi.")