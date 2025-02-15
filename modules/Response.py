import re
from flask import session
class Response:
    def __init__(self):
        
        # Define the info patterns for the conversation
        self.user_info_patterns = {
            'ask_occasion': r'(party|date|dinner|lunch|breakfast|brunch|tea|coffee|drinks|snacks|food|romantic|special occasion|casual|formal)',
            'ask_atmosphere': r'(quiet|loud|cozy|comfortable|warm|cool|dark|bright|dim|outside|inside|outdoor|indoor)',
            'ask_booking_history': r'(no|yes|first time|regular)',
            'ask_dietary': r'(vegetarian|vegan|kosher|halal)',
            'ask_cuisine': r'(italian|chinese|indian|mexican|japanese|thai|french|traditional|fusion|street food|healthy|fast food)',
            'ask_time_day': r'(today|tomorrow|(?:at\s+)?\d{1,2}(?::\d{2})?(?:\s*[ap]m)|morning|evening|noon|tonight|now)',
            'ask_guests': r'(?:table\s+for\s+|party\s+of\s+|^|\s+)(\d+)(?:\s+people|\s+persons?|$)|(?:alone|solo|couple)',
            'ask_location': r'(here|near|near me|nearby|near my location|in the area|in the neighborhood|in the city|in the town|in the village|in the county|in the state|in the region|in the district)',
            'ask_budget': r'(cheap|moderate|expensive)',
        }

    def check_responses(self, responses: dict, user_id: str):
        """Check all responses for user info and store in session"""
        
        user_info = session.get(f'user_info_{user_id}', {})

        for key, pattern in self.user_info_patterns.items():
            
            # Only check for user info if informmation is not yet available
            if key not in user_info.keys():
                matches = []
                for response in responses.values():
                    if response:
                        print(response, key, user_info)
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

        session[f'user_info_{user_id}'] = user_info
