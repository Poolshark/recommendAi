# A very simple Flask Hello World app for you to get started with...
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from textblob import TextBlob
from git import Repo
from modules.Conversation import Conversation
from dotenv import load_dotenv
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from models.recommendation import Recommendation, db

# --------------------------------
# Initialize Flask app
# --------------------------------
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Database configuration for session storage
app.config.update(
    SESSION_TYPE='sqlalchemy',
    SQLALCHEMY_DATABASE_URI='sqlite:///sessions.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    SECRET_KEY=os.getenv('SESSION_SECRET', "dev-123"),
    # SESSION_COOKIE_SECURE=False,
    # SESSION_COOKIE_HTTPONLY=True,
    # SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize SQLAlchemy with app
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

conversation = Conversation()

@app.route('/', methods=['GET', 'POST'])
def start_conversation():
    data = get_json_payload()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id in request"}), 400
    
    return conversation.start_conversation(data['user_id'])


@app.route('/git_update', methods=['POST'])
def git_update():
    try:
        repo = Repo('./mysite')
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

# Endpoint to process conversation input
@app.route('/conversation', methods=['POST'])
def process_input():
    # Attempt to retrieve the JSON payload
    data = get_json_payload()
    if not data:
        return jsonify({"error": "Missing or invalid JSON payload."}), 400

    # Ensure the payload contains required keys
    if 'text' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing 'text' or 'user_id' in JSON payload."}), 400

    user_text = data['text']
    user_id = data['user_id']

    return conversation.process_input(user_text, user_id)

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

# Add endpoint to get user's recommendations
@app.route('/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    # This query finds all recommendations for a specific user
    recommendations = Recommendation.query.filter_by(user_id=user_id).order_by(Recommendation.created_at.desc()).all()
    return jsonify([r.to_dict() for r in recommendations])

# @app.after_request
# def add_header(response):
#     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '-1'
#     return response

if __name__ == '__main__':
    # When running locally, enable debug mode for development
    app.run(debug=True)


