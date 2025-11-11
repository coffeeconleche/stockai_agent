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
    
    def send_interactive_message(self, to_phone: str, message_text: str, button_text: str, button_url: str) -> bool:
        """Send an interactive message with a CTA URL button"""
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
                'to': to_phone.replace('+', ''),
                'type': 'interactive',
                'interactive': {
                    'type': 'cta_url',
                    'body': {
                        'text': message_text
                    },
                    'action': {
                        'name': 'cta_url',
                        'parameters': {
                            'display_text': button_text,
                            'url': button_url
                        }
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Interactive CTA message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send interactive CTA message to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp interactive CTA message to {to_phone}: {str(e)}")
            return False
    
    def send_image_message(self, to_phone: str, image_url: str, caption: str = "") -> bool:
        """Send an image message via WhatsApp Business API"""
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
                'to': to_phone.replace('+', ''),
                'type': 'image',
                'image': {
                    'link': image_url
                }
            }
            
            if caption:
                payload['image']['caption'] = caption
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Image message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send image message to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp image message to {to_phone}: {str(e)}")
            return False
    
    def send_document_message(self, to_phone: str, document_url: str, filename: str = None, caption: str = "") -> bool:
        """Send a document message via WhatsApp Business API"""
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
                'to': to_phone.replace('+', ''),
                'type': 'document',
                'document': {
                    'link': document_url
                }
            }
            
            if filename:
                payload['document']['filename'] = filename
            
            if caption:
                payload['document']['caption'] = caption
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Document message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send document message to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp document message to {to_phone}: {str(e)}")
            return False
    
    def send_reply_buttons(self, to_phone: str, message_text: str, buttons: list) -> bool:
        """Send an interactive message with reply buttons"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp API credentials not configured")
                return False
            
            url = f"{self.api_url}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Format buttons for WhatsApp API
            button_list = []
            for btn in buttons[:3]:  # WhatsApp allows max 3 reply buttons
                button_list.append({
                    'type': 'reply',
                    'reply': {
                        'id': btn['id'],
                        'title': btn['title']
                    }
                })
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone.replace('+', ''),
                'type': 'interactive',
                'interactive': {
                    'type': 'button',
                    'body': {
                        'text': message_text
                    },
                    'action': {
                        'buttons': button_list
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Reply buttons sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send reply buttons to {to_phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp reply buttons to {to_phone}: {str(e)}")
            return False