import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, flash # render_template ve flash'ı import et
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Event(db.Model):
    __tablename__ = 'events' # Tablo adını belirtmek iyi bir pratiktir
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    url = db.Column(db.String(500), unique=True, nullable=False) # URL benzersiz olmalı
    source = db.Column(db.String(100), nullable=False) # Hangi kaynaktan geldiği
    is_active = db.Column(db.Boolean, default=True, nullable=False) # Etkinliğin aktif olup olmadığı
    scraped_at = db.Column(db.DateTime, default=datetime.now, nullable=False) # Kaydedilme/Güncellenme zamanı

    def __repr__(self):
        return f"<Event {self.title}>"

@app.route('/events', methods=['GET'])
def get_events():
    try:
        events = Event.query.all()
        
        events_for_template = []
        for event in events:
            # HTML şablonunda kullanılacak veriyi hazırla
            event_date_str = event.date.strftime('%Y-%m-%d') if event.date else 'Tarih Belirtilmedi'
            
            # image_url ve status için varsayılan değerler veya veritabanından çekim
            # Eğer Event modelinde image_url yoksa, burada varsayılan bir resim verilir.
            # Yoksa, scraper'ın bu URL'yi çekmesini sağlamalısın.
            # Şu an için geçici olarak sabit bir resim URL'si kullanalım:
            
            # Eğer Event modelinde image_url alanı varsa ve scraper çekiyorsa:
            # event_image_url = event.image_url if event.image_url else url_for('static', filename='images/default-event.jpg')
            # Yoksa aşağıdaki gibi kullan:
            event_image_url = url_for('static', filename='images/placeholder-image.jpeg') # Statik klasördeki varsayılan resim
            
            event_status_text = "Açık" if event.is_active else "Kapalı"
            event_status_class = "acik" if event.is_active else "kapali"


            events_for_template.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event_date_str, # HTML'de kullanılacak formatlanmış tarih
                'location': event.location,
                'url': event.url,
                'link': event.url, # HTML'deki 'link' alanı veritabanındaki 'url' ile eşleşiyor
                'source': event.source,
                'is_active': event.is_active,
                'scraped_at': event.scraped_at.isoformat(),
                'image_url': event_image_url, # Resim URL'si
                'status': event_status_text, # Durum metni
                'status_class': event_status_class # CSS sınıfı için
            })

        # HTML'deki üst bilgileri doldurmak için veri çekimi
        last_updated_event = Event.query.order_by(Event.scraped_at.desc()).first()
        last_updated = last_updated_event.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if last_updated_event else "N/A"
        total_active_events = Event.query.filter_by(is_active=True).count()

        # HTML şablonunu render et ve verileri gönder
        return render_template(
            'index.html', # Bu, senin gönderdiğin HTML dosyasının adını yansıtmalı.
            grouped_events={"Tüm Etkinlikler": events_for_template}, # HTML'de grouped_events bekleniyor.
                                                                  # İstersen kategorilere göre gruplayabiliriz.
            last_updated=last_updated,
            total_event_count=total_active_events
        )

    except Exception as e:
        app.logger.error(f"Etkinlikler çekilirken hata oluştu: {e}")
        flash('Etkinlikler yüklenirken bir sorun oluştu.', 'error')
        return render_template('index.html', grouped_events={}, last_updated="N/A", total_event_count=0)

# Veritabanına etkinlik kaydetme fonksiyonu
def save_events_to_db(events_data, source_name):
    print(f"Veritabanına {source_name} etkinlikleri kaydediliyor...")
    new_events_count = 0
    updated_events_count = 0
    duplicate_events_count = 0

    # Bu fonksiyon zaten app.app_context() içinde çağrıldığı için burada tekrar context açmaya gerek yok.
    # Ancak başka bir yerden direkt çağrılırsa diye güvenlik için tutulabilir.
    # Mevcut durumda run_daily_scrape.py zaten bir context açıyor.
    # with app.app_context(): # Bu satırı kaldırabiliriz, dışarıda zaten var
    for event_data in events_data:
        # URL üzerinden mevcut etkinliği kontrol et
        existing_event = Event.query.filter_by(url=event_data['url']).first()

        if existing_event:
            # Eğer etkinlik URL'si üzerinden zaten varsa, güncelle
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
                existing_event.scraped_at = datetime.now() # Güncelleme zamanı
                updated_events_count += 1
            else:
                duplicate_events_count += 1
            
        else:
            # Yeni etkinlik oluştur
            new_event = Event(
                title=event_data['title'],
                description=event_data['description'],
                date=event_data['date'],
                location=event_data['location'],
                url=event_data['url'],
                source=source_name, # Scraper fonksiyonundan gelen kaynak adı
                is_active=event_data.get('is_active', True), # Varsayılan olarak aktif
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
def index_redirect(): # İsim çakışmaması için değiştirdim
    return redirect(url_for('get_events'))

@app.route('/update_data')
def update_data():
    # Burada scraping ve veri kaydetme işlemlerini tetikleyeceksin.
    # Örneğin, 'run_daily_scrape.py' dosyasındaki mantığı buraya taşıyabilir veya bir background görevi başlatabilirsin.
    # Bu kısmı senin scraper mantığına göre doldurman gerekecek.
    # Şimdilik sadece bir flash mesajı gösterip ana sayfaya yönlendirelim.
    
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

# Yeni fonksiyon: Veritabanı tablolarını başlatmak için
def initialize_database():
    with app.app_context(): # Flask uygulama bağlamı içinde çalıştır
        db.create_all()
        print("Veritabanı tabloları oluşturuldu/kontrol edildi.")

# Flask CLI komutu: Veritabanı tablolarını oluşturur (manuel çalıştırma için)
@app.cli.command('create-db')
def create_db_command():
    """Veritabanı tablolarını oluşturur."""
    initialize_database() # initialize_database fonksiyonunu çağır

if __name__ == '__main__':
    # Eğer app.py doğrudan çalıştırılırsa (geliştirme modunda)
    # initialize_database() # Uygulama başladığında tabloları oluştur
    app.run(debug=True, host='0.0.0.0', port=5000) # Docker içinde 0.0.0.0 dinlemeli
