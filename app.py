import os
from flask import Flask, jsonify, request
from scrapers.youthall_scraper import scrape_youthall_events
from models import db, Event
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def save_events_to_db(events_data, platform_name):
    with app.app_context():
        new_events_count = 0
        for event_data in events_data:
            try:
                existing_event = Event.query.filter_by(url=event_data['url']).first()
                if existing_event:
                    continue

                new_event = Event(
                    platform=platform_name,
                    title=event_data['title'],
                    url=event_data['url'],
                    start_date=event_data.get('start_date'),
                    end_date=event_data.get('end_date'),
                    application_deadline=event_data.get('application_deadline'),
                    category=event_data.get('category'),
                    is_paid=event_data.get('is_paid'),
                    image_url=event_data.get('image_url'),
                    location=event_data.get('location')
                )
                db.session.add(new_event)
                new_events_count += 1
            except Exception as e:
                print(f"Etkinlik eklenirken hata oluştu (URL: {event_data.get('url')}): {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print(f"Veritabanına {new_events_count} yeni etkinlik kaydedildi.")
        except IntegrityError:
            db.session.rollback() 
            print("Veritabanına kaydederken URL benzersizlik hatası oluştu. Bazı etkinlikler atlanmış olabilir.")
        except Exception as e:
            db.session.rollback()
            print(f"Genel bir veritabanı kaydetme hatası oluştu: {e}")

@app.route('/events', methods=['GET'])
def get_events():
    category = request.args.get('category')
    is_paid_param = request.args.get('is_paid')

    query = Event.query

    if category:
        query = query.filter_by(category=category)
    
    if is_paid_param:
        is_paid = True if is_paid_param.lower() == 'true' else False if is_paid_param.lower() == 'false' else None
        if is_paid is not None:
            query = query.filter_by(is_paid=is_paid)

    events = query.order_by(Event.timestamp.desc()).limit(100).all() 
    return jsonify([event.to_dict() for event in events])


@app.cli.command('create-db')
def create_db_command():
    """Veritabanı tablolarını oluşturur."""
    with app.app_context():
        db.create_all()
        print('Veritabanı tabloları oluşturuldu/güncellendi.')

if __name__ == '__main__':
    # Geliştirme ortamında veritabanı tablolarını oluşturmak için:
    # `flask create-db` komutunu terminalde çalıştırın
    # Veya aşağıdaki satırı geçici olarak uncomment edebilirsiniz.
    # with app.app_context():
    #     db.create_all()
    
    # Scraper'ı burada manuel olarak çalıştırmak isterseniz (geliştirme için)
    # print("Youthall etkinlikleri cekiliyor...")
    # youthall_events = scrape_youthall_events()
    # save_events_to_db(youthall_events, "Youthall")
    # print("Scraper calismasi tamamlandi.")

    app.run(debug=True, host='0.0.0.0', port=5000)