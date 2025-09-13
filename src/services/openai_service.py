"""
OpenAI service for processing messages
"""
import openai
import json
import logging
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API operations"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.text_model = Config.OPENAI_TEXT_MODEL
        self.audio_model = Config.OPENAI_AUDIO_MODEL
        self.image_model = Config.OPENAI_IMAGE_MODEL
    
    def process_text_message(self, text_content: str) -> Optional[Dict[str, Any]]:
        """Process text message and extract transaction data"""
        try:
            system_prompt = """Eres un asistente especializado en procesar registros de ventas y compras para pequeños negocios en Perú.

Tu tarea es extraer y parametrizar la siguiente información de los mensajes en español:

1. transaction_type: 0 para compra (del proveedor), 1 para venta (al cliente)
2. product: El producto general (ej: "camisa roja" → "camisa", "leche de cabra" → "leche de cabra")
3. product_variation: Variaciones como color, tamaño, marca, etc. (ej: "camisa roja" → "roja")
4. quantity: Cantidad numérica
5. quantity_units: Unidades (kg, piezas, litros, etc.)
6. currency: Moneda (por defecto PEN - soles peruanos)
7. cost: Precio total (ej: "3 camisas a 30 soles cada una" → 90)
8. is_perishable: 0 para no perecedero, 1 para perecedero (comida, etc.)

IMPORTANTE: 
- Si el mensaje NO es sobre ventas o compras, responde con {"error": "not_business_transaction"}
- Si falta información crítica, responde con {"error": "insufficient_information"}
- Siempre responde en formato JSON válido (no devuelvas el tag de json como código, solo texto)

Ejemplos:
- "Vendí 5 camisas rojas a 25 soles cada una" → transaction_type: 1, product: "camisa", product_variation: "roja", quantity: 5, quantity_units: "piezas", cost: 125
- "Compré 2 kg de manzanas a 8 soles el kilo" → transaction_type: 0, product: "manzana", quantity: 2, quantity_units: "kg", cost: 16, is_perishable: 1"""

            user_prompt = f"Procesa este mensaje: '{text_content}'"
            
            response = openai.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                
                # Check for errors
                if "error" in result:
                    return {"error": result["error"]}
                
                # Validate and set defaults
                processed_data = {
                    "transaction_type": result.get("transaction_type", 0),
                    "product": result.get("product", "").strip(),
                    "product_variation": result.get("product_variation", "").strip(),
                    "quantity": float(result.get("quantity", 0)),
                    "quantity_units": result.get("quantity_units", "piezas").strip(),
                    "currency": result.get("currency", "PEN").strip(),
                    "cost": float(result.get("cost", 0)),
                    "is_perishable": result.get("is_perishable", 0)
                }
                
                # Basic validation
                if not processed_data["product"] or processed_data["quantity"] <= 0 or processed_data["cost"] <= 0:
                    return {"error": "insufficient_information"}
                
                return processed_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI JSON response: {result_text}")
                return {"error": "processing_failed"}
                
        except Exception as e:
            logger.error(f"Error processing text with OpenAI: {str(e)}")
            return {"error": "processing_failed"}
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = openai.audio.transcriptions.create(
                    model=self.audio_model,
                    file=audio_file,
                    language="es"  # Spanish
                )
                
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def process_image_message(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Process image and extract transaction data"""
        try:
            system_prompt = """Eres un asistente que analiza imágenes de registros de ventas y compras escritos a mano o impresos.

Extrae la información de transacciones comerciales de la imagen y devuelve los datos en el mismo formato JSON que usas para texto (no devuelvas en formato de código de json, solo texto):

1. transaction_type: 0 para compra, 1 para venta
2. product: Producto general
3. product_variation: Variaciones (color, tamaño, etc.)
4. quantity: Cantidad numérica
5. quantity_units: Unidades
6. currency: Moneda (por defecto PEN)
7. cost: Precio total
8. is_perishable: 0 o 1

Si la imagen NO contiene información de ventas/compras o no se puede leer claramente, responde con {"error": "not_business_transaction"} o {"error": "insufficient_information"}."""

            response = openai.chat.completions.create(
                model=self.image_model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen y extrae la información de transacciones comerciales:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                
                # Check for errors
                if "error" in result:
                    return {"error": result["error"]}
                
                # Validate and set defaults (same as text processing)
                processed_data = {
                    "transaction_type": result.get("transaction_type", 0),
                    "product": result.get("product", "").strip(),
                    "product_variation": result.get("product_variation", "").strip(),
                    "quantity": float(result.get("quantity", 0)),
                    "quantity_units": result.get("quantity_units", "piezas").strip(),
                    "currency": result.get("currency", "PEN").strip(),
                    "cost": float(result.get("cost", 0)),
                    "is_perishable": result.get("is_perishable", 0)
                }
                
                # Basic validation
                if not processed_data["product"] or processed_data["quantity"] <= 0 or processed_data["cost"] <= 0:
                    return {"error": "insufficient_information"}
                
                return processed_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI JSON response from image: {result_text}")
                return {"error": "processing_failed"}
                
        except Exception as e:
            logger.error(f"Error processing image with OpenAI: {str(e)}")
            return {"error": "processing_failed"}