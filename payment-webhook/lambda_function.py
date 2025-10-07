"""
Mercado Pago Payment Webhook Handler - Standalone Lambda Function
Handles payment notifications and auto-registers users
"""
import json
import boto3
import requests
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
AUTHORIZED_USERS_TABLE = os.getenv('AUTHORIZED_USERS_TABLE_NAME', 'whatsapp-authorized-users')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v20.0')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
authorized_users_table = dynamodb.Table(AUTHORIZED_USERS_TABLE)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for Mercado Pago payment webhooks
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse request body
        body_str = event.get('body', '{}')
        body = json.loads(body_str) if isinstance(body_str, str) else body_str
        
        logger.info(f"Parsed body: {json.dumps(body)}")
        
        # Extract payment information
        payment_type = body.get('type')
        action = body.get('action')
        payment_id = body.get('data', {}).get('id')
        
        logger.info(f"Payment notification - Type: {payment_type}, Action: {action}, ID: {payment_id}")
        
        # Process payment notification
        if payment_type == 'payment' and payment_id:
            # Verify payment with Mercado Pago
            payment_data = verify_payment(payment_id)
            
            if payment_data and payment_data['status'] == 'approved':
                # Payment approved - register user
                phone_number = payment_data.get('external_reference')
                payer_email = payment_data.get('payer_email', '')
                
                logger.info(f"Payment approved for phone: {phone_number}")
                
                if phone_number:
                    # Register user in authorized users table
                    success = register_authorized_user(phone_number, payer_email)
                    
                    if success:
                        # Send welcome message via WhatsApp
                        send_welcome_message(phone_number)
                        
                        return {
                            'statusCode': 200,
                            'body': json.dumps({
                                'status': 'success',
                                'message': 'User registered successfully'
                            })
                        }
                    else:
                        logger.error(f"Failed to register user: {phone_number}")
                else:
                    logger.error("No phone number in payment external_reference")
            else:
                status = payment_data.get('status') if payment_data else 'unknown'
                logger.info(f"Payment not approved. Status: {status}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'processed'})
        }
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def verify_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    """Verify payment status with Mercado Pago API"""
    try:
        if not MERCADOPAGO_ACCESS_TOKEN:
            logger.error("Mercado Pago access token not configured")
            return None
        
        url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
        
        headers = {
            'Authorization': f'Bearer {MERCADOPAGO_ACCESS_TOKEN}'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            payment_data = response.json()
            
            return {
                'status': payment_data.get('status'),
                'status_detail': payment_data.get('status_detail'),
                'external_reference': payment_data.get('external_reference'),
                'transaction_amount': payment_data.get('transaction_amount'),
                'currency_id': payment_data.get('currency_id'),
                'payer_email': payment_data.get('payer', {}).get('email', ''),
                'metadata': payment_data.get('metadata', {})
            }
        else:
            logger.error(f"Failed to verify payment: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return None


def register_authorized_user(phone_number: str, email: str = '') -> bool:
    """Register user in authorized users DynamoDB table with 3-month expiry"""
    try:
        from datetime import timedelta
        
        registration_date = datetime.utcnow()
        expiry_date = registration_date + timedelta(days=90)  # 3 months = 90 days
        
        item = {
            'phone_number': phone_number,
            'license_type': 'premium',
            'license_status': 'active',
            'email': email,
            'registration_date': registration_date.isoformat(),
            'expiry_date': expiry_date.isoformat(),
            'company_name': '',
            'contact_name': ''
        }
        
        authorized_users_table.put_item(Item=item)
        logger.info(f"Successfully registered user: {phone_number} (expires: {expiry_date.date()})")
        return True
        
    except Exception as e:
        logger.error(f"Error registering user {phone_number}: {str(e)}")
        return False


def send_welcome_message(phone_number: str) -> bool:
    """Send welcome message via WhatsApp"""
    try:
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            logger.warning("WhatsApp credentials not configured, skipping welcome message")
            return False
        
        url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        welcome_message = """🎉 ¡Pago confirmado! Bienvenido a StockAI

Tu licencia ha sido activada exitosamente.

¡Hola! 👋 Bienvenido/a a tu Asistente de Registro de Ventas.

Soy tu asistente de inteligencia artificial que te ayudará a registrar tus ventas y compras de manera fácil y rápida.

📝 Puedo procesar:
• Mensajes de texto
• Mensajes de voz 🎤
• Fotos de tus registros escritos 📸

💼 Registra tus transacciones diciendo algo como:
• "Vendí 5 camisas a 25 soles cada una"
• "Compré 2 kg de manzanas a 8 soles el kilo"
• O envía una foto de tu registro manual

¡Empecemos a registrar tus ventas! 🚀"""
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number.replace('+', ''),
            'type': 'text',
            'text': {
                'body': welcome_message
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Welcome message sent to {phone_number}")
            return True
        else:
            logger.error(f"Failed to send welcome message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending welcome message: {str(e)}")
        return False
