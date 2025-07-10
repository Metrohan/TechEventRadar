import requests
from bs4 import BeautifulSoup

def scrape_anbean_events():
    url = "https://anbeankampus.co/etkinlikler/"
    print(f"Anbean Kampüs etkinlikleri çekiliyor: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"URL'ye erişilirken hata oluştu: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []

    event_cards = soup.find_all('div', class_='mini-eventCard')

    if not event_cards:
        print("Anbean Kampüs sayfasında etkinlik kartları bulunamadı. Selector'ı kontrol edin.")

    for card in event_cards:
        main_link_element = card.find('a', title=True)
        link = main_link_element['href'].strip() if main_link_element and 'href' in main_link_element.attrs else "Link Bulunamadı"
        if link != "Link Bulunamadı" and not link.startswith('http'):
            link = "https://anbeankampus.co" + link

        title = main_link_element['title'].strip() if main_link_element and 'title' in main_link_element.attrs else "Başlık Bulunamadı"

        date_items = card.find('div', class_='mini-eventCard-dates')
        last_application_date = "Tarih Bulunamadı"
        if date_items:
            for item in date_items.find_all('div', class_='mini-eventCard-dateItem'):
                spans = item.find_all('span')
                if len(spans) == 2 and (spans[0].text.strip() == "Son Başvuru" or spans[0].text.strip() == "Son Kayıt"):
                    last_application_date = spans[1].text.strip()
                    break
        
        category_div = card.find('div', class_='mini-eventCard-headerType')
        category = category_div.find('span').text.strip() if category_div and category_div.find('span') else "Kategori Bulunamadı"

        is_application_open = False
        status_closed_badge = card.find('span', class_='mini-eventCard-statusBadge text-danger')
        if status_closed_badge and "Başvurular Tamamlandı" in status_closed_badge.text:
            is_application_open = False
        else:
            detail_button = card.find('button', class_='btn-primary')
            if detail_button and "Detaylı Bilgi" in detail_button.text:
                is_application_open = True

        if is_application_open:
            events.append({
                'title': title,
                'link': link,
                'date': last_application_date,
                'category': category,
                'status': 'Açık' 
            })
        else:
            #print(f"Kapalı ilan atlandı: {title}")
            pass

    return events

if __name__ == "__main__":
    open_events = scrape_anbean_events()
    if open_events:
        print("\n--- Anbean Kampüs Açık Etkinlikler ---")
        for event in open_events:
            print(f"Başlık: {event['title']}")
            print(f"Link: {event['link']}")
            print(f"Tarih: {event['date']}")
            print(f"Tür: {event['category']}")
            print(f"Durum: {event['status']}")
            print("------------------------------------")

    else:
        print("Anbean Kampüs'te açık etkinlik bulunamadı.")