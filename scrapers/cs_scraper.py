from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_coderspace_events():
    url = "https://coderspace.io/etkinlikler"
    print(f"Coderspace etkinlikleri çekiliyor: {url}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    events = []

    try:
        driver.get(url)

       
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.events-live-list div.col-12'))
        )
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        event_cards = soup.find_all('div', class_='col-12 col-lg-6 col-xl-4')

        if not event_cards:
            print("Coderspace sayfasında etkinlik kartları (col-12 div'leri) bulunamadı.")
            return []

        for card_col_div in event_cards:
            card = card_col_div.find('div', class_='event-card')
            if not card:
                continue

            title_link_element = card.find('h5', class_='mt-3')
            if title_link_element:
                title_link_element = title_link_element.find('a')
            
            title = title_link_element.text.strip() if title_link_element else "Başlık Bulunamadı"
            link = title_link_element['href'].strip() if title_link_element and 'href' in title_link_element.attrs else "Link Bulunamadı"
            
            if link != "Link Bulunamadı" and not link.startswith('http'):
                link = "https://coderspace.io" + link

            last_application_date = "Tarih Bulunamadı"
            info_list = card.find('ul', class_='event-card-info')
            if info_list:
                for item in info_list.find_all('li'):
                    spans = item.find_all('span')
                    strong_tag = item.find('strong')
                    if len(spans) > 0 and spans[0].text.strip() == "Son Başvuru" and strong_tag:
                        last_application_date = strong_tag.text.strip()
                        break
            
            category_element = card.find('span', class_='event-card-type')
            category = category_element.text.strip() if category_element else "Kategori Bulunamadı"

            is_application_open = False 
            
            main_button = card.find('a', class_='primary-button--big')
            
            if main_button:

                if 'primary-button--disabled' in main_button.get('class', []):
                    is_application_open = False
                else:
                    is_application_open = True

            if is_application_open:
                events.append({
                    'title': title,
                    'link': link,
                    'date': last_application_date,
                    'category': category,
                    'status': 'Açık' 
                })
            # else:
            #     print(f"Kapalı/Bilinmeyen ilan atlandı: {title}")

    except Exception as e:
        print(f"Coderspace çekilirken hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

    return events

if __name__ == "__main__":
    coderspace_events = scrape_coderspace_events()
    if coderspace_events:
        print("\n--- Coderspace Açık Etkinlikler ---")
        for event in coderspace_events:
            print(f"Başlık: {event['title']}")
            print(f"Link: {event['link']}")
            print(f"Tarih: {event['date']}")
            print(f"Kategori: {event['category']}")
            print(f"Durum: {event['status']}")
            print("------------------------------------")
    else:
        print("Coderspace'te açık etkinlik bulunamadı veya çekilirken sorun oluştu.")