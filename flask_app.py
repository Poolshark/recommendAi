# A very simple Flask Hello World app for you to get started with...
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from textblob import TextBlob
from git import Repo
from modules.Conversation import Conversation
from dotenv import load_dotenv

# --------------------------------
# Initialize Flask app
# --------------------------------
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# For simplicity, we're using Flask's built-in session.
# For production, consider server-side session storage.
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev-key-123')  # Add fallback key
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')  # Specify session directory
Session(app)
# --------------------------------

conversation = Conversation()

@app.route('/', methods=['GET', 'POST'])
def start_conversation():
    return conversation.start_conversation()


@app.route('/git_update', methods=['POST'])
def git_update():
    try:
        repo = Repo('./mysite')  # Use current directory instead of hardcoded path
        origin = repo.remotes.origin
        origin.pull()
        return jsonify({"message": "Repository updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

def get_json_payload():
    """
    Helper function to retrieve JSON data from the request.
    Returns None if the request data is not in JSON format.
    """
    if request.is_json:
        return request.get_json()
    else:
        return None
    
# @app.route('/start_conversation', methods=['POST'])
# def start_conversation():
#     return input_module.start_conversation()

# Endpoint to process conversation input
@app.route('/conversation', methods=['POST'])
def process_input():
    # Attempt to retrieve the JSON payload
    data = get_json_payload()
    if not data:
        return jsonify({"error": "Missing or invalid JSON payload."}), 400

    # Ensure the payload contains the 'text' key
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' parameter in JSON payload."}), 400

    user_text = data['text']

    return conversation.process_input(user_text)

    # ----- LEGACY
    # # Here, implement your conversation management logic.
    # # For this example, we simply echo the user's input.
    # response_text = f"You said: {user_text}. What would you like to do next?"

    # # Return the response as JSON
    # return jsonify({"response": response_text})


# Endpoint to perform sentiment analysis - TESTING
@app.route('/sentiment_analysis', methods=['POST'])
def sentiment_analysis():
    # Retrieve the JSON payload
    data = get_json_payload()
    if not data:
        return jsonify({"error": "Missing or invalid JSON payload."}), 400

    if 'text' not in data:
        return jsonify({"error": "Missing 'text' parameter in JSON payload."}), 400

    user_text = data['text']

    # Analyze the sentiment using TextBlob
    blob = TextBlob(user_text)
    sentiment = blob.sentiment  # Returns a namedtuple with polarity and subjectivity

    # Format the result
    sentiment_result = {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "interpretation": (
            "positive" if sentiment.polarity > 0
            else "negative" if sentiment.polarity < 0
            else "neutral"
        )
    }

    return jsonify(sentiment_result)


if __name__ == '__main__':
    # When running locally, enable debug mode for development
    app.run(debug=True)


