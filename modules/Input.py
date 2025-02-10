from flask import Flask, session, jsonify, Request
from flask_session import Session
from textblob import TextBlob

class InputModule:
    def __init__(self, app: Flask):
        # For simplicity, we're using Flask's built-in session. For production, consider server-side session storage.
        app.secret_key = 'your_secret_key'  # Required to use sessions

        # Optionally, configure Flask-Session to store session data on the filesystem:
        app.config['SESSION_TYPE'] = 'filesystem'
        Session(app)

        # Define the conversation flow as a list of steps
        self.conversation_flow = [
            {"state": "ask_booking_history", "question": "Have you booked a restaurant before? (yes/no)"},
            {"state": "ask_dietary", "question": "Do you have any dietary restrictions or preferences? (e.g., vegan, vegetarian)"},
            {"state": "ask_cuisine", "question": "What type of cuisine would you like?"},
            {"state": "ask_time_day", "question": "When would you like to book your table? Please provide day and time."},
            {"state": "ask_guests", "question": "How many guests will be dining?"}
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
            session['current_step'] = current  # Stay at the last step if completed

    # Endpoint to initialize or reset the conversation
    def start_conversation(self):
        session['current_step'] = 0
        session['responses'] = {}  # Optional: store user responses
        question = self.conversation_flow[0]["question"]
        return jsonify({"question": question, "state": self.conversation_flow[0]["state"]})


    # Endpoint to process conversation input and return the next question
    def process_input(self, user_text: str):

        # Retrieve current conversation step index
        current_step = self.get_current_step()
        current_state = self.conversation_flow[current_step]["state"]

        # Save the user response in session (optional)
        responses = session.get('responses', {})
        responses[current_state] = user_text
        session['responses'] = responses

        # (Optional) Process sentiment analysis for user text
        # For example, if you wanted to adjust behavior based on sentiment:
        blob = TextBlob(user_text)
        sentiment = blob.sentiment.polarity  # Could be used to modify next question if needed

        # Advance the conversation if there are more steps
        if current_step < len(self.conversation_flow) - 1:
            self.advance_step()
            next_step = self.get_current_step()
            next_question = self.conversation_flow[next_step]["question"]
            next_state = self.conversation_flow[next_step]["state"]
            return jsonify({
                "response": f"Got it. You said: '{user_text}'",
                "next_question": next_question,
                "next_state": next_state,
                "current_conversation": session['responses']
            }), 200
        else:
            # End of conversation flow reached
            return jsonify({
                "response": f"Got it. You said: '{user_text}'",
                "final_response": "Thank you for providing all the details. We will now process your restaurant booking.",
                "collected_data": session.get('responses')
            }), 200
