"""
WhatsApp Business API service
"""
import requests
import logging
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for WhatsApp Business API operations"""
    
    def __init__(self):
        self.access_token = Config.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = Config.get_whatsapp_api_url()
        
    def send_text_message(self, to_phone: str, message_text: str) -> bool:
        """Send a text message via WhatsApp Business API"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp API credentials not configured")
                return False
            
            url = f"{self.api_url}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone.replace('+', ''),  # Remove + for API call
                'type': 'text',
                'text': {
                    'body': message_text
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send message to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message to {to_phone}: {str(e)}")
            return False
    
    def send_template_message(self, to_phone: str, template_name: str, language_code: str = 'es', 
                            parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Send a template message via WhatsApp Business API"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp API credentials not configured")
                return False
            
            url = f"{self.api_url}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            template_payload = {
                'name': template_name,
                'language': {
                    'code': language_code
                }
            }
            
            if parameters:
                template_payload['components'] = parameters
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone.replace('+', ''),
                'type': 'template',
                'template': template_payload
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Template message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send template message to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp template message to {to_phone}: {str(e)}")
            return False