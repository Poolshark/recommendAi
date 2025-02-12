import re

class Response:
    def __init__(self):
        
        # Check if essential info is already provided in the response
        self.essential_info = {
            'ask_booking_history': r'(never been|been before|first time|regular|visited)',
            'ask_dietary': r'(vegetarian|vegan|gluten|allerg|dairy|kosher|halal)',
            'ask_cuisine': r'(italian|chinese|indian|mexican|japanese|thai|french)',
            'ask_time_day': r'(today|tomorrow|\d{1,2}(?::\d{2})?(?:am|pm)|morning|evening|noon)',
            'ask_guests': r'(\d+\s*people|table for \d+|party of \d+|alone|solo|couple)'
        }

    def check_responses(self, responses: dict):
        # Check all responses for essential info
        all_responses = ' '.join(str(value) for value in responses.values() if value is not None).lower()
        found_info = {}

        for key, pattern in self.essential_info.items():
            if re.search(pattern, all_responses, re.IGNORECASE):
                found_info[key] = True

        return found_info
