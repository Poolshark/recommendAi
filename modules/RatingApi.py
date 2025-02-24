import os
import requests
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

class RatingApi:
    def __init__(self):
        
        self.config = {
            # "yelp": {
            #     "api_key": os.getenv('YELP_API_KEY'),
            #     "base_url": "https://api.yelp.com/v3/businesses",
            #     "headers": {
            #         "Authorization": f"Bearer {os.getenv('YELP_API_KEY')}"
            #     }
            # },
            "google": {
                "api_key": os.getenv('GOOGLE_API_KEY'),
                "base_url": "https://maps.googleapis.com/maps/api/place/textsearch/json",
                "photo_url": "https://maps.googleapis.com/maps/api/place/photo"
            },
            # "tripadvisor": {
            #     "api_key": os.getenv('TRIPADVISOR_API_KEY'),
            #     "base_url": "https://api.tripadvisor.com/api/partner/2.0/location"
            # }
        }

    def fetch_yelp_ratings(self, location: str, cuisine: str):
        url = f'{self.config.yelp.base_url}/search?location={location}&term={cuisine}'
        
        response = requests.get(url, headers=self.config.yelp.headers)
        if response.status_code == 200:
            return response.json().get('businesses', [])
        else:
            return []

    # Function to fetch restaurant ratings from Google Places
    def fetch_google_ratings(self, location: str, cuisine: str):
        url = f'{self.config["google"]["base_url"]}?query={cuisine}+restaurants+in+{location}&key={self.config["google"]["api_key"]}'
        
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            # Add photo URL for each result that has photos
            for result in results:
                if result.get('photos'):
                    photo_reference = result['photos'][0]['photo_reference']  # Get first photo reference
                    result['photo_url'] = self.get_photo_url(photo_reference)
            
            return results
        else:
            return []

    # Endpoint to process conversation input and return the next question
    def process_reccomendations(self, location: str, cuisine: str):
        # Fetch ratings from Yelp and Google
        # yelp_ratings = self.fetch_yelp_ratings(location, cuisine)
        google_ratings = self.fetch_google_ratings(location, cuisine)

        # Prepare a response with ratings
        ratings_response = {
            # "yelp": yelp_ratings,
            "google": google_ratings
        }
        return jsonify({
            "response": "Here are the ratings I found:",
            "ratings": ratings_response
        }), 200
