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
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    OPENAI_TEXT_MODEL: str = os.getenv('OPENAI_TEXT_MODEL', 'gpt-5-nano-2025-08-07')
    OPENAI_AUDIO_MODEL: str = os.getenv('OPENAI_AUDIO_MODEL', 'gpt-4o-transcribe') # whisper-1
    OPENAI_IMAGE_MODEL: str = os.getenv('OPENAI_IMAGE_MODEL', 'gpt-5-nano-2025-08-07')
    GEMINI_IMAGE_MODEL: str = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.5-flash')

    # Database Configuration
    USERS_TABLE_NAME: str = os.getenv('USERS_TABLE_NAME', 'whatsapp-users')
    TRANSACTIONS_TABLE_NAME: str = os.getenv('TRANSACTIONS_TABLE_NAME', 'whatsapp-transactions')
    AUTHORIZED_USERS_TABLE_NAME: str = os.getenv('AUTHORIZED_USERS_TABLE_NAME', 'whatsapp-authorized-users')
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    
    # Application Configuration
    DEFAULT_LANGUAGE: str = 'es'  # Spanish
    DEFAULT_CURRENCY: str = 'PEN'  # Peruvian Soles
    
    # Response Configuration
    RESPONSE_MODE: str = os.getenv('RESPONSE_MODE', 'auto')  # 'text', 'image', or 'auto'
    TRANSACTION_THRESHOLD: int = int(os.getenv('TRANSACTION_THRESHOLD', '4'))  # Use image if more than this number
    
    # S3 Configuration for image storage
    S3_BUCKET_NAME: str = os.getenv('S3_BUCKET_NAME', 'whatsapp-ai-agent-images')
    S3_IMAGES_PREFIX: str = 'transaction-images/'
    
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