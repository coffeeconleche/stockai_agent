"""
Configuration module for WhatsApp AI Agent
"""
import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # WhatsApp API Configuration
    WHATSAPP_ACCESS_TOKEN: Optional[str] = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_API_VERSION: str = os.getenv('WHATSAPP_API_VERSION', 'v20.0')
    
    # Webhook Configuration
    VERIFY_TOKEN: Optional[str] = os.getenv('VERIFY_TOKEN')
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_TEXT_MODEL: str = os.getenv('OPENAI_TEXT_MODEL', 'gpt-4o-mini')
    OPENAI_AUDIO_MODEL: str = os.getenv('OPENAI_AUDIO_MODEL', 'whisper-1')
    OPENAI_IMAGE_MODEL: str = os.getenv('OPENAI_IMAGE_MODEL', 'gpt-4o')
    
    # Database Configuration
    USERS_TABLE_NAME: str = os.getenv('USERS_TABLE_NAME', 'whatsapp-users')
    TRANSACTIONS_TABLE_NAME: str = os.getenv('TRANSACTIONS_TABLE_NAME', 'whatsapp-transactions')
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    
    # Application Configuration
    DEFAULT_LANGUAGE: str = 'es'  # Spanish
    DEFAULT_CURRENCY: str = 'PEN'  # Peruvian Soles
    
    @classmethod
    def validate_required_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            cls.WHATSAPP_ACCESS_TOKEN,
            cls.WHATSAPP_PHONE_NUMBER_ID,
            cls.VERIFY_TOKEN,
            cls.OPENAI_API_KEY
        ]
        return all(var is not None for var in required_vars)
    
    @classmethod
    def get_whatsapp_api_url(cls) -> str:
        """Get WhatsApp API base URL"""
        return f"https://graph.facebook.com/{cls.WHATSAPP_API_VERSION}/{cls.WHATSAPP_PHONE_NUMBER_ID}"