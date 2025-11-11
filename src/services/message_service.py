"""
Message processing service
"""
import logging
import requests
import tempfile
import os
from typing import Dict, Any, List
from src.models import User, UserRepository, Transaction, TransactionRepository, AuthorizedUser, AuthorizedUserRepository, PendingTransaction, PendingTransactionRepository
from src.services.whatsapp_service import WhatsAppService
from src.services.openai_service import OpenAIService
from src.services.bedrock_service import BedrockService
from src.services.image_service import ImageService
from src.services.query_service import QueryService
from src.services.mercadopago_service import MercadoPagoService
from src.services.freemium_service import FreemiumService
from src.utils.message_templates import MessageTemplates
from src.config import Config

logger = logging.getLogger(__name__)

class MessageService:
    """Service for processing incoming messages"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.transaction_repo = TransactionRepository()
        self.pending_transaction_repo = PendingTransactionRepository()
        self.authorized_user_repo = AuthorizedUserRepository()
        self.whatsapp_service = WhatsAppService()
        
        # Initialize AI service based on configuration
        if Config.AI_PROVIDER == 'bedrock':
            logger.info("Using AWS Bedrock for AI processing")
            self.ai_service = BedrockService()
        else:
            logger.info("Using OpenAI/DeepSeek/Gemini for AI processing")
            self.ai_service = OpenAIService()
        
        # Keep reference for backward compatibility
        self.openai_service = self.ai_service
        
        self.image_service = ImageService()
        self.query_service = QueryService()
        self.mercadopago_service = MercadoPagoService()
        self.freemium_service = FreemiumService()
        
        # Import Excel service here to avoid circular imports
        from src.services.excel_service import ExcelService
        self.excel_service = ExcelService()
        self.templates = MessageTemplates()
        self.response_mode = Config.RESPONSE_MODE  # 'text', 'image', or 'auto'
        self.current_user_status = None  # 'premium' or 'freemium'
    
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
                
                # Check and register user if needed
                authorized_user = self.freemium_service.check_and_register_user(normalized_phone)
                
                # Check if user can interact
                can_interact, status = self.freemium_service.can_user_interact(normalized_phone)
                
                if not can_interact:
                    self._handle_limit_reached(normalized_phone)
                    return
                
                # Store status for later use
                self.current_user_status = status  # "premium" or "freemium"
                
                # Check if user exists in our system
                user = self.user_repo.get_user(normalized_phone)
                
                if not user:
                    # New authorized user flow
                    self._handle_new_user(normalized_phone, message_data)
                else:
                    # Existing user flow
                    self._handle_existing_user(normalized_phone, message, user)
                    
        except Exception as e:
            logger.error(f"Error processing message change: {str(e)}")
    
    def _handle_limit_reached(self, phone_number: str) -> None:
        """Handle user who has reached daily interaction limit"""
        try:
            limit_message = """⚠️ Has alcanzado tu límite de interacciones gratuitas por hoy

Tu límite diario se restablecerá a medianoche (hora de Lima).

🌟 ¿Quieres interacciones ilimitadas?

Con la licencia Premium de StockAI obtendrás:
✅ Interacciones ilimitadas
✅ Acceso 24/7
✅ Soporte prioritario
✅ Todas las funciones avanzadas

💰 Solo S/ {price:.2f} por 3 meses

👉 Haz clic en 'Obtener Premium' para actualizar ahora."""
            
            payment_link = self.mercadopago_service.create_payment_preference(phone_number)
            
            if payment_link:
                self.whatsapp_service.send_interactive_message(
                    phone_number,
                    limit_message.format(price=Config.LICENSE_PRICE),
                    "Obtener Premium",
                    payment_link
                )
            else:
                # Fallback if payment link generation fails
                self.whatsapp_service.send_text_message(
                    phone_number, 
                    limit_message.format(price=Config.LICENSE_PRICE)
                )
            
            logger.info(f"Sent limit reached message to {phone_number}")
            
        except Exception as e:
            logger.error(f"Error handling limit reached for {phone_number}: {str(e)}")
    
    def _send_remaining_interactions_message(self, phone_number: str, remaining: int) -> None:
        """Send message about remaining interactions"""
        try:
            if remaining > 0:
                message = f"ℹ️ Te quedan {remaining} interacción{'es' if remaining != 1 else ''} gratuita{'s' if remaining != 1 else ''} hoy."
            else:
                message = "ℹ️ Has usado todas tus interacciones gratuitas por hoy."
            
            self.whatsapp_service.send_text_message(phone_number, message)
            logger.info(f"Sent remaining interactions message to {phone_number}: {remaining} remaining")
            
        except Exception as e:
            logger.error(f"Error sending remaining interactions message to {phone_number}: {str(e)}")
    
    def _handle_unauthorized_user(self, phone_number: str, message: Dict[str, Any]) -> None:
        """Handle message from unauthorized user or expired license"""
        try:
            # Check if user exists and get license status
            authorized_user = self.authorized_user_repo.get_authorized_user(phone_number)
            
            # IMPORTANT: Only generate payment link if user does NOT have active license
            if authorized_user and authorized_user.is_active():
                # User has ACTIVE license but somehow got here (shouldn't happen)
                # This is a safety check
                days_remaining = authorized_user.days_until_expiry()
                expiry_date_str = authorized_user.expiry_date[:10] if authorized_user.expiry_date else 'N/A'
                
                already_active_msg = f"""✅ Tu licencia ya está activa

Tu licencia de StockAI está activa y funcionando.

📅 Vence el: {expiry_date_str}
⏰ Días restantes: {days_remaining} días

No necesitas realizar ningún pago en este momento.
Te notificaremos cuando sea momento de renovar. 🚀"""
                
                self.whatsapp_service.send_text_message(phone_number, already_active_msg)
                logger.warning(f"User {phone_number} has active license but reached unauthorized handler")
                return
            
            if authorized_user and not authorized_user.is_active():
                # User exists but license expired - OK to generate payment link
                expiry_date_str = authorized_user.expiry_date[:10] if authorized_user.expiry_date else 'N/A'
                expired_message = f"""⚠️ Tu licencia de StockAI ha expirado

Tu acceso venció el: {expiry_date_str}

Para continuar disfrutando de todos los beneficios de StockAI:
🌱 Ahorrar dinero
📊 Reducir desperdicios
♻️ Contribuir a la economía circular

💰 *Renueva tu licencia por 3 meses:* S/ {Config.LICENSE_PRICE:.2f}

👉 Haz clic en 'Renovar' para reactivar tu acceso."""
                
                payment_link = self.mercadopago_service.create_payment_preference(phone_number)
                
                if payment_link:
                    self.whatsapp_service.send_interactive_message(
                        phone_number, 
                        expired_message, 
                        "Renovar", 
                        payment_link
                    )
                else:
                    self.whatsapp_service.send_text_message(phone_number, expired_message)
                
                logger.info(f"Sent renewal message to expired user: {phone_number}")
            else:
                # New user (no record) - OK to generate payment link
                payment_link = self.mercadopago_service.create_payment_preference(phone_number)
                
                if payment_link:
                    # Send unauthorized message with payment link
                    unauthorized_message = f"""✨ ¡Bienvenido a StockAI! 👋
Soy tu asistente inteligente para la optimización de inventarios, diseñado para ser potente, sencillo y práctico.

Con StockAI podrás:
🌱 Ahorrar dinero
📊 Reducir desperdicios
♻️ Contribuir a la economía circular

💰 *Precio Especial por Licencia de 3 meses:* S/ {Config.LICENSE_PRICE:.2f}

Actualmente no cuentas con una licencia activa.
👉 Para comenzar a aprovechar todos estos beneficios, haz clic en 'Registrarme' y completa tu pago de forma segura."""
                    
                    self.whatsapp_service.send_interactive_message(
                        phone_number, 
                        unauthorized_message, 
                        "Registrarme", 
                        payment_link
                    )
                    
                    logger.info(f"Sent payment link to new user: {phone_number}")
                else:
                    # Fallback if payment link generation fails
                    fallback_message = """✨ ¡Bienvenido a StockAI! 👋

Actualmente no cuentas con una licencia activa.
Por favor, visita https://stockai.cloud/ para registrarte."""
                    
                    self.whatsapp_service.send_text_message(phone_number, fallback_message)
                    logger.error(f"Failed to generate payment link for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error handling unauthorized user {phone_number}: {str(e)}")
    
    def _send_transaction_response(self, phone_number: str, transactions: List[Dict[str, Any]], user: User) -> None:
        """Send transaction response based on configured mode (text or image)"""
        try:
            # Determine response mode
            use_image = False
            
            if self.response_mode == 'image':
                use_image = True
            elif self.response_mode == 'auto':
                # Use image if transactions exceed threshold
                use_image = len(transactions) > Config.TRANSACTION_THRESHOLD
            # else: use_image = False (text mode)
            
            if use_image:
                # Generate and send image
                image_url = self.image_service.generate_transaction_image(transactions)
                
                if image_url:
                    caption = f"✅ Registré {len(transactions)} transacción{'es' if len(transactions) > 1 else ''}"
                    # Send image and wait for confirmation before sending buttons
                    image_sent = self.whatsapp_service.send_image_message(phone_number, image_url, caption)
                    
                    if image_sent:
                        # Add small delay to ensure image is delivered before buttons
                        import time
                        time.sleep(0.5)  # 500ms delay
                        # Send confirmation buttons AFTER image
                        self._send_confirmation_buttons(phone_number)
                    else:
                        # Image failed to send, fallback to text
                        logger.warning("Image send failed, falling back to text response")
                        self._send_text_response(phone_number, transactions, user)
                else:
                    # Fallback to text if image generation fails
                    logger.warning("Image generation failed, falling back to text response")
                    self._send_text_response(phone_number, transactions, user)
            else:
                # Send text response
                self._send_text_response(phone_number, transactions, user)
                
        except Exception as e:
            logger.error(f"Error sending transaction response: {str(e)}")
            # Fallback to text
            self._send_text_response(phone_number, transactions, user)
    
    def _send_text_response(self, phone_number: str, transactions: List[Dict[str, Any]], user: User) -> None:
        """Send text-based transaction response"""
        try:
            if len(transactions) > 1:
                responses = []
                for transaction_data in transactions:
                    response = self.templates.format_transaction_response(transaction_data, user.language)
                    responses.append(response)
                
                final_response = f"✅ Registré {len(transactions)} transacciones:\n\n" + "\n\n---\n\n".join(responses)
                self.whatsapp_service.send_text_message(phone_number, final_response)
            else:
                response = self.templates.format_transaction_response(transactions[0], user.language)
                self.whatsapp_service.send_text_message(phone_number, response)
            
            # Send confirmation buttons
            self._send_confirmation_buttons(phone_number)
                
        except Exception as e:
            logger.error(f"Error sending text response: {str(e)}")
    
    def _process_query_request(self, phone_number: str, query_params: Dict[str, Any], user: User) -> None:
        """Process query/report request"""
        try:
            logger.info(f"Processing query request from {phone_number}: {query_params}")
            
            # Query transactions
            transactions = self.query_service.query_transactions(phone_number, query_params)
            
            if not transactions:
                no_data_msg = "No se encontraron transacciones con los criterios especificados. 🔍"
                self.whatsapp_service.send_text_message(phone_number, no_data_msg)
                return
            
            # Summarize transactions
            summary = self.query_service.summarize_transactions(transactions)
            
            # Determine report format based on product count
            if self.query_service.should_use_excel(summary):
                # Generate and send Excel file for large reports
                excel_url, filename = self.excel_service.generate_report_excel(summary, query_params, phone_number)
                
                if excel_url and filename:
                    product_count = len(summary.get('products', []))
                    
                    # Send document attachment
                    caption = f"📊 Reporte de {product_count} productos"
                    document_sent = self.whatsapp_service.send_document_message(
                        phone_number, 
                        excel_url, 
                        filename=filename,
                        caption=caption
                    )
                    
                    if document_sent:
                        # Send additional info message
                        info_message = f"📋 El archivo Excel incluye:\n"
                        info_message += f"• Resumen ejecutivo\n"
                        info_message += f"• Detalle por producto\n"
                        info_message += f"• Top 10 productos\n"
                        info_message += f"• Datos listos para gráficos"
                        
                        self.whatsapp_service.send_text_message(phone_number, info_message)
                        logger.info(f"Sent query report as Excel document to {phone_number}: {len(transactions)} transactions")
                    else:
                        # Fallback: send URL if document send fails
                        excel_message = f"📊 **Reporte Completo en Excel**\n\n"
                        excel_message += f"📈 {product_count} productos encontrados\n"
                        excel_message += f"💾 Descarga: {excel_url}"
                        self.whatsapp_service.send_text_message(phone_number, excel_message)
                        logger.warning(f"Document send failed, sent URL instead to {phone_number}")
                else:
                    # Fallback to image if Excel generation fails
                    logger.warning("Excel generation failed, falling back to image")
                    image_url = self.image_service.generate_report_image(summary, query_params, phone_number)
                    
                    if image_url:
                        product_count = len(summary.get('products', []))
                        caption = f"📊 Reporte de {product_count} producto{'s' if product_count != 1 else ''}"
                        self.whatsapp_service.send_image_message(phone_number, image_url, caption)
                        logger.info(f"Sent query report as image (Excel fallback) to {phone_number}: {len(transactions)} transactions")
                    else:
                        # Final fallback to text
                        report_text = self.query_service.format_summary_text(summary, query_params, phone_number)
                        self.whatsapp_service.send_text_message(phone_number, report_text)
                        logger.warning(f"Both Excel and image failed, sent as text to {phone_number}")
                        
            elif self.query_service.should_use_image(summary):
                # Generate and send report image for medium reports
                image_url = self.image_service.generate_report_image(summary, query_params, phone_number)
                
                if image_url:
                    product_count = len(summary.get('products', []))
                    caption = f"📊 Reporte de {product_count} producto{'s' if product_count != 1 else ''}"
                    self.whatsapp_service.send_image_message(phone_number, image_url, caption)
                    logger.info(f"Sent query report as image to {phone_number}: {len(transactions)} transactions")
                else:
                    # Fallback to text if image generation fails
                    logger.warning("Report image generation failed, falling back to text")
                    report_text = self.query_service.format_summary_text(summary, query_params, phone_number)
                    self.whatsapp_service.send_text_message(phone_number, report_text)
            else:
                # Send as text for small reports
                report_text = self.query_service.format_summary_text(summary, query_params, phone_number)
                self.whatsapp_service.send_text_message(phone_number, report_text)
                logger.info(f"Sent query report as text to {phone_number}: {len(transactions)} transactions")
            
            # Record interaction for freemium users
            if self.current_user_status == "freemium":
                remaining = self.freemium_service.record_interaction(
                    phone_number, 
                    "query_response"
                )
                self._send_remaining_interactions_message(phone_number, remaining)
            
        except Exception as e:
            logger.error(f"Error processing query request from {phone_number}: {str(e)}")
            error_msg = "Ocurrió un error al generar el reporte. Por favor, intenta de nuevo."
            self.whatsapp_service.send_text_message(phone_number, error_msg)
    
    def _merge_transactions(self, existing: List[Dict[str, Any]], new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge new transactions with existing ones, updating or adding as needed"""
        try:
            # Create a dictionary of existing transactions by product name (case-insensitive)
            existing_dict = {}
            for trans in existing:
                product_key = trans['product'].lower().strip()
                existing_dict[product_key] = trans
            
            # Update or add new transactions
            for new_trans in new:
                product_key = new_trans['product'].lower().strip()
                # If product exists, update it; otherwise, it will be added
                existing_dict[product_key] = new_trans
            
            # Return merged list
            return list(existing_dict.values())
            
        except Exception as e:
            logger.error(f"Error merging transactions: {str(e)}")
            # If merge fails, return new transactions
            return new
    
    def _send_confirmation_buttons(self, phone_number: str) -> None:
        """Send confirmation buttons for transaction verification"""
        try:
            # Get current pending transaction to include session_id in buttons
            pending = self.pending_transaction_repo.get_pending_transaction(phone_number)
            
            if not pending:
                logger.error(f"No pending transaction found for {phone_number} when sending buttons")
                return
            
            session_id = pending.session_id
            
            confirmation_message = "Si los productos están correctamente identificados, click en *Confirmar*. Caso contrario, click en *Editar* o *Cancelar*."
            
            self.whatsapp_service.send_reply_buttons(
                phone_number,
                confirmation_message,
                [
                    {"id": f"confirm_transaction:{session_id}", "title": "Confirmar"},
                    {"id": f"edit_transaction:{session_id}", "title": "Editar"},
                    {"id": f"cancel_transaction:{session_id}", "title": "Cancelar"}
                ]
            )
            
        except Exception as e:
            logger.error(f"Error sending confirmation buttons: {str(e)}")
    
    def _process_button_response(self, phone_number: str, message: Dict[str, Any], user: User) -> None:
        """Process button click responses"""
        try:
            button_reply = message.get('interactive', {}).get('button_reply', {})
            button_id = button_reply.get('id', '')
            
            # Parse button_id to extract action and session_id
            if ':' in button_id:
                action, session_id = button_id.split(':', 1)
            else:
                # Old format without session_id (backward compatibility)
                action = button_id
                session_id = None
            
            # Get current pending transaction
            pending = self.pending_transaction_repo.get_pending_transaction(phone_number)
            
            # Validate session_id if present
            if session_id and pending:
                if pending.session_id != session_id:
                    # Button is from an old session, ignore it
                    logger.warning(f"Ignoring stale button click from {phone_number}. Expected session: {pending.session_id}, got: {session_id}")
                    stale_msg = "⚠️ Este botón ya no es válido. Por favor, usa los botones del mensaje más reciente."
                    self.whatsapp_service.send_text_message(phone_number, stale_msg)
                    return
            
            if action == 'confirm_transaction':
                if pending:
                    # Save all transactions to permanent table
                    success_count = 0
                    for transaction_data in pending.transactions_data:
                        transaction = Transaction(
                            phone_number=phone_number,
                            transaction_type=transaction_data['transaction_type'],
                            product=transaction_data['product'],
                            product_variation=transaction_data.get('product_variation', ''),
                            quantity=transaction_data['quantity'],
                            quantity_units=transaction_data['quantity_units'],
                            currency=transaction_data['currency'],
                            cost=transaction_data['cost'],
                            is_perishable=transaction_data['is_perishable'],
                            raw_message=transaction_data.get('raw_message', ''),
                            message_type=pending.message_type
                        )
                        
                        if self.transaction_repo.create_transaction(transaction):
                            success_count += 1
                    
                    # Delete pending transactions
                    self.pending_transaction_repo.delete_pending_transaction(phone_number)
                    
                    confirmation_msg = f"✅ ¡Perfecto! {success_count} transacción{'es' if success_count > 1 else ''} confirmada{'s' if success_count > 1 else ''} y guardada{'s' if success_count > 1 else ''} correctamente."
                    self.whatsapp_service.send_text_message(phone_number, confirmation_msg)
                    logger.info(f"User {phone_number} confirmed {success_count} transactions")
                    
                    # Record interaction for freemium users
                    if self.current_user_status == "freemium":
                        remaining = self.freemium_service.record_interaction(
                            phone_number, 
                            "transaction_confirmation"
                        )
                        self._send_remaining_interactions_message(phone_number, remaining)
                else:
                    error_msg = "No hay transacciones pendientes para confirmar."
                    self.whatsapp_service.send_text_message(phone_number, error_msg)
                
            elif action == 'edit_transaction':
                # User wants to edit - keep pending transactions for merging
                edit_msg = """📝 Para editar, envía la información correcta.

Puedes enviar:
• Mensaje de texto con los detalles corregidos
• Mensaje de voz
• Foto de tu registro

💡 **Importante:**
• Si mencionas productos que ya registraste, se actualizarán
• Si mencionas productos nuevos, se agregarán a la lista
• Solo envía los productos que quieres corregir o agregar

Ejemplo: "Vendí 5 camisas rojas a 25 soles cada una" """
                self.whatsapp_service.send_text_message(phone_number, edit_msg)
                logger.info(f"User {phone_number} requested to edit transactions")
            
            elif action == 'cancel_transaction':
                if pending:
                    # Delete pending transactions
                    if self.pending_transaction_repo.delete_pending_transaction(phone_number):
                        cancel_msg = "❌ Registro cancelado. Las transacciones no han sido guardadas."
                        self.whatsapp_service.send_text_message(phone_number, cancel_msg)
                        logger.info(f"User {phone_number} cancelled transaction registration")
                    else:
                        error_msg = "Error al cancelar el registro. Por favor, intenta de nuevo."
                        self.whatsapp_service.send_text_message(phone_number, error_msg)
                        logger.error(f"Failed to delete pending transaction for {phone_number}")
                else:
                    no_pending_msg = "No hay transacciones pendientes para cancelar."
                    self.whatsapp_service.send_text_message(phone_number, no_pending_msg)
            
            else:
                logger.warning(f"Unknown button action: {action}")
                
        except Exception as e:
            logger.error(f"Error processing button response from {phone_number}: {str(e)}")
    
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
                
            elif message_type == 'interactive':
                logger.info(f"Interactive button response from {phone_number}")
                self._process_button_response(phone_number, message, user)
                
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
            
            # First, check if this is a query request
            query_check = self.openai_service.process_query_request(text_content)
            
            if query_check.get('is_query'):
                # Handle query request
                self._process_query_request(phone_number, query_check, user)
                return
            
            # Process as transaction with OpenAI
            result = self.openai_service.process_text_message(text_content)
            print(result)
            if result and "error" not in result:
                # Handle multiple transactions
                if "multiple_transactions" in result:
                    transactions_data = result["multiple_transactions"]
                else:
                    # Single transaction
                    transactions_data = [result]
                
                # Check if there are pending transactions (user is editing)
                existing_pending = self.pending_transaction_repo.get_pending_transaction(phone_number)
                
                if existing_pending:
                    # Merge new transactions with existing ones
                    transactions_data = self._merge_transactions(existing_pending.transactions_data, transactions_data)
                    logger.info(f"Merged {len(transactions_data)} transactions for {phone_number}")
                
                # Save to pending transactions table
                pending_transaction = PendingTransaction(
                    phone_number=phone_number,
                    transactions_data=transactions_data,
                    message_type='text'
                )
                
                if self.pending_transaction_repo.create_pending_transaction(pending_transaction):
                    # Send response (text or image based on config)
                    self._send_transaction_response(phone_number, transactions_data, user)
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
                    # First, check if this is a query request
                    query_check = self.openai_service.process_query_request(transcribed_text)
                    
                    if query_check.get('is_query'):
                        # Handle query request
                        self._process_query_request(phone_number, query_check, user)
                        return
                    
                    # Process the transcribed text as a regular transaction message
                    result = self.openai_service.process_text_message(transcribed_text)
                    
                    if result and "error" not in result:
                        # Handle multiple transactions
                        if "multiple_transactions" in result:
                            transactions_data = result["multiple_transactions"]
                        else:
                            # Single transaction
                            transactions_data = [result]
                        
                        # Check if there are pending transactions (user is editing)
                        existing_pending = self.pending_transaction_repo.get_pending_transaction(phone_number)
                        
                        if existing_pending:
                            # Merge new transactions with existing ones
                            transactions_data = self._merge_transactions(existing_pending.transactions_data, transactions_data)
                            logger.info(f"Merged {len(transactions_data)} transactions for {phone_number}")
                        
                        # Save to pending transactions table
                        pending_transaction = PendingTransaction(
                            phone_number=phone_number,
                            transactions_data=transactions_data,
                            message_type='audio'
                        )
                        
                        if self.pending_transaction_repo.create_pending_transaction(pending_transaction):
                            self._send_transaction_response(phone_number, transactions_data, user)
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
            
            # Download image file from WhatsApp
            image_file_path = self._download_whatsapp_media(image_id)
            if not image_file_path:
                error_msg = self.templates.get_error_message(user.language)
                self.whatsapp_service.send_text_message(phone_number, error_msg)
                return
            
            try:
                # Process image with OpenAI
                result = self.openai_service.process_image_message(image_file_path)
            finally:
                # Clean up temporary file
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)
            
            if result and "error" not in result:
                # Handle multiple transactions
                if "multiple_transactions" in result:
                    transactions_data = result["multiple_transactions"]
                else:
                    # Single transaction
                    transactions_data = [result]
                
                # Check if there are pending transactions (user is editing)
                existing_pending = self.pending_transaction_repo.get_pending_transaction(phone_number)
                
                if existing_pending:
                    # Merge new transactions with existing ones
                    transactions_data = self._merge_transactions(existing_pending.transactions_data, transactions_data)
                    logger.info(f"Merged {len(transactions_data)} transactions for {phone_number}")
                
                # Save to pending transactions table
                pending_transaction = PendingTransaction(
                    phone_number=phone_number,
                    transactions_data=transactions_data,
                    message_type='image'
                )
                
                if self.pending_transaction_repo.create_pending_transaction(pending_transaction):
                    self._send_transaction_response(phone_number, transactions_data, user)
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
            
            # Determine file extension based on content type or default
            content_type = media_response.headers.get('content-type', '')
            if 'image' in content_type:
                if 'jpeg' in content_type or 'jpg' in content_type:
                    suffix = '.jpg'
                elif 'png' in content_type:
                    suffix = '.png'
                elif 'webp' in content_type:
                    suffix = '.webp'
                else:
                    suffix = '.jpg'  # Default for images
            else:
                suffix = '.ogg'  # Default for audio
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
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