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
    
    # AI Provider Selection
    AI_PROVIDER: str = os.getenv('AI_PROVIDER', 'openai')  # 'openai' or 'bedrock'
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    OPENAI_TEXT_MODEL: str = os.getenv('OPENAI_TEXT_MODEL', 'gpt-5-nano-2025-08-07')
    OPENAI_AUDIO_MODEL: str = os.getenv('OPENAI_AUDIO_MODEL', 'gpt-4o-transcribe') # whisper-1
    OPENAI_IMAGE_MODEL: str = os.getenv('OPENAI_IMAGE_MODEL', 'gpt-5-nano-2025-08-07')
    GEMINI_IMAGE_MODEL: str = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.5-flash')
    
    # AWS Bedrock Configuration
    BEDROCK_REGION: str = os.getenv('BEDROCK_REGION', 'us-east-1')
    BEDROCK_MODEL_TEXT: str = os.getenv('BEDROCK_MODEL_TEXT', 'anthropic.claude-3-haiku-20240307-v1:0')
    BEDROCK_MODEL_VISION: str = os.getenv('BEDROCK_MODEL_VISION', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

    # Database Configuration
    USERS_TABLE_NAME: str = os.getenv('USERS_TABLE_NAME', 'whatsapp-users')
    TRANSACTIONS_TABLE_NAME: str = os.getenv('TRANSACTIONS_TABLE_NAME', 'whatsapp-transactions')
    PENDING_TRANSACTIONS_TABLE_NAME: str = os.getenv('PENDING_TRANSACTIONS_TABLE_NAME', 'whatsapp-pending-transactions')
    AUTHORIZED_USERS_TABLE_NAME: str = os.getenv('AUTHORIZED_USERS_TABLE_NAME', 'whatsapp-authorized-users')
    FREEMIUM_INTERACTIONS_TABLE_NAME: str = os.getenv('FREEMIUM_INTERACTIONS_TABLE_NAME', 'whatsapp-freemium-interactions')
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    
    # Application Configuration
    DEFAULT_LANGUAGE: str = 'es'  # Spanish
    DEFAULT_CURRENCY: str = 'PEN'  # Peruvian Soles
    
    # Response Configuration
    RESPONSE_MODE: str = os.getenv('RESPONSE_MODE', 'auto')  # 'text', 'image', or 'auto'
    TRANSACTION_THRESHOLD: int = int(os.getenv('TRANSACTION_THRESHOLD', '4'))  # Use image if more than this number
    QUERY_THRESHOLD: int = int(os.getenv('QUERY_THRESHOLD', '3'))  # Use image for reports if more than this number of products
    
    # S3 Configuration for image storage
    S3_BUCKET_NAME: str = os.getenv('S3_BUCKET_NAME', 'whatsapp-ai-agent-images')
    S3_IMAGES_PREFIX: str = 'transaction-images/'
    
    # Mercado Pago Configuration
    MERCADOPAGO_ACCESS_TOKEN: str = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
    MERCADOPAGO_PUBLIC_KEY: str = os.getenv('MERCADOPAGO_PUBLIC_KEY', '')
    LICENSE_PRICE: float = float(os.getenv('LICENSE_PRICE', '99.00'))  # Price in PEN
    LICENSE_CURRENCY: str = os.getenv('LICENSE_CURRENCY', 'PEN')
    PAYMENT_WEBHOOK_URL: str = os.getenv('PAYMENT_WEBHOOK_URL', '')
    
    # Freemium Configuration
    FREEMIUM_DAILY_LIMIT: int = int(os.getenv('FREEMIUM_DAILY_LIMIT', '5'))
    LIMA_TIMEZONE: str = 'America/Lima'
    
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