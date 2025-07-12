from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
MAX_LOAD_ATTEMPTS = 0

def scrape_kodluyoruz_events():
    url = "https://www.kodluyoruz.org/programlar"
    base_url = "https://www.kodluyoruz.org"

    print(f"\n--- Kodluyoruz Scraper Başlatılıyor ---")
    print(f"Kodluyoruz etkinlikleri çekiliyor: {url}")

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "all-programs-tabs"))
        )
        time.sleep(2)

        try:
            target_tab_xpath = "//a[contains(@class, 'all-programs-tabs')]//div[contains(@class, 'all-program-tap-text') and contains(text(), 'Genç & Genç Yetişkinler İçin')]"
            
            target_tab_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, target_tab_xpath))
            )
            driver.execute_script("arguments[0].click();", target_tab_div.find_element(By.XPATH, ".."))
            print("✔ 'Genç & Genç Yetişkinler İçin' sekmesine tıklandı.")
            time.sleep(3)

        except Exception as e:
            print(f"Uyarı: 'Genç & Genç Yetişkinler İçin' sekmesine tıklanırken sorun oluştu: {e}")
            print("Sayfa varsayılan sekmede taranmaya devam edecek.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        events = []

        event_cards = soup.find_all('div', class_='program-erik-wrap')

        if not event_cards:
            print("Hata: Kodluyoruz sayfasında 'program-erik-wrap' sınıfına sahip etkinlik kartları bulunamadı.")
            print("Lütfen selector'ı veya sayfa yüklenme durumunu kontrol edin.")
            return []

        for card in event_cards:
            title = "Başlık Bulunamadı"
            link = "Link Bulunamadı"
            date = "Tarih Bulunamadı"
            image_url = "Resim Bulunamadı"
            category = "Kategori Bulunamadı"
            status = "Bilinmiyor"

            title_element = card.find('h5', class_='program-ad programlar')
            if title_element:
                title = title_element.text.strip()

            link_element = card.find('a', class_='program-btn')
            if link_element and 'href' in link_element.attrs:
                link = urljoin(base_url, link_element['href'].strip())

            date_flex_divs = card.find_all('div', class_='program-detay-flex')
            for div in date_flex_divs:
                detail_label = div.find('div', class_='program-detail')
                detail_value = div.find('div', class_='program-detail-tarih')
                if detail_label and detail_value and "Son Başvuru Tarihi:" in detail_label.text:
                    date = detail_value.text.strip()
                    break

            image_element = card.find('img', class_='program-img')
            if image_element and 'src' in image_element.attrs:
                raw_image_src = image_element['src'].strip()
                if raw_image_src:
                    image_url = urljoin(base_url, raw_image_src)
            
            format_category_element = card.find('div', class_='program-format')
            if format_category_element:
                category = format_category_element.text.strip()
            else:
                category = "Program"

            status = "Kapalı"
            active_apply_button = None
            apply_buttons = card.find_all('a', class_='program-btn', text="Şimdi Başvur")
            for btn in apply_buttons:
                if 'w-condition-invisible' not in btn.get('class', []):
                    active_apply_button = btn
                    break

            if active_apply_button:
                status = "Açık"
            else:
                status = "Kapalı"

            if status == "Açık" and title != "Başlık Bulunamadı" and link != "Link Bulunamadı":
                events.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'category': category,
                    'status': status, 
                    'image_url': image_url
                })
            else:
                pass

        print(f"Kodluyoruz'dan {len(events)} açık etkinlik başarıyla çekildi.")
        return events

    except Exception as e:
        print(f"Hata: Kodluyoruz scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    open_events = scrape_kodluyoruz_events()
    if open_events:
        print("\n--- Kodluyoruz Açık Etkinlikler ---")
        for event in open_events:
            print(f"Başlık: {event['title']}")
            print(f"Link: {event['link']}")
            print(f"Tarih: {event['date']}")
            print(f"Tür: {event['category']}")
            print(f"Durum: {event['status']}")
            print(f"Görsel URL: {event['image_url']}")
            print("------------------------------------")
    else:
        print("Kodluyoruz'da açık etkinlik bulunamadı.")