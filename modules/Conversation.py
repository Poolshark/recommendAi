from flask import session, jsonify
from modules.Response import Response
from modules.Sentiment import Sentiment
from modules.Recommend import Recommend
from models.recommendation import Recommendation, db

class Conversation(Sentiment, Response):
    def __init__(self):
        Sentiment.__init__(self)  # Initialize Sentiment
        Response.__init__(self)   # Initialize Response
        self.recommend = Recommend()

        # Define the conversation flow as a list of steps
        self.conversation_flow = [
            {
                "id": 0,
                "state": "greet",
                "is_essential": False,
                "question": lambda name: f"Hello {name}! I'm Recommendy your restaurant recommendation assistant. I can help you find the perfect restaurant for your needs. What are you looking for?"
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
                "question": "Have you dined with any of our recommended restaurants before?",
                "specify_question": "Please answer: yes, no, first time, or regular"
            },
            {
                "id": 4,
                "is_essential": True,
                "state": "ask_dietary",
                "question": "Do you have any dietary restrictions or preferences I should know about?",
                "specify_question": "Please specify: vegetarian, vegan, kosher, or halal"
            },
            {
                "id": 5,
                "is_essential": True,
                "state": "ask_cuisine",
                "question": "What type of cuisine would you like to try?",
                "specify_question": "Choose cuisine: italian, chinese, indian, mexican, japanese, thai, french"
            },
            {
                "id": 6,
                "is_essential": True,
                "state": "ask_time_day",
                "question": "When would you like to dine? Please provide day and time.",
                "specify_question": "Specify time: today, tomorrow, specific time (e.g., 7pm), morning, evening"
            },
            {
                "id": 7,
                "is_essential": True,
                "state": "ask_guests",
                "question": "How many people will be joining you?",
                "specify_question": "Please be more specific: alone, solo, couple"
            },
            {
                "id": 8,
                "is_essential": True,
                "state": "ask_location",
                "question": "Which area would you prefer to dine in?",
                "specify_question": "Specify location: near me, nearby, in the area, in the city"
            },
            {
                "id": 9,
                "is_essential": False,
                "state": "ask_budget",
                "question": "What's your comfortable budget range for this meal? Options are 'cheap', 'moderate' and 'expensive'."
            }
        ]

    # Helper function: get current conversation index
    def get_current_step(self, user_id: str):
        return session.get(f'current_step_{user_id}', 0)

    # Helper function: advance conversation state
    def advance_step(self, user_id: str):
        current = self.get_current_step(user_id)
        if current < len(self.conversation_flow) - 1:
            session[f'current_step_{user_id}'] = current + 1
        else:
            # Stay at the last step if completed
            session[f'current_step_{user_id}'] = current
    
    def get_next_step(self, next_step: int, user_id: str):
        
        is_urgent = session.get(f'is_urgent_{user_id}', False)

        while next_step < len(self.conversation_flow):
            
            # Check if the next step is already answered in a previous step
            if self.conversation_flow[next_step]["state"] in session.get(f'user_info_{user_id}', {}):
                next_step += 1
            else:
                if is_urgent and not self.conversation_flow[next_step]["is_essential"]:
                    next_step += 1
                else:
                    break;

        return next_step
    
    # Start or reset the conversation
    # This method is called via the /start_conversation endpoint
    def start_conversation(self, user_id: str, user_name: str="Mr. Food"):
        """Initialize or reset the conversation"""
        
        # Initialize or reset the conversation for this user
        session[f'responses_{user_id}'] = {}
        session[f'user_info_{user_id}'] = {}
        session[f'current_step_{user_id}'] = 0
        session[f'is_urgent_{user_id}'] = False
        session[f'sentiment_{user_id}'] = 'neutral'
        session[f'user_name_{user_id}'] = user_name

        return jsonify({
            "user_id": user_id,
            "user_name": user_name,
            "state": self.conversation_flow[0]["state"],
            "next_question": self.conversation_flow[0]["question"](user_name)
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

        # Skip question if it's an already answered essential question or if
        # the user is in urgent mode and the question is not essential
        self.check_responses(responses=responses, user_id=user_id)
        if session.get(f'user_info_{user_id}'):
            next_step = self.get_next_step(next_step=next_step, user_id=user_id)


        # If the current step is an essential step but no user info is stored, repeat the question
        if self.conversation_flow[current_step]["is_essential"] and current_state not in session.get(f'user_info_{user_id}').keys():
            return jsonify({
                "user_id": user_id,
                "state": current_state,
                "sentiment": sentiment,
                "current_step": current_step,
                "current_conversation": responses,
                "user_info": session.get(f'user_info_{user_id}', {}),
                "next_state": self.conversation_flow[next_step]["state"],
                "question": self.conversation_flow[current_step]["question"],
                "next_question": self.conversation_flow[current_step]["specify_question"],
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
                "user_id": user_id,
                "sentiment": sentiment,
                "current_step": current_step,
                "next_question": next_question,
                "current_conversation": responses,
                "user_info": session.get(f'user_info_{user_id}', {}),
                "next_state": self.conversation_flow[next_step]["state"],
            }), 200
        else:
            # If we have all essential info, make a recommendation
            user_info = session.get(f'user_info_{user_id}', {})
            # essential_fields = {'ask_cuisine', 'ask_location', 'ask_guests', 'ask_time_day', 'ask_dietary'}
            # if all(field in user_info for field in essential_fields):
            recommendation = self.recommend.get_recommendation(user_info, user_id)
            if recommendation:
                return jsonify({
                    "response": f"I recommend {recommendation['restaurant_name']}!",
                    "recommendation": recommendation,
                    "current_conversation": responses,
                    "user_id": user_id,
                    "user_info": user_info
                }), 200
                
            # If the conversation is complete, return the final response
            return jsonify({
                "response": "Could not find a restaurant that matches your preferences. Please try again with different preferences.",
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