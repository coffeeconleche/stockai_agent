# -*- coding: utf-8 -*-
"""
Mercado Pago payment service
"""
import requests
import logging
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class MercadoPagoService:
    """Service for Mercado Pago payment operations"""
    
    def __init__(self):
        self.access_token = Config.MERCADOPAGO_ACCESS_TOKEN
        self.base_url = "https://api.mercadopago.com/v1"
    
    def create_payment_preference(self, phone_number: str) -> Optional[str]:
        """Create a payment preference and return the payment link"""
        try:
            if not self.access_token:
                logger.error("Mercado Pago access token not configured")
                return None
            
            # Correct endpoint according to MP documentation
            url = "https://api.mercadopago.com/checkout/preferences"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Idempotency-Key': phone_number  # Prevent duplicate preferences
            }
            
            # Create payment preference according to MP API spec
            from datetime import datetime, timedelta
            
            # Set expiration to 24 hours from now
            expiration_date = datetime.utcnow() + timedelta(hours=24)
            
            # Generate unique reference to prevent reuse
            unique_reference = f"{phone_number}_{int(datetime.utcnow().timestamp())}"
            
            payload = {
                "items": [
                    {
                        "title": "Licencia StockAI - Asistente de Inventarios",
                        "description": "Acceso completo al asistente inteligente de gestión de inventarios",
                        "quantity": 1,
                        "currency_id": Config.LICENSE_CURRENCY,
                        "unit_price": float(Config.LICENSE_PRICE)
                    }
                ],
                "payer": {
                    "phone": {
                        "number": phone_number.replace('+', '')
                    }
                },
                "external_reference": unique_reference,  # Unique reference per payment link
                "statement_descriptor": "STOCKAI",
                "expires": True,
                "expiration_date_from": datetime.utcnow().isoformat(),
                "expiration_date_to": expiration_date.isoformat(),
                "metadata": {
                    "phone_number": phone_number,  # Store actual phone here
                    "product": "stockai_license",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            # Add optional fields if webhook URL is configured
            if Config.PAYMENT_WEBHOOK_URL:
                payload["notification_url"] = Config.PAYMENT_WEBHOOK_URL
            
            # Add back URLs if you have them
            payload["back_urls"] = {
                "success": "https://stockai.cloud/payment-success",
                "failure": "https://stockai.cloud/payment-failure",
                "pending": "https://stockai.cloud/payment-pending"
            }
            payload["auto_return"] = "approved"
            
            logger.info(f"Creating payment preference for {phone_number}")
            logger.info(f"Payload: {payload}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            logger.info(f"MP Response status: {response.status_code}")
            logger.info(f"MP Response body: {response.text}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                init_point = data.get('init_point')  # Payment link
                logger.info(f"Created payment preference for {phone_number}: {init_point}")
                return init_point
            else:
                logger.error(f"Failed to create payment preference: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating payment preference: {str(e)}")
            return None
    
    def verify_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Verify payment status"""
        try:
            if not self.access_token:
                logger.error("Mercado Pago access token not configured")
                return None
            
            url = f"{self.base_url}/payments/{payment_id}"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
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
                    'payer_email': payment_data.get('payer', {}).get('email'),
                    'metadata': payment_data.get('metadata', {})
                }
            else:
                logger.error(f"Failed to verify payment: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return None
