"""
Message processing service
"""
import logging
import requests
import tempfile
import os
from typing import Dict, Any
from src.models import User, UserRepository, Transaction, TransactionRepository
from src.services.whatsapp_service import WhatsAppService
from src.services.openai_service import OpenAIService
from src.utils.message_templates import MessageTemplates

logger = logging.getLogger(__name__)

class MessageService:
    """Service for processing incoming messages"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.transaction_repo = TransactionRepository()
        self.whatsapp_service = WhatsAppService()
        self.openai_service = OpenAIService()
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
                logger.info(f"Text message from {phone_number}")
                self._process_text_message(phone_number, text_content, user)
                
            elif message_type == 'audio':
                logger.info(f"Audio message from {phone_number}")
                self._process_audio_message(phone_number, message, user)
                
            elif message_type == 'image':
                logger.info(f"Image message from {phone_number}")
                self._process_image_message(phone_number, message, user)
                
            else:
                # Handle other unsupported message types
                response = self.templates.get_unsupported_message_response(user.language)
                self.whatsapp_service.send_text_message(phone_number, response)
                
        except Exception as e:
            logger.error(f"Error handling existing user message from {phone_number}: {str(e)}")
    
    def _process_text_message(self, phone_number: str, text_content: str, user: User) -> None:
        """Process text message from user"""
        try:
            # Send processing message
            processing_msg = self.templates.get_processing_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, processing_msg)
            
            # Process with OpenAI
            result = self.openai_service.process_text_message(text_content)
            print(result)
            if result and "error" not in result:
                # Create and save transaction
                transaction = Transaction(
                    phone_number=phone_number,
                    transaction_type=result['transaction_type'],
                    product=result['product'],
                    product_variation=result['product_variation'],
                    quantity=result['quantity'],
                    quantity_units=result['quantity_units'],
                    currency=result['currency'],
                    cost=result['cost'],
                    is_perishable=result['is_perishable'],
                    raw_message=text_content,
                    message_type='text'
                )
                
                if self.transaction_repo.create_transaction(transaction):
                    # Send success response with formatted data
                    response = self.templates.format_transaction_response(result, user.language)
                    self.whatsapp_service.send_text_message(phone_number, response)
                else:
                    # Database error
                    error_msg = self.templates.get_error_message(user.language)
                    self.whatsapp_service.send_text_message(phone_number, error_msg)
            else:
                # AI couldn't process or error occurred
                not_understood_msg = self.templates.get_not_understood_message(user.language)
                
                # Add brief explanation based on error type
                if result and result.get("error") == "not_business_transaction":
                    explanation = "\n\nPor favor, describe una venta o compra de tu negocio."
                elif result and result.get("error") == "insufficient_information":
                    explanation = "\n\nAsegúrate de incluir: producto, cantidad y precio."
                else:
                    explanation = "\n\nIntenta ser más específico con los detalles de la transacción."
                
                full_message = not_understood_msg + explanation
                self.whatsapp_service.send_text_message(phone_number, full_message)
            
            logger.info(f"Processed text message from {phone_number}")
            
        except Exception as e:
            logger.error(f"Error processing text message from {phone_number}: {str(e)}")
            error_msg = self.templates.get_error_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, error_msg)
    
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
   
    def _process_audio_message(self, phone_number: str, message: Dict[str, Any], user: User) -> None:
        """Process audio message from user"""
        try:
            # Send processing message
            processing_msg = self.templates.get_processing_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, processing_msg)
            
            # Get audio file URL from WhatsApp
            audio_id = message.get('audio', {}).get('id')
            if not audio_id:
                error_msg = self.templates.get_error_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, error_msg)
                return
            
            # Download audio file
            audio_file_path = self._download_whatsapp_media(audio_id)
            if not audio_file_path:
                error_msg = self.templates.get_error_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, error_msg)
                return
            
            try:
                # Transcribe audio to text
                transcribed_text = self.openai_service.transcribe_audio(audio_file_path)
                
                if transcribed_text:
                    # Process the transcribed text as a regular text message
                    result = self.openai_service.process_text_message(transcribed_text)
                    
                    if result and "error" not in result:
                        # Create and save transaction
                        transaction = Transaction(
                            phone_number=phone_number,
                            transaction_type=result['transaction_type'],
                            product=result['product'],
                            product_variation=result['product_variation'],
                            quantity=result['quantity'],
                            quantity_units=result['quantity_units'],
                            currency=result['currency'],
                            cost=result['cost'],
                            is_perishable=result['is_perishable'],
                            raw_message=transcribed_text,
                            message_type='audio'
                        )
                        
                        if self.transaction_repo.create_transaction(transaction):
                            response = self.templates.format_transaction_response(result, user.language)
                            self.whatsapp_service.send_text_message(phone_number, response)
                        else:
                            error_msg = self.templates.get_error_message(user.language)
                            self.whatsapp_service.send_text_message(phone_number, error_msg)
                    else:
                        not_understood_msg = self.templates.get_not_understood_message(user.language)
                        explanation = "\n\nAsegúrate de hablar claramente sobre una venta o compra."
                        full_message = not_understood_msg + explanation
                        self.whatsapp_service.send_text_message(phone_number, full_message)
                else:
                    error_msg = "No pude procesar el audio. Intenta enviar un mensaje de texto."
                    self.whatsapp_service.send_text_message(phone_number, error_msg)
                    
            finally:
                # Clean up temporary file
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
            
            logger.info(f"Processed audio message from {phone_number}")
            
        except Exception as e:
            logger.error(f"Error processing audio message from {phone_number}: {str(e)}")
            error_msg = self.templates.get_error_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, error_msg)
    
    def _process_image_message(self, phone_number: str, message: Dict[str, Any], user: User) -> None:
        """Process image message from user"""
        try:
            # Send processing message
            processing_msg = self.templates.get_processing_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, processing_msg)
            
            # Get image file URL from WhatsApp
            image_id = message.get('image', {}).get('id')
            if not image_id:
                error_msg = self.templates.get_error_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, error_msg)
                return
            
            # Get image URL for OpenAI processing
            image_url = self._get_whatsapp_media_url(image_id)
            if not image_url:
                error_msg = self.templates.get_error_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, error_msg)
                return
            
            # Process image with OpenAI
            result = self.openai_service.process_image_message(image_url)
            
            if result and "error" not in result:
                # Create and save transaction
                transaction = Transaction(
                    phone_number=phone_number,
                    transaction_type=result['transaction_type'],
                    product=result['product'],
                    product_variation=result['product_variation'],
                    quantity=result['quantity'],
                    quantity_units=result['quantity_units'],
                    currency=result['currency'],
                    cost=result['cost'],
                    is_perishable=result['is_perishable'],
                    raw_message="[Imagen procesada]",
                    message_type='image'
                )
                
                if self.transaction_repo.create_transaction(transaction):
                    response = self.templates.format_transaction_response(result, user.language)
                    self.whatsapp_service.send_text_message(phone_number, response)
                else:
                    error_msg = self.templates.get_error_message(user.language)
                    self.whatsapp_service.send_text_message(phone_number, error_msg)
            else:
                not_understood_msg = self.templates.get_not_understood_message(user.language)
                explanation = "\n\nAsegúrate de que la imagen contenga información clara de ventas o compras."
                full_message = not_understood_msg + explanation
                self.whatsapp_service.send_text_message(phone_number, full_message)
            
            logger.info(f"Processed image message from {phone_number}")
            
        except Exception as e:
            logger.error(f"Error processing image message from {phone_number}: {str(e)}")
            error_msg = self.templates.get_error_message(user.language)
            self.whatsapp_service.send_text_message(phone_number, error_msg)
    
    def _download_whatsapp_media(self, media_id: str) -> str:
        """Download media file from WhatsApp and return local path"""
        try:
            from src.config import Config
            
            # Get media URL
            url = f"https://graph.facebook.com/{Config.WHATSAPP_API_VERSION}/{media_id}"
            headers = {'Authorization': f'Bearer {Config.WHATSAPP_ACCESS_TOKEN}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
            
            media_info = response.json()
            media_url = media_info.get('url')
            
            if not media_url:
                return None
            
            # Download the actual file
            media_response = requests.get(media_url, headers=headers)
            if media_response.status_code != 200:
                return None
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
            temp_file.write(media_response.content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error downloading WhatsApp media {media_id}: {str(e)}")
            return None
    
    def _get_whatsapp_media_url(self, media_id: str) -> str:
        """Get media URL from WhatsApp for direct access"""
        try:
            from src.config import Config
            
            # Get media URL
            url = f"https://graph.facebook.com/{Config.WHATSAPP_API_VERSION}/{media_id}"
            headers = {'Authorization': f'Bearer {Config.WHATSAPP_ACCESS_TOKEN}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
            
            media_info = response.json()
            return media_info.get('url')
            
        except Exception as e:
            logger.error(f"Error getting WhatsApp media URL {media_id}: {str(e)}")
            return None