from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    is_paid = db.Column(db.Boolean, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Event {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "title": self.title,
            "url": self.url,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "category": self.category,
            "is_paid": self.is_paid,
            "image_url": self.image_url,
            "location": self.location,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }