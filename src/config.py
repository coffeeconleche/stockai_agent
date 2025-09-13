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
    
    # Database Configuration
    USERS_TABLE_NAME: str = os.getenv('USERS_TABLE_NAME', 'whatsapp-users')
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    
    # Application Configuration
    DEFAULT_LANGUAGE: str = 'es'  # Spanish
    
    @classmethod
    def validate_required_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            cls.WHATSAPP_ACCESS_TOKEN,
            cls.WHATSAPP_PHONE_NUMBER_ID,
            cls.VERIFY_TOKEN
        ]
        return all(var is not None for var in required_vars)
    
    @classmethod
    def get_whatsapp_api_url(cls) -> str:
        """Get WhatsApp API base URL"""
        return f"https://graph.facebook.com/{cls.WHATSAPP_API_VERSION}/{cls.WHATSAPP_PHONE_NUMBER_ID}"