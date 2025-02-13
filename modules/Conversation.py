from flask import session, jsonify
from modules.Response import Response
from modules.Sentiment import Sentiment
from models.recommendation import Recommendation, db

class Conversation(Sentiment, Response):
    def __init__(self):
        Sentiment.__init__(self)  # Initialize Sentiment
        Response.__init__(self)   # Initialize Response

        # Define the conversation flow as a list of steps
        self.conversation_flow = [
            {
                "id": 0,
                "state": "greet",
                "is_essential": False,
                "question": "Hello! I'm Recommendy your restaurant recommendation assistant. How can I help you today? (For example: 'I'm looking for a restaurant for dinner' or 'I need a quick lunch spot')"
            },
            {
                "id": 1,
                "is_essential": False,
                "state": "ask_occasion",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["ask_occasion"]
            },
            {
                "id": 2,
                "is_essential": False,
                "state": "ask_atmosphere",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["ask_atmosphere"]
            },
            {
                "id": 3,
                "is_essential": True,
                "state": "ask_booking_history",
                "question": "Have you dined with any of our recommended restaurants before?"
            },
            {
                "id": 4,
                "is_essential": True,
                "state": "ask_dietary",
                "question": "Do you have any dietary restrictions or preferences I should know about?"
            },
            {
                "id": 5,
                "is_essential": True,
                "state": "ask_cuisine",
                "question": "What type of cuisine interests you today?"
            },
            {
                "id": 6,
                "is_essential": True,
                "state": "ask_time_day",
                "question": "When would you like to dine? Please provide day and time."
            },
            {
                "id": 7,
                "is_essential": True,
                "state": "ask_guests",
                "question": "How many people will be joining you?"
            },
            {
                "id": 8,
                "is_essential": True,
                "state": "ask_location",
                "question": "Which area would you prefer to dine in?"
            },
            {
                "id": 9,
                "is_essential": False,
                "state": "ask_budget",
                "question": "What's your comfortable budget range for this meal? Options are 'cheap', 'moderate' and 'expensive'."
            },
            {
                "id": 10,
                "is_essential": False,
                "state": "suggest_special",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["suggest_special"]
            }
        ]

    # Helper function: get current conversation index
    def get_current_step(self, user_id: str):
        return session.get(f'current_step_{user_id}', 0)

    # Helper function: advance conversation state
    def advance_step(self, user_id: str):
        current = self.get_current_step(user_id)
        if current < len(self.conversation_flow) - 1:
            session['current_step_{user_id}'] = current + 1
        else:
            # Stay at the last step if completed
            session['current_step_{user_id}'] = current
    
    def get_next_step(self, next_step: int, user_id: str):
        
        is_urgent = session.get('is_urgent', False)

        while next_step < len(self.conversation_flow):
            
            # Check if the next step is already answered in a previous step
            if self.conversation_flow[next_step]["state"] in session.get('user_info_{user_id}', {}):
                next_step += 1
            else:
                if is_urgent and not self.conversation_flow[next_step]["is_essential"]:
                    next_step += 1
                else:
                    break;

        return next_step
    
    # Start or reset the conversation
    # This method is called via the /start_conversation endpoint
    def start_conversation(self, user_id: str):
        """Initialize or reset the conversation"""
        
        # Initialize or reset the conversation for this user
        session[f'responses_{user_id}'] = {}
        session[f'user_info_{user_id}'] = {}
        session[f'current_step_{user_id}'] = 0
        session[f'is_urgent_{user_id}'] = False
        session[f'sentiment_{user_id}'] = 'neutral'
        
        return jsonify({
            "state": self.conversation_flow[0]["state"],
            "question": self.conversation_flow[0]["question"]
        })
    
    # Process user input and return the next question
    # This method is called via the /process_input endpoint
    def process_input(self, user_text: str, user_id: str):
        current_step = self.get_current_step(user_id)
        current_state = self.conversation_flow[current_step]["state"]

        # Extract any essential info from current response
        responses = session.get(f'responses_{user_id}', {})
        responses[current_state] = user_text
        session[f'responses_{user_id}'] = responses
 
        # Only analyse sentiment after the greeting
        if current_state != "greet":
            sentiment = session.get(f'sentiment_{user_id}', 'neutral')
            is_urgent = session.get(f'is_urgent_{user_id}', False)
        else:
            # First user input - analyse sentiment and urgency
            is_urgent = self.analyze_urgency(user_text)
            sentiment = "urgent" if is_urgent else self.analyze_sentiment(user_text)
            
            # Store in session
            session[f'sentiment_{user_id}'] = sentiment
            session[f'is_urgent_{user_id}'] = is_urgent

        

        # Get next question based on current state
        next_step = current_step + 1

        # Skip question if user is in urgent mode
        # if session.get('is_urgent'):
        #     next_step = self.get_next_step(next_step=next_step, is_urgent=True)

        # Skip question if it's an already answered essential question or if
        # the user is in urgent mode and the question is not essential
        self.check_responses(responses)
        if session.get(f'user_info_{user_id}'):
            next_step = self.get_next_step(next_step=next_step, user_id=user_id)


        # If the current step is an essential step but no user info os stored, repeat the question
        if self.conversation_flow[current_step]["is_essential"] and current_state not in session.get(f'user_info_{user_id}').keys():
            return jsonify({
                "state": current_state,
                "question": self.conversation_flow[current_step]["question"],
                "response": "I'm sorry, I didn't catch that. Can you please repeat?"
            }), 200

        if next_step < len(self.conversation_flow):
            question = self.conversation_flow[next_step]["question"]
            
            # Apply sentiment-based question only after greeting
            if callable(question):
                next_question = question(sentiment)
            else:
                next_question = question

            # Modify question for urgent cases
            if is_urgent:
                next_question = self.make_question_urgent(next_question)

            # Add follow-up questions based on sentiment and previous responses
            # Only add follow-ups after greeting
            if current_state != "greet":
                follow_up = self.get_follow_up_question(sentiment, responses)
                if follow_up:
                    next_question = f"{next_question}\n{follow_up}"

            # Advance to the next step
            self.advance_step(user_id)

            return jsonify({
                "response": self.get_sentiment_response(sentiment, user_text) if current_state != "greet" else "Thank you for sharing! Let me help you find the perfect restaurant.",
                "next_question": next_question,
                "next_state": self.conversation_flow[next_step]["state"],
                "sentiment": sentiment,
                "current_conversation": responses,
                "user_info": session.get(f'user_info_{user_id}', {}),
                "current_step": current_step
            }), 200
        else:
            # If the conversation is complete, return the final response
            return jsonify({
                "response": "Final response",
                "sentiment": sentiment,
                "current_conversation": responses,
            }), 200

    def store_recommendation(self, user_id: str, recommendation_data: dict):
        recommendation = Recommendation(
            user_id=user_id,
            restaurant_name=recommendation_data.get('name'),
            cuisine=recommendation_data.get('cuisine'),
            location=recommendation_data.get('location'),
            guests=recommendation_data.get('guests'),
            dietary=recommendation_data.get('dietary'),
            booking_time=recommendation_data.get('booking_time')
        )
        db.session.add(recommendation)
        db.session.commit()