from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from datetime import datetime
MAX_LOAD_ATTEMPTS = 2

def parse_turkish_date(date_string):
    """
    Türkçe tarih stringini datetime objesine çevirir.
    Örnek: "11 Ağustos 2025 Pzt 12:00" veya "10 Ağustos 2025 Paz"
    """
    months_turkish = {
        'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4, 'Mayıs': 5, 'Haziran': 6,
        'Temmuz': 7, 'Ağustos': 8, 'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12
    }
    
    parts = date_string.split()
    day = int(parts[0])
    month = months_turkish[parts[1]]
    year = int(parts[2])
    
    if len(parts) > 4:
        time_part = parts[4]
        hour, minute = map(int, time_part.split(':'))
        return datetime(year, month, day, hour, minute)
    else:
        return datetime(year, month, day)

def get_event_details(driver, event_url):
    """
    Etkinlik detay sayfasından 'Etkinlik Başlangıç', 'Etkinlik Bitiş' ve 'Son Başvuru' tarihlerini çeker.
    """
    event_start_date_str = "Başlangıç Tarihi Bulunamadı"
    event_end_date_str = "Bitiş Tarihi Bulunamadı"
    application_deadline_str = "Son Başvuru Tarihi Bulunamadı"

    try:
        driver.get(event_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-job_detail_content_list"))
        )
        time.sleep(2)

        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        detail_list_items = detail_soup.find_all('div', class_='c-job_detail_content_list')

        for item in detail_list_items:
            feature_box = item.find('div', class_='c-job_detail_content_list_features')
            if feature_box:
                title_tag = feature_box.find('h6')
                date_tag = feature_box.find('small')
                
                if title_tag and date_tag:
                    title = title_tag.text.strip()
                    date_text = date_tag.text.strip()

                    if "Etkinlik Başlangıç" in title:
                        event_start_date_str = date_text
                    elif "Etkinlik Bitiş" in title:
                        event_end_date_str = date_text
                    elif "Son Başvuru" in title:
                        application_deadline_str = date_text
        
    except Exception as e:
        print(f"Hata: Etkinlik detayları çekilirken sorun oluştu {event_url}: {e}")
    
    return event_start_date_str, event_end_date_str, application_deadline_str


def scrape_youthall_events():
    base_url = "https://www.youthall.com"
    events_url = "https://www.youthall.com/tr/events/" 

    print(f"\n--- Youthall Scraper Başlatılıyor ---")
    print(f"Youthall etkinlikleri çekiliyor: {events_url}")

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    all_events = []
    current_date = datetime.now() # Mevcut tarih ve saat

    try:
        driver.get(events_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "events"))
        )
        time.sleep(3) 

        current_attempts = 0
        while current_attempts < MAX_LOAD_ATTEMPTS:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"Youthall: Sayfa aşağı kaydırıldı (Deneme: {current_attempts + 1}/{MAX_LOAD_ATTEMPTS}).")
                time.sleep(3) 
                
                current_attempts += 1
            except Exception as e:
                print(f"Youthall: Daha fazla içerik yüklenemedi veya 'Daha Fazla' butonu bulunamadı. ({e})")
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        event_cards = soup.find_all('div', class_='events box_hover border-line-light-blue')

        if not event_cards:
            print("Hata: Youthall sayfasında etkinlik kartları bulunamadı. Lütfen selector'ı veya sayfa yüklenme durumunu kontrol edin.")
            return []

        for card in event_cards:
            title = "Başlık Bulunamadı"
            link = "Link Bulunamadı"
            image_url = "Resim Bulunamadı"
            category = "Etkinlik"
            status = "Açık"

            link_element = card.find('a', href=True)
            if link_element and 'href' in link_element.attrs:
                link = urljoin(base_url, link_element['href'].strip())

            title_element = card.find('div', class_='events__content__title')
            if title_element and title_element.find('h2'):
                title = title_element.find('h2').text.strip()
            
            image_element = card.find('img') 
            if image_element and 'src' in image_element.attrs:
                raw_image_src = image_element['src'].strip()
                if raw_image_src:
                    image_url = raw_image_src 

            all_list_items = card.find_all('li')
            for li in all_list_items:
                if li.find('i', class_='fa fa-hashtag'):
                    category = li.text.replace('fa-hashtag', '').strip().replace('#', '').strip()
                    break 
            
            event_start_date_str, event_end_date_str, application_deadline_str = "","",""
            if link != "Link Bulunamadı":
                print(f"Youthall: Detayları çekmek için linke gidiliyor: {link}")
                event_start_date_str, event_end_date_str, application_deadline_str = get_event_details(driver, link)
            
            is_active = False
            
            if application_deadline_str != "Son Başvuru Tarihi Bulunamadı":
                try:
                    deadline_date = parse_turkish_date(application_deadline_str)
                    if deadline_date >= current_date.replace(hour=0, minute=0, second=0, microsecond=0): 
                        is_active = True
                    else:
                        is_active = False
                except ValueError:
                    print(f"Youthall: Son başvuru tarihi parse edilemedi: {application_deadline_str}. Etkinlik pasif kabul ediliyor.")
                    is_active = False
            else:
                if event_start_date_str != "Başlangıç Tarihi Bulunamadı":
                    try:
                        start_date = parse_turkish_date(event_start_date_str)
                        end_date = parse_turkish_date(event_end_date_str) if event_end_date_str != "Bitiş Tarihi Bulunamadı" else start_date
                        
                        if (start_date <= current_date and end_date >= current_date) or (start_date > current_date):
                            is_active = True
                    except ValueError:
                        print(f"Youthall: Etkinlik başlangıç/bitiş tarihi parse edilemedi: Başlangıç: {event_start_date_str}, Bitiş: {event_end_date_str}. Etkinlik pasif kabul ediliyor.")
                        is_active = False
            
            if is_active:
                final_date = ""
                if application_deadline_str != "Son Başvuru Tarihi Bulunamadı" and \
                   parse_turkish_date(application_deadline_str) >= current_date.replace(hour=0, minute=0, second=0, microsecond=0):
                    final_date = f"Son Başvuru: {application_deadline_str}"
                elif event_start_date_str != "Başlangıç Tarihi Bulunamadı":
                    final_date = f"Başlangıç: {event_start_date_str}"
                
                date = final_date 

                if title != "Başlık Bulunamadı" and link != "Link Bulunamadı":
                    all_events.append({
                        'title': title,
                        'link': link,
                        'date': date, 
                        'category': category,
                        'status': status,
                        'image_url': image_url,
                        'event_start_date': event_start_date_str, 
                        'event_end_date': event_end_date_str,     
                        'application_deadline': application_deadline_str 
                    })
                else:
                    print(f"Hata: Geçersiz veya eksik bilgiye sahip etkinlik atlandı: {title}")
            else:
                print(f"Youthall: Geçmiş tarihli veya başvuru süresi dolmuş etkinlik atlandı: {title}")


        print(f"Youthall'dan {len(all_events)} aktif etkinlik başarıyla çekildi.")
        return all_events

    except Exception as e:
        print(f"Hata: Youthall scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc() 
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    open_events = scrape_youthall_events()
    if open_events:
        print("\n--- Youthall Aktif Etkinlikler ---")
        for event in open_events:
            print(f"Başlık: {event['title']}")
            print(f"Link: {event['link']}")
            print(f"Tarih (Liste Sayfasından): {event.get('date', 'Liste Tarihi Yok')}") 
            print(f"Etkinlik Başlangıç Tarihi: {event['event_start_date']}")
            print(f"Etkinlik Bitiş Tarihi: {event['event_end_date']}")
            print(f"Son Başvuru Tarihi: {event['application_deadline']}")
            print(f"Tür: {event['category']}")
            print(f"Durum: {event['status']}")
            print(f"Görsel URL: {event['image_url']}")
            print("------------------------------------")
    else:
        print("Youthall'da aktif etkinlik bulunamadı.")