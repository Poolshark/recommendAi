from textblob import TextBlob

class Sentiment:
    def __init__(self):
        # Define sentiment-specific questions and responses
        self.sentiment_responses = {
            "happy": {
                "ask_occasion": "Are you celebrating something special today?",
                "ask_atmosphere": "Would you prefer a lively, upbeat atmosphere to match your mood?",
            },
            "neutral": {
                "ask_occasion": "Is this a casual dining experience or something specific you're looking for?",
                "ask_atmosphere": "What kind of atmosphere would you prefer - something relaxed or more energetic?",
            },
            "sad": {
                "ask_occasion": "Would you prefer a quiet, cozy place where you can relax?",
                "ask_atmosphere": "How about a restaurant with a warm, comfortable atmosphere?",
            },
            "urgent": {
                "ask_occasion": "Any special requirements I should know about?",
                "ask_atmosphere": "For quick service, would you prefer casual dining or fast-casual?",
                "ask_time_day": "When do you need the table? I'll prioritize restaurants with immediate availability."
            }
        }

    def analyze_urgency(self, user_text: str) -> bool:
        """
        Analyze if the user's message indicates urgency
        """
        # Keywords indicating urgency
        urgency_keywords = [
            'quick', 'hurry', 'fast', 'asap', 'urgent', 'soon',
            'running late', 'immediately', 'right now', 'emergency',
            'quickly', 'rush', 'short time', 'busy', 'no time'
        ]
        
        # Time-related patterns indicating urgency
        time_patterns = [
            'next hour', 'within hour', '30 minutes', '15 minutes',
            'half hour', 'quarter hour'
        ]

        text = user_text.lower()
        
        # Check for urgency keywords
        has_urgency_keywords = any(keyword in text for keyword in urgency_keywords)
        
        # Check for time patterns
        has_time_urgency = any(pattern in text for pattern in time_patterns)
        
        # Check for exclamation marks (might indicate urgency)
        has_exclamations = '!' in text
        
        # Check for repeated punctuation (!!!???)
        has_repeated_punctuation = any(p * 2 in text for p in '!?.')
        
        # Return True if multiple urgency indicators are present
        urgency_score = sum([
            has_urgency_keywords,
            has_time_urgency,
            has_exclamations and has_repeated_punctuation
        ])
        
        return urgency_score >= 1
    
    def analyze_sentiment(self, user_text: str):
        blob = TextBlob(user_text)
        sentiment = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Enhanced sentiment analysis with subjectivity consideration
        if sentiment > 0.3:
            return "happy"
        elif sentiment < -0.2:
            return "sad"
        else:
            return "neutral"
        

    def make_question_urgent(self, question: str) -> str:
        """Make questions more concise for urgent cases"""
        # Remove pleasantries and make questions more direct
        question = question.replace("Would you like", "Do you want")
        question = question.replace("Please provide", "Enter")
        question = question.replace("I would love to know", "Tell me")
        question = question.replace("Could you tell me", "What is")
        
        # Add urgency indicators when appropriate
        # if "when" in question.lower():
        #     question = "ASAP: " + question
        
        return question

    def get_follow_up_question(self, sentiment, responses):
        """Generate follow-up questions based on sentiment and previous responses"""

        if sentiment == "urgent":
            if "time_day" not in responses:
                return "What time do you need the table?"
            return "Anything else I should know for the booking?"
        elif sentiment == "sad":
            return "Would you like me to focus on restaurants known for their comfort food or peaceful atmosphere?"
        elif sentiment == "happy" and "occasion" in responses:
            return "Should I look for restaurants that are great for celebrations?"
        return None

    def get_sentiment_response(self, sentiment, user_text):
        """Generate appropriate responses based on sentiment"""

        if sentiment == "urgent":
            return "I understand you're in a hurry. I'll help you find something quickly."
        elif sentiment == "happy":
            return f"That's wonderful! {user_text}"
        elif sentiment == "sad":
            return f"I understand. Let me help you find something that might cheer you up. You said: {user_text}"
        else:
            return f"I see. You said: {user_text}"