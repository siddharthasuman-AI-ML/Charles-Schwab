"""
Configuration management for BigQuery Chatbot - DEMO VERSION
Uses Gemini API instead of Vertex AI
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing environment variables and settings - DEMO MODE"""
    
    # Gemini API Settings (for demo)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Google Cloud Project Settings (dummy values for demo)
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'demo-project')
    GCP_DATASET_ID = os.getenv('GCP_DATASET_ID', 'demo-dataset')
    
    # API Settings
    API_PORT = int(os.getenv('API_PORT', '8501'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Chatbot Settings
    MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '500'))
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', '100'))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration values are set for demo mode"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "Missing GEMINI_API_KEY in .env file.\n"
                "Please add your Gemini API key to backend/.env\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        return True
    
    @classmethod
    def get_summary(cls):
        """Get a summary of current configuration (without sensitive data)"""
        return {
            'MODE': 'DEMO MODE (Gemini API)',
            'GCP_PROJECT_ID': cls.GCP_PROJECT_ID,
            'GCP_DATASET_ID': cls.GCP_DATASET_ID,
            'API_PORT': cls.API_PORT,
            'API_KEY_SET': bool(cls.GEMINI_API_KEY),
            'MAX_QUERY_LENGTH': cls.MAX_QUERY_LENGTH,
            'MAX_RESULTS': cls.MAX_RESULTS
        }






