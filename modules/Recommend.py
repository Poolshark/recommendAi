from models.recommendation import Recommendation, db
from modules.RatingApi import RatingApi
from datetime import datetime
import re

class Recommend:
    def __init__(self):
        self.rating_api = RatingApi()

    def parse_time(self, time_str):
        """Convert time string to datetime object"""
        if not time_str:
            return None
        
        # Handle different time formats
        time_patterns = {
            'now': datetime.now(),
            'tonight': datetime.now().replace(hour=19, minute=0),
            'today': datetime.now(),
            'tomorrow': datetime.now().replace(day=datetime.now().day + 1),
            'morning': datetime.now().replace(hour=10, minute=0),
            'noon': datetime.now().replace(hour=12, minute=0),
            'evening': datetime.now().replace(hour=18, minute=0)
        }

        # Check for exact patterns first
        for pattern, time in time_patterns.items():
            if pattern in time_str.lower():
                return time

        # Try to parse specific time (e.g., "8pm", "14:30")
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*([ap]m)?', time_str.lower())
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            if time_match.group(3) == 'pm' and hour < 12:
                hour += 12
            return datetime.now().replace(hour=hour, minute=minute)

        return None

    def parse_guests(self, guests_str):
        """Convert guests string to number"""
        if not guests_str:
            return 1
        
        if 'alone' in guests_str or 'solo' in guests_str:
            return 1
        if 'couple' in guests_str:
            return 2
        
        # Extract number from string
        match = re.search(r'(\d+)', guests_str)
        if match:
            return int(match.group(1))
        return 1

    def get_recommendation(self, user_info: dict, user_id: str):
        """Generate restaurant recommendation based on user preferences"""
        
        # Extract relevant information
        cuisine = user_info.get('ask_cuisine', [None])[0]
        location = user_info.get('ask_location', [None])[0]
        guests = self.parse_guests(user_info.get('ask_guests', [None])[0])
        time = self.parse_time(user_info.get('ask_time_day', [None])[0])
        dietary = user_info.get('ask_dietary', [None])[0]
        budget = user_info.get('ask_budget', [None])[0]
        atmosphere = user_info.get('ask_atmosphere', [None])[0]
        
        # Build search query with all relevant info
        search_query = []
        if cuisine:
            search_query.append(cuisine)
        if dietary:
            search_query.append(dietary)
        if atmosphere:
            search_query.append(atmosphere)
        if budget:
            search_query.append(budget)
        if location:
            search_query.append(f"in {location}")
        
        # Combine into search string
        search_string = " ".join(search_query)
        
        # Get restaurant recommendations from Google Places with enhanced query
        restaurants = self.rating_api.fetch_google_ratings(location, search_string)
        
        # Enhanced scoring system
        scored_restaurants = []
        for restaurant in restaurants:
            score = 0
            
            # Basic match criteria
            if cuisine and cuisine.lower() in restaurant.get('types', []):
                score += 2
            
            # Dietary requirements (critical)
            if dietary:
                if any(dietary.lower() in tag.lower() for tag in restaurant.get('types', [])):
                    score += 3
                elif any(dietary.lower() in restaurant.get('name', '').lower()):
                    score += 2
            
            # Atmosphere matching
            if atmosphere:
                if any(atmosphere.lower() in review.get('text', '').lower() 
                      for review in restaurant.get('reviews', [])):
                    score += 1
            
            # Budget matching
            price_level = restaurant.get('price_level', 2)
            if budget:
                budget_map = {'cheap': 1, 'moderate': 2, 'expensive': 3}
                if price_level == budget_map.get(budget.lower(), 2):
                    score += 2
            
            # Rating boost
            rating = restaurant.get('rating', 0)
            score += rating / 2  # Add up to 2.5 points for 5-star rating
            
            # Number of ratings boost
            user_ratings_total = restaurant.get('user_ratings_total', 0)
            score += min(user_ratings_total / 1000, 1)  # Up to 1 point for 1000+ reviews
            
            # Opening hours check
            if time and restaurant.get('opening_hours', {}).get('open_now'):
                score += 1
            
            scored_restaurants.append((restaurant, score))
        
        # Sort by score and get best match
        scored_restaurants.sort(key=lambda x: x[1], reverse=True)
        if not scored_restaurants:
            return None
        
        best_match = scored_restaurants[0][0]
        
        # Enhanced recommendation data
        recommendation_data = {
            'name': best_match.get('name'),
            'cuisine': cuisine,
            'location': location,
            'guests': guests,
            'dietary': dietary,
            'booking_time': time,
            'atmosphere': atmosphere,
            'budget': budget,
            'rating': best_match.get('rating'),
            'total_ratings': best_match.get('user_ratings_total'),
            'price_level': best_match.get('price_level'),
            'address': best_match.get('formatted_address'),
            'place_id': best_match.get('place_id')
        }
        
        # Store recommendation with user_id
        recommendation = Recommendation(
            user_id=user_id,
            restaurant_name=recommendation_data['name'],
            cuisine=recommendation_data['cuisine'],
            location=recommendation_data['location'],
            guests=recommendation_data['guests'],
            dietary=recommendation_data['dietary'],
            booking_time=recommendation_data['booking_time']
        )
        db.session.add(recommendation)
        db.session.commit()
        
        return recommendation.to_dict()
