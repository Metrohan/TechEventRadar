import os
from flask import Flask, jsonify, request
from models import db, Event
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://app_user:your_strong_password_here@localhost:5432/event_scraper_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/events', methods=['GET'])
def get_events():
    try:
        events = Event.query.all()
        events_data = [
            {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date.isoformat() if event.date else None,
                'location': event.location,
                'url': event.url,
                'source': event.source,
                'is_active': event.is_active,
                'scraped_at': event.scraped_at.isoformat()
            } for event in events
        ]
        return jsonify(events_data)
    except Exception as e:
        app.logger.error(f"Etkinlikler çekilirken hata oluştu: {e}")
        return jsonify({"error": "Etkinlikler çekilirken bir sorun oluştu."}), 500

def save_events_to_db(events_data, source_name):
    print(f"Veritabanına {source_name} etkinlikleri kaydediliyor...")
    new_events_count = 0
    updated_events_count = 0
    duplicate_events_count = 0

    with app.app_context():
        for event_data in events_data:
            existing_event = Event.query.filter_by(url=event_data['url']).first()

            if existing_event:
                if (existing_event.title != event_data['title'] or
                    existing_event.description != event_data['description'] or
                    existing_event.date != event_data['date'] or
                    existing_event.location != event_data['location'] or
                    existing_event.is_active != event_data['is_active']):
                    
                    existing_event.title = event_data['title']
                    existing_event.description = event_data['description']
                    existing_event.date = event_data['date']
                    existing_event.location = event_data['location']
                    existing_event.is_active = event_data['is_active']
                    existing_event.scraped_at = datetime.now()
                    updated_events_count += 1
                else:
                    duplicate_events_count += 1
                
            else:
                new_event = Event(
                    title=event_data['title'],
                    description=event_data['description'],
                    date=event_data['date'],
                    location=event_data['location'],
                    url=event_data['url'],
                    source=source_name,
                    is_active=event_data.get('is_active', True),
                    scraped_at=datetime.now()
                )
                db.session.add(new_event)
                new_events_count += 1
        
        try:
            db.session.commit()
            print(f"{source_name} için: {new_events_count} yeni, {updated_events_count} güncellendi, {duplicate_events_count} tekrar eden etkinlik kaydedildi.")
        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Veritabanına kaydederken bütünlük hatası oluştu: {e}")
            print(f"Hata: {source_name} etkinlikleri kaydedilirken bir sorun oluştu (Bütünlük Hatası).")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Veritabanına kaydederken genel hata oluştu: {e}")
            print(f"Hata: {source_name} etkinlikleri kaydedilirken bir sorun oluştu.")


@app.cli.command('create-db')
def create_db_command():
    """Veritabanı tablolarını oluşturur."""
    with app.app_context():
        db.create_all()
    click.echo('Veritabanı tabloları oluşturuldu/güncellendi.')

if __name__ == '__main__':
    app.run(debug=True)