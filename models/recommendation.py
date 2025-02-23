from models.db import db  # Import the shared db instance
from datetime import datetime

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100))
    restaurant_name = db.Column(db.String(200))
    cuisine = db.Column(db.String(100))
    location = db.Column(db.String(200))
    guests = db.Column(db.Integer)
    dietary = db.Column(db.String(200))
    booking_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    atmosphere = db.Column(db.String(100))
    budget = db.Column(db.String(50))
    rating = db.Column(db.Float)
    total_ratings = db.Column(db.Integer)
    price_level = db.Column(db.Integer)
    address = db.Column(db.String(200))
    place_id = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'restaurant_name': self.restaurant_name,
            'cuisine': self.cuisine,
            'location': self.location,
            'guests': self.guests,
            'dietary': self.dietary,
            'booking_time': self.booking_time.isoformat() if self.booking_time else None,
            'created_at': self.created_at.isoformat(),
            'atmosphere': self.atmosphere,
            'budget': self.budget,
            'rating': self.rating,
            'total_ratings': self.total_ratings,
            'price_level': self.price_level,
            'address': self.address,
            'place_id': self.place_id
        } 