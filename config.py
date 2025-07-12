"""
Configuration settings for the Knowledge Assessment Tool
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # AI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Assessment System Configuration
    DEFAULT_NUM_DOMAINS = 5  # Number of knowledge domains to assess
    MIN_DOMAINS = 3
    MAX_DOMAINS = 8

    # Assessment Configuration
    QUESTIONS_PER_DOMAIN = 15  # Target questions per domain
    MIN_QUESTIONS_PER_DOMAIN = 10
    MAX_QUESTIONS_PER_DOMAIN = 20

    # Adaptive Difficulty Algorithm
    INITIAL_DIFFICULTY = 50  # Starting difficulty (1-100 scale)
    MIN_DIFFICULTY = 10
    MAX_DIFFICULTY = 95

    # Real-time Adaptation Parameters
    DIFFICULTY_STEP_SIZE = 5  # Base step size for difficulty adjustments
    CONFIDENCE_THRESHOLD = 0.8  # Confidence threshold for difficulty changes
    STREAK_MULTIPLIER = 1.5  # Multiplier for consecutive correct/incorrect answers
    RESPONSE_TIME_FACTOR = 0.3  # Weight of response time in difficulty calculation

    # Performance Tracking
    MOVING_AVERAGE_WINDOW = 5  # Number of recent questions to consider
    MASTERY_THRESHOLD = 0.85  # Accuracy threshold to consider domain mastered
    STRUGGLE_THRESHOLD = 0.4  # Accuracy threshold to identify struggling areas

    # UI Configuration
    THEME = "soft"
    CUSTOM_CSS_PATH = "styles.css"
    
    # Validation
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        return True
