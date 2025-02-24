import os
import requests
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------
# Rating API
# ------------------------------------------
# This module is used to fetch ratings from Google Places.
# It is used to get the ratings for a specific location and cuisine.
# ------------------------------------------
class RatingApi:
    def __init__(self):
        
        self.config = {
            "google": {
                "api_key": os.getenv('GOOGLE_API_KEY'),
                "base_url": "https://maps.googleapis.com/maps/api/place/textsearch/json",
                "details_url": "https://maps.googleapis.com/maps/api/place/details/json",
                "photo_url": "https://maps.googleapis.com/maps/api/place/photo"
            },
        }

    # Function to fetch restaurant ratings from Google Places
    def fetch_google_ratings(self, location: str, cuisine: str):
        """Fetch ratings from Google Places"""
        url = f'{self.config["google"]["base_url"]}?query={cuisine}+restaurants+in+{location}&key={self.config["google"]["api_key"]}'
        
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            # Add photo URL for each result that has photos
            for result in results:
                # Add photo URL if available
                if result.get('photos'):
                    photo_reference = result['photos'][0]['photo_reference']  # Get first photo reference
                    result['photo_url'] = self.get_photo_url(photo_reference)
                
                # Get URLs if place_id is available
                if result.get('place_id'):
                    urls = self.get_place_details(result['place_id'])
                    result.update(urls)
            
            return results
        else:
            return []
    
    def get_photo_url(self, photo_reference: str, maxwidth: int = 400):
        """Generate photo URL using the photo reference"""

        return f"{self.config['google']['photo_url']}?maxwidth={maxwidth}&photo_reference={photo_reference}&key={self.config['google']['api_key']}"
    
    def get_place_details(self, place_id: str):
        """Fetch detailed place information including URLs"""
        url = f"{self.config['google']['details_url']}?place_id={place_id}&fields=website,url&key={self.config['google']['api_key']}"
        
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json().get('result', {})
            return {
                'website_url': result.get('website', ''),  # Restaurant's own website
                'maps_url': result.get('url', '')          # Google Maps URL
            }
        return {'website_url': '', 'maps_url': ''}

    # Endpoint to process conversation input and return the next question
    def process_reccomendations(self, location: str, cuisine: str):
        # Fetch ratings from Google
        google_ratings = self.fetch_google_ratings(location, cuisine)

        # Prepare a response with ratings
        ratings_response = {
            "google": google_ratings
        }
        return jsonify({
            "response": "Here are the ratings I found:",
            "ratings": ratings_response
        }), 200
