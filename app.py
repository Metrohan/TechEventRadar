import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from datetime import datetime
import json
import webbrowser

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)

from data_manager import load_events_from_json, DATA_DIR
from main import run_scraper_and_save

app = Flask(__name__)
app.secret_key = 'super_secret_key'

LAST_UPDATE_FILE = os.path.join(DATA_DIR, 'last_update.json')

def get_last_update_time():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_updated')
    return None

def set_last_update_time():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LAST_UPDATE_FILE, 'w') as f:
        json.dump({'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, f)

@app.route('/')
def index():
    events = load_events_from_json("all_events.json")
    last_updated = get_last_update_time()
    
    grouped_events = {}
    for event in events:
        category = event.get('category', 'Diğer')
        if category not in grouped_events:
            grouped_events[category] = []
        grouped_events[category].append(event)

    return render_template('index.html', grouped_events=grouped_events, 
                           last_updated=last_updated,
                           total_event_count=len(events))

@app.route('/update_data')
def update_data():
    print("\n[FLASK]: Veri güncelleme isteği alındı. Scraper çalıştırılıyor...")
    try:
        run_scraper_and_save()
        set_last_update_time()
        flash('Etkinlik verileri başarıyla güncellendi!', 'success')
    except Exception as e:
        flash(f'Veri güncellenirken bir hata oluştu: {e}', 'error')
        print(f"Hata: Scraper çağrılırken sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    reloader = False
    app_url = "http://127.0.0.1:5000/"
    print(f"Flask uygulaması başlatılıyor. Tarayıcınızda {app_url} adresi açılacak.")
    webbrowser.open(app_url)
    app.run(debug=True, use_reloader=reloader)