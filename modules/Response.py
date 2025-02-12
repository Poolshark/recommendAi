import re
from flask import session, jsonify
class Response:
    def __init__(self):
        
        # Define the info patterns for the conversation
        self.user_info_patterns = {
            'ask_occasion': r'(party|date|dinner|lunch|breakfast|brunch|tea|coffee|drinks|snacks|food|romantic|special occasion|casual|formal)',
            'ask_atmosphere': r'(quiet|loud|cozy|comfortable|warm|cool|dark|bright|dim|outside|inside|outdoor|indoor)',
            'ask_booking_history': r'(no|yes|first time|regular)',
            'ask_dietary': r'(vegetarian|vegan|kosher|halal)',
            'ask_cuisine': r'(italian|chinese|indian|mexican|japanese|thai|french|traditional|fusion|street food|healthy|fast food)',
            'ask_time_day': r'(today|tomorrow|\d{1,2}(?::\d{2})?(?:am|pm)|morning|evening|noon|now)',
            'ask_guests': r'(\d+\s*people|table for \d+|party of \d+|alone|solo|couple|\d+)',
            'ask_location': r'(here|near|near me|nearby|near my location|in the area|in the neighborhood|in the city|in the town|in the village|in the county|in the state|in the region|in the district)',
            'ask_budget': r'(cheap|moderate|expensive)',
        }

    def check_responses(self, responses: dict):
        """Check all responses for user info and store in session"""
        
        user_info = session.get('user_info', {})

        for key, pattern in self.user_info_patterns.items():
            
            # Only check for user info if informmation is not yet available
            if key not in user_info.keys():
                matches = []
                for response in responses.values():
                    if response:
                        # Find all matches in the response
                        all_matches = re.finditer(pattern, response.lower(), re.IGNORECASE)
                        for match in all_matches:
                            # Add each match to the matches array
                            if match.groups():
                                matches.extend(match.groups())
                            else:
                                matches.append(match.group())
            
                # Only store if we found matches
                if matches:
                    user_info[key] = matches

        session['user_info'] = user_info
