import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, flash # render_template ve flash'ı import et
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_dev_secret_key_change_this!')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Event(db.Model):
    __tablename__ = 'events' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    url = db.Column(db.String(500), unique=True, nullable=False)
    source = db.Column(db.String(100), nullable=False) 
    is_active = db.Column(db.Boolean, default=True, nullable=False) 
    scraped_at = db.Column(db.DateTime, default=datetime.now, nullable=False) 

    def __repr__(self):
        return f"<Event {self.title}>"

@app.route('/events', methods=['GET'])
def get_events():
    try:
        events = Event.query.all()
        
        events_for_template = []
        for event in events:
            event_date_str = event.date.strftime('%Y-%m-%d') if event.date else 'Tarih Belirtilmedi'
            # Eğer Event modelinde image_url alanı varsa ve scraper çekiyorsa:
            # event_image_url = event.image_url if event.image_url else url_for('static', filename='images/default-event.jpg')
            # Yoksa aşağıdaki gibi kullan:
            event_image_url = url_for('static', filename='images/placeholder-image-colored.jpeg') 
            event_status_text = "Açık" if event.is_active else "Kapalı"
            event_status_class = "acik" if event.is_active else "kapali"


            events_for_template.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event_date_str,
                'location': event.location,
                'url': event.url,
                'link': event.url, 
                'source': event.source,
                'is_active': event.is_active,
                'scraped_at': event.scraped_at.isoformat(),
                'image_url': event_image_url, 
                'status': event_status_text, 
                'status_class': event_status_class 
            })

        last_updated_event = Event.query.order_by(Event.scraped_at.desc()).first()
        last_updated = last_updated_event.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if last_updated_event else "N/A"
        total_active_events = Event.query.filter_by(is_active=True).count()


        return render_template(
            'index.html', 
            grouped_events={"Tüm Etkinlikler": events_for_template}, 
            last_updated=last_updated,
            total_event_count=total_active_events
        )

    except Exception as e:
        app.logger.error(f"Etkinlikler çekilirken hata oluştu: {e}")
        flash('Etkinlikler yüklenirken bir sorun oluştu.', 'error')
        return render_template('index.html', grouped_events={}, last_updated="N/A", total_event_count=0)


def save_events_to_db(events_data, source_name):
    print(f"Veritabanına {source_name} etkinlikleri kaydediliyor...")
    new_events_count = 0
    updated_events_count = 0
    duplicate_events_count = 0

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

@app.route('/')
def index_redirect():
    return redirect(url_for('get_events'))

@app.route('/update_data')
def update_data():
    # Gerçek uygulamada, bu işlem uzun sürebileceği için bir kuyruk sistemi (örn. Celery) kullanmak daha iyidir.
    # Veya direkt olarak scraper fonksiyonunu çağırabilirsin.
    try:
        # Örnek: scraper'ı buradan çağır
        # from your_scraper_module import scrape_and_save_all_sources
        # scrape_and_save_all_sources() # Bu fonksiyonu senin scraper dosyanından çağır

        flash('Veriler güncelleniyor, lütfen bekleyin. Sayfa kısa süre içinde yenilenecektir.', 'success')
    except Exception as e:
        flash(f'Veriler güncellenirken bir hata oluştu: {e}', 'error')

    return redirect(url_for('get_events'))

def initialize_database():
    with app.app_context():
        db.create_all()
        print("Veritabanı tabloları oluşturuldu/kontrol edildi.")

@app.cli.command('create-db')
def create_db_command():
    """Veritabanı tablolarını oluşturur."""
    initialize_database()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
