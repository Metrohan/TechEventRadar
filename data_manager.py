import json
import os

DATA_DIR = 'data'

def save_events_to_json(events, filename="events.json"):
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
        print(f"Veriler başarıyla '{filepath}' dosyasına kaydedildi.")
    except IOError as e:
        print(f"Hata: Veriler '{filepath}' dosyasına kaydedilirken sorun oluştu: {e}")

def load_events_from_json(filename="events.json"):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Bilgi: '{filepath}' dosyası bulunamadı, boş liste döndürülüyor.")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            events = json.load(f)
        print(f"Veriler başarıyla '{filepath}' dosyasından yüklendi.")
        return events
    except json.JSONDecodeError as e:
        print(f"Hata: '{filepath}' dosyası okunurken JSON format hatası: {e}")
        return []
    except IOError as e:
        print(f"Hata: Veriler '{filepath}' dosyasından yüklenirken sorun oluştu: {e}")
        return []

if __name__ == "__main__":
    test_events = [
        {"title": "Test Etkinliği 1", "link": "http://test.com/1", "date": "10.07.2025", "category": "Test", "status": "Açık"},
        {"title": "Test Etkinliği 2", "link": "http://test.com/2", "date": "15.08.2025", "category": "Test", "status": "Kapalı"}
    ]
    
    print("\nTest: save_events_to_json")
    save_events_to_json(test_events, "test_events.json")

    print("\nTest: load_events_from_json")
    loaded_events = load_events_from_json("test_events.json")
    print(f"Yüklenen etkinlik sayısı: {len(loaded_events)}")
    if loaded_events:
        print(f"İlk yüklenen etkinlik: {loaded_events[0]['title']}")
    print("\nTest: Olmayan dosyayı yükle")
    empty_events = load_events_from_json("non_existent_file.json")
    print(f"Yüklenen etkinlik sayısı (olmayan dosya): {len(empty_events)}")