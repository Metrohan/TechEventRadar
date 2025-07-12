from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time 

def scrape_techcareer_events():
    base_url = "https://www.techcareer.net"
    categories = {
        "Bootcamp": "/bootcamp"
    }

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_events = []

    try:
        for category_name, path in categories.items():
            url = f"{base_url}{path}"
            print(f"TechCareer.net {category_name} çekiliyor: {url}")
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until( 
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="single-event-box"]'))
                )
                print(f"DEBUG: {category_name} - İlk etkinlik kartı bulundu.")
                time.sleep(5)
            except Exception as e:
                print(f"DEBUG: {category_name} sayfası için etkinlik kartları bulunamadı veya ilk yükleme başarısız oldu: {e}")
                continue 

            last_height = driver.execute_script("return document.body.scrollHeight")
            previous_event_count = 0
            no_new_content_count = 0
            max_no_new_content_attempts = 2

            initial_soup = BeautifulSoup(driver.page_source, 'html.parser')
            previous_event_count = len(initial_soup.find_all(attrs={"data-test": "single-event-box"}))
            print(f"DEBUG: {category_name} - Başlangıç etkinlik sayısı: {previous_event_count}, Sayfa Yüksekliği: {last_height}")


            while True:

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"DEBUG: {category_name} - Sayfa aşağı kaydırıldı.")
                time.sleep(4)


                new_height = driver.execute_script("return document.body.scrollHeight")


                current_soup = BeautifulSoup(driver.page_source, 'html.parser')
                current_event_count = len(current_soup.find_all(attrs={"data-test": "single-event-box"}))
                
                print(f"DEBUG: {category_name} - Şu anki etkinlik sayısı: {current_event_count}, Yeni Sayfa Yüksekliği: {new_height}")


                if new_height == last_height and current_event_count == previous_event_count:
                    no_new_content_count += 1
                    print(f"DEBUG: {category_name} - İçerik veya yükseklik değişmedi. Deneme: {no_new_content_count}/{max_no_new_content_attempts}")
                    if no_new_content_count > max_no_new_content_attempts:
                        print(f"DEBUG: {category_name} sayfasında {max_no_new_content_attempts} ardışık kaydırma denemesinde yeni etkinlik/yükseklik bulunamadı, durduruluyor.")
                        break
                else:
                    no_new_content_count = 0

                last_height = new_height
                previous_event_count = current_event_count
                

            soup = BeautifulSoup(driver.page_source, 'html.parser')


            event_cards = soup.find_all(attrs={"data-test": "single-event-box"})

            if not event_cards:
                print(f"DEBUG: {category_name} sayfasında 'data-test=\"single-event-box\"' niteliğine sahip etkinlik kartları bulunamadı.")
            else:
                print(f"DEBUG: {category_name} - Toplam bulunan etkinlik kartı sayısı (final): {len(event_cards)}")


            for card in event_cards:
                title = "Başlık Bulunamadı"
                link = "Link Bulunamadı"
                date = "Tarih Bulunamadı"
                status = "Bilinmiyor"
                

                if 'href' in card.attrs:
                    link = card['href'].strip()
                    if not link.startswith('http'):
                        link = base_url + link


                title_element = card.find('h3', attrs={"data-test": "single-event-title"})
                if title_element:
                    title = title_element.text.strip()
                

                date_element = card.find('div', attrs={"data-test": "single-event-date"})
                if date_element:
                    date = date_element.text.strip()

                image_element = card.find('img', attrs={"data-test": "single-event-image"})
                if image_element and 'src' in image_element.attrs:
                    full_image_url = image_element['src']
                    if full_image_url.startswith('/_next/image'):
                        from urllib.parse import urlparse, parse_qs
                        parsed_url = urlparse(full_image_url)
                        query_params = parse_qs(parsed_url.query)
                        if 'url' in query_params:
                            image_url_raw = query_params['url'][0]
                            if not image_url_raw.startswith('http'):
                                image_url = base_url + image_url_raw
                            else:
                                image_url = image_url_raw
                        else:
                            image_url = base_url + full_image_url
                    elif not full_image_url.startswith('http'):
                        image_url = base_url + full_image_url
                    else:
                        image_url = full_image_url
                
                open_button = card.find('button', attrs={"data-test": "single-event-open-btn"})
                closed_button = card.find('button', attrs={"data-test": "single-event-closed-btn"})
                
                if open_button:
                    status = "Açık"
                elif closed_button:
                    status = "Kapalı"
                else:
                    status = "Bilinmiyor" 

                if status == "Açık" and title != "Başlık Bulunamadı": 
                    all_events.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'category': category_name,
                        'status': status,
                        'image_url': image_url
                    })
                # else:
                #     print(f"Kapalı/Bilinmeyen ilan atlandı: {title} (Kategori: {category_name}, Durum: {status})")

    except Exception as e:
        print(f"TechCareer.net çekilirken genel bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

    return all_events


if __name__ == "__main__":
    techcareer_events = scrape_techcareer_events()
    if techcareer_events:
        print("\n--- TechCareer.net Açık Etkinlikler ---")
        for event in techcareer_events:
            print(f"Kategori: {event['category']}")
            print(f"Başlık: {event['title']}")
            print(f"Link: {event['link']}")
            print(f"Tarih: {event['date']}")
            print(f"Durum: {event['status']}")
            print("------------------------------------")
    else:
        print("TechCareer.net'te açık etkinlik bulunamadı veya çekilirken sorun oluştu.")