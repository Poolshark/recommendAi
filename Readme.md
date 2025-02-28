# 🤖 Recommendy - Restaurant Recommendation Engine
**Recommendy** is a restaurant recommendation engine that uses natural
language processing to recommend restaurants based on user preferences.
This project is built with Flask and uses the following modules:

- `Flask` - Web framework
- `Flask-Session` - Session management
- `Flask-SQLAlchemy` - Database ORM
- `Flask-CORS` - Cross-origin resource sharing
- `Python-DotEnv` - Environment variables
- `TextBlob` - Sentiment analysis
- `GitPython` - Git repository management
- `Requests` - HTTP requests

> This project is part of a university assignment and is not intended for production use. 
> Feel free to use the code as a reference for your own projects. **NOTE: This chatbot only
> uses a bunch of pre-defined questions and responses. It does not use any machine learning.**

There is a version of this project that is deployed to 
[PythonAnywhere](https://www.pythonanywhere.com/). Furthermore, this engine
is intended to work with a **mobile app**, which is availabe 
[here](https://github.com/Poolshark/recommendy-app). Currently, there is no 
intention to make the mobile app publicly avaulable via the app store.

## 🚀 Getting Started (Local Setup)
After cloning the repository, you have toset up the local virtual environment by
running

```bash
python3 -m venv venv
soure venv/bin/activate
```

You can deactive the environment by running
```
deactivate
```

Then install all necessary libraries by running

```bash
pip3 install -r requirements.txt
```

to install the dependencies. 

Next, create a `.env` file in the root directory and add the f
ollowing variables:

```bash
GOOGLE_API_KEY=<your-google-api-key>
SESSION_SECRET=<your-session-secret>

FLASK_APP=flask_app.py
FLASK_ENV=development
```

> The `SESSION_SECRET` can be any string you want. This engine uses the 
> [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview) 
> to get restaurant information. You can get your own API key 
> [here](https://console.cloud.google.com/apis/api/places-backend.googleapis.com/overview).

Now run the following commands to genearte and migrate the database:

```bash
python3 -m flask db init
python3 -m flask db migrate
python3 -m flask db upgrade
```
Finally, you are ready to run the Flask app:

```bash
python3 -m flask run
```

This will start the Flask server on `http://127.0.0.1:5000`.

## 📦 Project Structure

The project is structured as follows:

```bash
recommendy/
├── flask_app.py
├── instance
├── migrations
├── models/
├── modules/
├── requirements.txt
├── .env
└── README.md
```

## 📝 API Documentation
This project uses a very simple API. There are two endpoints:

### Root Endpoint `/`

```bash
METHOD: POST
BODY:
{
    "user_id": "123",
    "user_name": "John Doe"
}
```

This is the main endpoint that starts a new conversation. It returns a
JSON object with the following fields:

- `user_id`: The ID of the user
- `user_name`: The name of the user
- `state`: The current state of the conversation
- `next_question`: The next question to ask the user
- `recommendations`: A list of recommendations for the user if the user has
  made a previous request.

### Endpoint `/conversation`

```bash
METHOD: POST
BODY:
{
    "user_id": "123",
    "text": "I wnat to book a table for 2 today at 7pm"
}
```

This endpoint is used to process the user's input and return the next question. 
It returns a JSON object with the following fields:

- `user_id`: The ID of the user
- `state`: The current state of the conversation
- `sentiment`: The sentiment of the user's input
- `current_step`: The current step of the conversation
- `current_conversation`: The current conversation
- `user_info`: The user's information (the information that has been extracted from the user's input)
- `next_state`: The next state of the conversation
- `question`: The current question
- `next_question`: The next question to ask the user

### Endpoint `/git_update`

```bash
METHOD: POST
```
This endpoint is used to automatically update the repository on e.g. PythonAnywhere.

### Endpoint `/recommendations/<user_id>`

```bash
METHOD: GET
```

This endpoint is used to get the recommendations for a specific user.
It returns a JSON object with the following fields:

- `recommendations`: A list of recommendations for the user














