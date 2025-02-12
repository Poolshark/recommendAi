from flask import session, jsonify
from modules.Response import Response
from modules.Sentiment import Sentiment

class Conversation(Sentiment, Response):
    def __init__(self):
        Sentiment.__init__(self)  # Initialize Sentiment
        Response.__init__(self)   # Initialize Response

        # Define the conversation flow as a list of steps
        self.conversation_flow = [
            {
                "state": "greet",
                "question": "Hello! I'm Recommendy your restaurant recommendation assistant. How can I help you today? (For example: 'I'm looking for a restaurant for dinner' or 'I need a quick lunch spot')"
            },
            {
                "state": "ask_occasion",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["ask_occasion"]
            },
            {
                "state": "ask_atmosphere",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["ask_atmosphere"]
            },
            {
                "state": "ask_booking_history",
                "question": "Have you dined with any of our recommended restaurants before?"
            },
            {
                "state": "ask_dietary",
                "question": "Do you have any dietary restrictions or preferences I should know about?"
            },
            {
                "state": "ask_cuisine",
                "question": "What type of cuisine interests you today?"
            },
            {
                "state": "ask_time_day",
                "question": "When would you like to dine? Please provide day and time."
            },
            {
                "state": "ask_guests",
                "question": "How many people will be joining you?"
            },
            {
                "state": "ask_location",
                "question": "Which area would you prefer to dine in?"
            },
            {
                "state": "ask_budget",
                "question": "What's your comfortable budget range for this meal?"
            },
            {
                "state": "suggest_special",
                "question": lambda sentiment: self.sentiment_responses[sentiment]["suggest_special"]
            },
            {
                "state": "ask_ratings",
                "question": "Would you like to see ratings and reviews for the restaurants I have in mind?"
            },
            {
                "state": "confirm_booking",
                "question": "Just to confirm, you want to book a table for {guests} at a {cuisine} restaurant in {location} for {time}. Is that correct?"
            }
        ]

    # Helper function: get current conversation index
    def get_current_step(self):
        return session.get('current_step', 0)

    # Helper function: advance conversation state
    def advance_step(self):
        current = self.get_current_step()
        if current < len(self.conversation_flow) - 1:
            session['current_step'] = current + 1
        else:
            # Stay at the last step if completed
            session['current_step'] = current
    
    def get_next_step(self, next_step: int, urgent_steps: dict = None, found_info_steps: dict = None):
        
        steps = urgent_steps if urgent_steps else found_info_steps or {}

        while next_step < len(self.conversation_flow):
            if self.conversation_flow[next_step]["state"] in steps:
              next_step += 1
            else:
              break

        return next_step
    
    # Start or reset the conversation
    # This method is called via the /start_conversation endpoint
    def start_conversation(self):
        """Initialize or reset the conversation"""

        # Initialize or reset the conversation
        session['responses'] = {}
        session['current_step'] = 0
        session['essential_info'] = {}
        session['sentiment'] = 'neutral'
        
        # Return initial greeting
        return jsonify({
            "state": self.conversation_flow[0]["state"],
            "question": self.conversation_flow[0]["question"]
        })
    
    # Process user input and return the next question
    # This method is called via the /process_input endpoint
    def process_input(self, user_text: str):
        # Retrieve current conversation step index
        current_step = self.get_current_step()
        current_state = self.conversation_flow[current_step]["state"]

        # Extract any essential info from current response
        responses = session.get('responses', {})
        responses[current_state] = user_text
        session['responses'] = responses
 
        # Only analyze sentiment after the greeting
        if current_state != "greet":
            sentiment = session.get('sentiment', 'neutral')
            is_urgent = session.get('is_urgent', False)
        else:
            # First user input - analyze sentiment and urgency
            is_urgent = self.analyze_urgency(user_text)
            sentiment = "urgent" if is_urgent else self.analyze_sentiment(user_text)
            
            # Store in session
            session['sentiment'] = sentiment
            session['is_urgent'] = is_urgent

            # If urgent, modify the conversation flow to skip non-essential questions
            if is_urgent:
                essential_states = {
                    'ask_time_day',
                    'ask_guests',
                    'ask_location',
                    'ask_cusine',
                    'ask_dietary',
                    'confirm_booking'
                }
                
                # Find next essential question
                next_step = current_step + 1
                while (next_step < len(self.conversation_flow) - 1 and 
                       self.conversation_flow[next_step]["state"] not in essential_states):
                    next_step += 1
                
                session['current_step'] = next_step - 1  # -1 because advance_step will increment it

        # Get next question based on current state
        next_step = current_step + 1

        # Skip question if user is in urgent mode
        if session.get('is_urgent', True):
            next_step = self.get_next_step(next_step=next_step, urgent_steps=self.urgent_essential_states)

        # Skip question if it's an already answered essential question
        found_info = self.check_responses(responses)
        if found_info:
            next_step = self.get_next_step(next_step=next_step, found_info_steps=found_info)
          # while next_step < len(self.conversation_flow):
          #   if self.conversation_flow[next_step]["state"] in found_info:
          #     next_step += 1
          #   else:
          #     break

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
            self.advance_step()

            return jsonify({
                "response": self.get_sentiment_response(sentiment, user_text) if current_state != "greet" else "Thank you for sharing! Let me help you find the perfect restaurant.",
                "next_question": next_question,
                "next_state": self.conversation_flow[next_step]["state"],
                "sentiment": sentiment,
                "current_conversation": responses,
                "essential_info": session.get('essential_info', {}),
                "current_step": current_step
            }), 200