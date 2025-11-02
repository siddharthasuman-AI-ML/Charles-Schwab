"""
Configuration management for BigQuery Chatbot
Loads environment variables and provides centralized configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing environment variables and settings"""
    
    # Google Cloud Project Settings
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
    GCP_DATASET_ID = os.getenv('GCP_DATASET_ID', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # BigQuery Settings
    BIGQUERY_LOCATION = os.getenv('BIGQUERY_LOCATION', 'US')
    
    # Vertex AI Settings
    VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    VERTEX_AI_MODEL = os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash')
    
    # API Settings
    API_PORT = int(os.getenv('API_PORT', '8501'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Chatbot Settings
    MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '500'))
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', '100'))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration values are set"""
        required_fields = [
            'GCP_PROJECT_ID',
            'GCP_DATASET_ID',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}\n"
                f"Please set these in your .env file or environment variables."
            )
        
        return True
    
    @classmethod
    def get_summary(cls):
        """Get a summary of current configuration (without sensitive data)"""
        return {
            'GCP_PROJECT_ID': cls.GCP_PROJECT_ID,
            'GCP_DATASET_ID': cls.GCP_DATASET_ID,
            'BIGQUERY_LOCATION': cls.BIGQUERY_LOCATION,
            'VERTEX_AI_LOCATION': cls.VERTEX_AI_LOCATION,
            'VERTEX_AI_MODEL': cls.VERTEX_AI_MODEL,
            'API_PORT': cls.API_PORT,
            'CREDENTIALS_SET': bool(cls.GOOGLE_APPLICATION_CREDENTIALS)
        }
