# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, jsonify
from textblob import TextBlob
from git import Repo

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask! - test with Git'


@app.route('/git_update', methods=['POST'])
def git_update():
    try:
        repo = Repo('./mysite')  # Use current directory instead of hardcoded path
        origin = repo.remotes.origin
        # repo.create_head('master', origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
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
@app.route('/process_input', methods=['POST'])
def process_input():
    # Attempt to retrieve the JSON payload
    data = get_json_payload()
    if not data:
        return jsonify({"error": "Missing or invalid JSON payload."}), 400

    # Ensure the payload contains the 'text' key
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' parameter in JSON payload."}), 400

    user_text = data['text']

    # Here, implement your conversation management logic.
    # For this example, we simply echo the user's input.
    response_text = f"You said: {user_text}. What would you like to do next?"

    # Return the response as JSON
    return jsonify({"response": response_text})


# Endpoint to perform sentiment analysis
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


#if __name__ == '__main__':
    # When running locally, enable debug mode for development
#    app.run(debug=True)

