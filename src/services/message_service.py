"""
Message processing service
"""
import logging
from typing import Dict, Any
from src.models import User, UserRepository
from src.services.whatsapp_service import WhatsAppService
from src.utils.message_templates import MessageTemplates

logger = logging.getLogger(__name__)

class MessageService:
    """Service for processing incoming messages"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.whatsapp_service = WhatsAppService()
        self.templates = MessageTemplates()
    
    def process_webhook_data(self, webhook_data: Dict[str, Any]) -> None:
        """Process incoming webhook data from WhatsApp"""
        try:
            if 'entry' not in webhook_data:
                return
                
            for entry in webhook_data['entry']:
                if 'changes' not in entry:
                    continue
                    
                for change in entry['changes']:
                    if change.get('field') == 'messages':
                        self._process_message_change(change['value'])
                        
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
    
    def _process_message_change(self, message_data: Dict[str, Any]) -> None:
        """Process message changes from WhatsApp webhook"""
        try:
            # Extract messages if they exist
            if 'messages' not in message_data:
                return
                
            for message in message_data['messages']:
                sender_phone = message['from']
                message_id = message['id']
                message_type = message.get('type', 'unknown')
                
                logger.info(f"Processing message from {sender_phone}, type: {message_type}")
                
                # Normalize phone number
                normalized_phone = User._normalize_phone_number(sender_phone)
                
                # Check if user exists
                user = self.user_repo.get_user(normalized_phone)
                
                if not user:
                    # New user flow
                    self._handle_new_user(normalized_phone, message_data)
                else:
                    # Existing user flow
                    self._handle_existing_user(normalized_phone, message, user)
                    
        except Exception as e:
            logger.error(f"Error processing message change: {str(e)}")
    
    def _handle_new_user(self, phone_number: str, message_data: Dict[str, Any]) -> None:
        """Handle new user registration and welcome message"""
        try:
            # Extract profile information if available
            profile_name = self._extract_profile_name(phone_number, message_data)
            
            # Create new user
            user = User(phone_number=phone_number, profile_name=profile_name)
            
            # Save to database
            if self.user_repo.create_user(user):
                # Send welcome message
                welcome_message = self.templates.get_welcome_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, welcome_message)
                logger.info(f"New user {phone_number} registered and welcomed")
            else:
                logger.error(f"Failed to register new user {phone_number}")
                
        except Exception as e:
            logger.error(f"Error handling new user {phone_number}: {str(e)}")
    
    def _handle_existing_user(self, phone_number: str, message: Dict[str, Any], user: User) -> None:
        """Handle message from existing user"""
        try:
            # Update user interaction
            self.user_repo.update_user_interaction(phone_number)
            
            message_type = message.get('type', 'unknown')
            
            if message_type == 'text':
                text_content = message.get('text', {}).get('body', '')
                logger.info(f"Text message from {phone_number}: {text_content}")
                
                # Process the text message
                self._process_text_message(phone_number, text_content, user)
                
            else:
                # Handle other message types
                response = self.templates.get_unsupported_message_response(user.language)
                self.whatsapp_service.send_text_message(phone_number, response)
                
        except Exception as e:
            logger.error(f"Error handling existing user message from {phone_number}: {str(e)}")
    
    def _process_text_message(self, phone_number: str, text_content: str, user: User) -> None:
        """Process text message from user"""
        try:
            # TODO: Implement AI processing logic here
            # For now, send acknowledgment
            response = self.templates.get_processing_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, response)
            
            logger.info(f"Processed text message from {phone_number}: {text_content}")
            
        except Exception as e:
            logger.error(f"Error processing text message from {phone_number}: {str(e)}")
    
    def _extract_profile_name(self, phone_number: str, message_data: Dict[str, Any]) -> str:
        """Extract profile name from message data"""
        try:
            if 'contacts' in message_data:
                for contact in message_data['contacts']:
                    if contact.get('wa_id') == phone_number.replace('+', ''):
                        return contact.get('profile', {}).get('name', '')
            return ""
        except Exception as e:
            logger.error(f"Error extracting profile name: {str(e)}")
            return ""