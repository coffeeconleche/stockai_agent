# -*- coding: utf-8 -*-
"""
AWS Bedrock service for processing messages
Alternative to OpenAI/DeepSeek/Gemini
"""
import boto3
import json
import logging
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class BedrockService:
    """Service for AWS Bedrock API operations"""
    
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=Config.BEDROCK_REGION)
        self.text_model = Config.BEDROCK_MODEL_TEXT
        self.vision_model = Config.BEDROCK_MODEL_VISION
        self.transcribe = boto3.client('transcribe', region_name=Config.AWS_REGION)
    
    def _invoke_claude(self, system_prompt: str, user_prompt: str, model_id: str = None, max_tokens: int = 2000) -> Optional[str]:
        """Invoke Claude model via Bedrock"""
        try:
            if model_id is None:
                model_id = self.text_model
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result_text = response_body['content'][0]['text']
            
            return result_text
            
        except Exception as e:
            logger.error(f"Error invoking Claude via Bedrock: {str(e)}")
            return None
    
    def _invoke_claude_vision(self, system_prompt: str, image_bytes: bytes, image_format: str) -> Optional[str]:
        """Invoke Claude vision model via Bedrock"""
        try:
            import base64
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Map format
            media_type_map = {
                'jpeg': 'image/jpeg',
                'jpg': 'image/jpeg',
                'png': 'image/png',
                'webp': 'image/webp'
            }
            media_type = media_type_map.get(image_format.lower(), 'image/jpeg')
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": "Analiza esta imagen y extrae la información de transacciones comerciales:"
                            }
                        ]
                    }
                ],
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.vision_model,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result_text = response_body['content'][0]['text']
            
            return result_text
            
        except Exception as e:
            logger.error(f"Error invoking Claude vision via Bedrock: {str(e)}")
            return None
    
    def process_text_message(self, text_content: str) -> Optional[Dict[str, Any]]:
        """Process text message and extract transaction data"""
        try:
            system_prompt = """Eres un asistente especializado en procesar registros de ventas y compras para pequeños negocios en Perú.
Los mensajes pueden contenter registros de más de un producto.
Tu tarea es extraer y parametrizar la siguiente información por producto de los mensajes en español:

1. transaction_type: 0 para compra (del proveedor), 1 para venta (al cliente)
2. product: El producto general en singular (ej: "camisa roja" → "camisa", "leche de cabra" → "leche de cabra")
3. product_variation: Variaciones como color, tamaño, marca, etc. (ej: "camisa roja" → "roja")
4. quantity: Cantidad numérica
5. quantity_units: Unidades en sistema internacional si es una medida del SI o en singular si es otra medida (kg, pieza, litros, etc.)
6. currency: Moneda (por defecto PEN - soles peruanos)
7. cost: **Costo total** de la transacción del producto. **NO es el precio unitario.** 
   - Si el mensaje dice "a X soles cada una" → multiplicar cantidad × precio unitario
   - Si el mensaje dice "por X soles" o "a X soles" sin "cada/c/u" → es el monto total
   - Ejemplo: "6 manzanas a 5 soles cada una" → cost: 30
   - Ejemplo: "3 camisas a 15 soles" → cost: 15 (se asume que es el total)
8. is_perishable: 0 para no perecedero como objetos, 1 para perecedero (comida, etc.)

NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos y variaciones SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Esto aplica a TODOS los campos de texto: product, product_variation, quantity_units
- Mantén las palabras en minúsculas

IMPORTANTE: 
- Si hay MÚLTIPLES transacciones en el mensaje, devuelve un array JSON con cada transacción
- Si hay UNA sola transacción, devuelve un objeto JSON
- Si el mensaje NO es sobre ventas o compras, responde con {"error": "not_business_transaction"}
- Si falta información crítica, responde con {"error": "insufficient_information"}
- Siempre responde en formato JSON válido (no devuelvas el tag de json como código, solo texto)

Ejemplos de JSON:
- Una venta: {"transaction_type": 1, "product": "camisa", "product_variation": "roja", "quantity": 5, "quantity_units": "pieza", "cost": 125, "is_perishable": 0}
- Múltiples transacciones: [{"transaction_type": 1, "product": "camisa", "quantity": 3, "cost": 30, "is_perishable": 0}, {"transaction_type": 1, "product": "manzana", "quantity": 6, "cost": 30, "is_perishable": 1}]
- Con tildes normalizadas: {"transaction_type": 1, "product": "mani", "quantity": 2, "quantity_units": "kg", "cost": 20, "is_perishable": 1}
"""

            user_prompt = f"Procesa este mensaje: '{text_content}'"
            
            result_text = self._invoke_claude(system_prompt, user_prompt)
            
            if not result_text:
                return {"error": "processing_failed"}
            
            # Clean up response
            if result_text.startswith("```json\n"):
                result_text = result_text[len("```json\n"):]
            if result_text.endswith("\n```"):
                result_text = result_text[:-len("\n```")]
            
            logger.info(f"Bedrock Claude response: {result_text}")
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                
                # Handle multiple transactions (array) or single transaction (object)
                if isinstance(result, list):
                    processed_transactions = []
                    for transaction in result:
                        if "error" in transaction:
                            continue
                        
                        processed_data = {
                            "transaction_type": transaction.get("transaction_type", 0),
                            "product": transaction.get("product", "").strip(),
                            "product_variation": transaction.get("product_variation", "") or "",
                            "quantity": float(transaction.get("quantity", 0)),
                            "quantity_units": transaction.get("quantity_units", "pieza").strip(),
                            "currency": transaction.get("currency", "PEN").strip(),
                            "cost": float(transaction.get("cost", 0)),
                            "is_perishable": transaction.get("is_perishable", 0)
                        }
                        
                        if isinstance(processed_data["product_variation"], str):
                            processed_data["product_variation"] = processed_data["product_variation"].strip()
                        
                        if processed_data["product"] and processed_data["quantity"] > 0 and processed_data["cost"] > 0:
                            processed_transactions.append(processed_data)
                    
                    return {"multiple_transactions": processed_transactions} if processed_transactions else {"error": "insufficient_information"}
                
                else:
                    if "error" in result:
                        return {"error": result["error"]}
                    
                    processed_data = {
                        "transaction_type": result.get("transaction_type", 0),
                        "product": result.get("product", "").strip(),
                        "product_variation": result.get("product_variation", "") or "",
                        "quantity": float(result.get("quantity", 0)),
                        "quantity_units": result.get("quantity_units", "pieza").strip(),
                        "currency": result.get("currency", "PEN").strip(),
                        "cost": float(result.get("cost", 0)),
                        "is_perishable": result.get("is_perishable", 0)
                    }
                    
                    if isinstance(processed_data["product_variation"], str):
                        processed_data["product_variation"] = processed_data["product_variation"].strip()
                    
                    if not processed_data["product"] or processed_data["quantity"] <= 0 or processed_data["cost"] <= 0:
                        return {"error": "insufficient_information"}
                    
                    return processed_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Bedrock JSON response: {result_text}")
                return {"error": "processing_failed"}
                
        except Exception as e:
            logger.error(f"Error processing text with Bedrock: {str(e)}")
            return {"error": "processing_failed"}
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text using Amazon Transcribe"""
        try:
            # Note: Amazon Transcribe requires S3 upload for file-based transcription
            # For real-time, you'd use TranscribeStreamingClient
            # This is a simplified version - you'd need to upload to S3 first
            
            logger.warning("Bedrock audio transcription requires S3 upload - not implemented in this version")
            logger.warning("Falling back to OpenAI Whisper for audio transcription")
            
            # Import OpenAI client for audio only
            from openai import OpenAI
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            with open(audio_file_path, 'rb') as audio_file:
                response = client.audio.transcriptions.create(
                    model=Config.OPENAI_AUDIO_MODEL,
                    file=audio_file,
                    response_format="text",
                    prompt="El siguiente audio es de una persona que está interactuando con un agente de IA que le ayuda a administrar sus inventarios de compras o ventas.",
                    language="es"
                )
            
            logger.info(f"Transcribed from audio (OpenAI Whisper): {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def process_image_message(self, image_file_path: str) -> Optional[Dict[str, Any]]:
        """Process image file and extract transaction data"""
        try:
            # Read image file
            with open(image_file_path, 'rb') as f:
                image_bytes = f.read()
            
            # Determine image format
            image_format = "jpeg"
            if image_file_path.lower().endswith('.png'):
                image_format = "png"
            elif image_file_path.lower().endswith('.webp'):
                image_format = "webp"
            
            system_prompt = """Eres un asistente que analiza imágenes de registros de ventas y compras escritos a mano o impresos.

Estás especializado en procesar registros de ventas y compras para pequeños negocios en Perú.
Las imágenes pueden contenter registros de más de un producto.
Tu tarea es extraer y parametrizar la siguiente información por producto de las imágenes en español:

1. transaction_type: 0 para compra (del proveedor), 1 para venta (al cliente)
2. product: El producto general en singular (ej: "camisa roja" → "camisa", "leche de cabra" → "leche de cabra")
3. product_variation: Variaciones como color, tamaño, marca, etc. (ej: "camisa roja" → "roja")
4. quantity: Cantidad numérica
5. quantity_units: Unidades en el Sistema Internacional (SI) y siempre en singular (ej: kg, litro, metro). Si se mencionan unidades más pequeñas (como gramos, mililitros), se deben convertir a su equivalente en el SI (ej: "200 gramos" → quantity: 0.2, quantity_units: "kg"; "700 mililitros" → quantity: 0.7, quantity_units: "litro").
6. currency: Moneda (por defecto PEN - soles peruanos)
7. cost: **Costo total** de la transacción del producto. **NO es el precio unitario.** 
   - Si el mensaje dice "a X soles cada una" → multiplicar cantidad × precio unitario
   - Si el mensaje dice "por X soles" o "a X soles" sin "cada/c/u" → es el monto total
   - Ejemplo: "6 manzanas a 5 soles cada una" → cost: 30
   - Ejemplo: "3 camisas a 15 soles" → cost: 15 (se asume que es el total)
8. is_perishable: 0 para no perecedero como objetos, 1 para perecedero (comida, etc.)

NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos y variaciones SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Esto aplica a TODOS los campos de texto: product, product_variation, quantity_units
- Mantén las palabras en minúsculas

IMPORTANTE: 
- Si hay MÚLTIPLES transacciones en la imagen, devuelve un array JSON con cada transacción
- Si hay UNA sola transacción, devuelve un objeto JSON
- Si la imagen NO contiene información de ventas/compras o no se puede leer claramente, responde con {"error": "not_business_transaction"} o {"error": "insufficient_information"}
- Siempre responde en formato JSON válido. NO INCLUYAS NINGÚN BLOQUE DE CÓDIGO (```json) EN LA RESPUESTA, SOLO EL TEXTO JSON DIRECTO.

Ejemplos de JSON:
- Una venta: {"transaction_type": 1, "product": "camisa", "product_variation": "roja", "quantity": 5, "quantity_units": "pieza", "cost": 125, "is_perishable": 0}
- Múltiples transacciones: [{"transaction_type": 1, "product": "camisa", "quantity": 3, "cost": 30, "is_perishable": 0}, {"transaction_type": 1, "product": "manzana", "quantity": 6, "cost": 30, "is_perishable": 1}]
- Con tildes normalizadas: {"transaction_type": 1, "product": "mani", "quantity": 2, "quantity_units": "kg", "cost": 20, "is_perishable": 1}
"""
            
            result_text = self._invoke_claude_vision(system_prompt, image_bytes, image_format)
            
            if not result_text:
                return {"error": "processing_failed"}
            
            # Clean up response
            if result_text.startswith("```json\n"):
                result_text = result_text[len("```json\n"):]
            if result_text.endswith("\n```"):
                result_text = result_text[:-len("\n```")]
            
            logger.info(f"Bedrock Claude vision response: {result_text}")
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                
                if isinstance(result, list):
                    processed_transactions = []
                    for transaction in result:
                        if "error" in transaction:
                            continue
                        
                        processed_data = {
                            "transaction_type": transaction.get("transaction_type", 0),
                            "product": transaction.get("product", "").strip(),
                            "product_variation": transaction.get("product_variation", "") or "",
                            "quantity": float(transaction.get("quantity", 0)),
                            "quantity_units": transaction.get("quantity_units", "pieza").strip(),
                            "currency": transaction.get("currency", "PEN").strip(),
                            "cost": float(transaction.get("cost", 0)),
                            "is_perishable": transaction.get("is_perishable", 0)
                        }
                        
                        if isinstance(processed_data["product_variation"], str):
                            processed_data["product_variation"] = processed_data["product_variation"].strip()
                        
                        if processed_data["product"] and processed_data["quantity"] > 0 and processed_data["cost"] > 0:
                            processed_transactions.append(processed_data)
                    
                    return {"multiple_transactions": processed_transactions} if processed_transactions else {"error": "insufficient_information"}
                
                else:
                    if "error" in result:
                        return {"error": result["error"]}
                    
                    processed_data = {
                        "transaction_type": result.get("transaction_type", 0),
                        "product": result.get("product", "").strip(),
                        "product_variation": result.get("product_variation", "") or "",
                        "quantity": float(result.get("quantity", 0)),
                        "quantity_units": result.get("quantity_units", "pieza").strip(),
                        "currency": result.get("currency", "PEN").strip(),
                        "cost": float(result.get("cost", 0)),
                        "is_perishable": result.get("is_perishable", 0)
                    }
                    
                    if isinstance(processed_data["product_variation"], str):
                        processed_data["product_variation"] = processed_data["product_variation"].strip()
                    
                    if not processed_data["product"] or processed_data["quantity"] <= 0 or processed_data["cost"] <= 0:
                        return {"error": "insufficient_information"}
                    
                    return processed_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Bedrock JSON response from image: {result_text}")
                return {"error": "processing_failed"}
                
        except Exception as e:
            logger.error(f"Error processing image with Bedrock: {str(e)}")
            return {"error": "processing_failed"}
    
    def process_query_request(self, text_content: str) -> Optional[Dict[str, Any]]:
        """Process query/report request and extract parameters"""
        try:
            from datetime import datetime
            import pytz
            
            peru_tz = pytz.timezone('America/Lima')
            current_date = datetime.now(peru_tz)
            current_date_str = current_date.strftime('%Y-%m-%d')
            
            system_prompt = f"""Eres un asistente especializado en procesar solicitudes de reportes de ventas y compras para pequeños negocios en Perú.

FECHA ACTUAL: {current_date_str} (Perú, GMT-5)

Tu tarea es determinar si el mensaje es una SOLICITUD DE REPORTE y extraer los parámetros de consulta.

Parámetros a extraer:
1. is_query: true si es una solicitud de reporte, false si no lo es
2. transaction_type: 0 para compras, 1 para ventas, null para ambos
3. products: Lista de productos en singular (ej: ["tomate", "manzana"])
4. date_from: Fecha inicio en formato YYYY-MM-DD (null si no se especifica)
5. date_to: Fecha fin en formato YYYY-MM-DD (null si no se especifica)

NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Mantén las palabras en minúsculas y en singular
- Esto asegura consistencia con los datos almacenados

IMPORTANTE:
- Detecta palabras clave: "reporte", "necesito saber", "cuánto", "resumen", "ventas de", "compras de", etc.
- Convierte productos a singular y sin tildes
- Si dice "mes de agosto 2024", usa date_from: "2024-08-01", date_to: "2024-08-31"
- Si dice "hoy", usa la fecha actual ({current_date_str})
- Si dice "esta semana", calcula desde el lunes de esta semana hasta hoy
- Si dice "últimos 30 días" o "último mes", resta 30 días desde hoy
- Si dice "últimos 7 días" o "última semana", resta 7 días desde hoy
- Si dice "este mes", usa desde el día 1 del mes actual hasta hoy
- Si dice "año 2024", usa "2024-01-01" a "2024-12-31"
- Si no menciona fechas, usa null para ambos
- Si no menciona productos específicos, usa lista vacía []
- Siempre responde en formato JSON válido (no devuelvas el tag de json como código, solo texto)

Ejemplos:
- "Necesito saber mi reporte de ventas de tomate y manzanas del mes de agosto 2024"
  → {{"is_query": true, "transaction_type": 1, "products": ["tomate", "manzana"], "date_from": "2024-08-01", "date_to": "2024-08-31"}}

- "Cuánto vendí de maní esta semana"
  → {{"is_query": true, "transaction_type": 1, "products": ["mani"], "date_from": "YYYY-MM-DD", "date_to": "{current_date_str}"}}

- "Mis ventas de azúcar y café de los últimos 30 días"
  → {{"is_query": true, "transaction_type": 1, "products": ["azucar", "cafe"], "date_from": "YYYY-MM-DD", "date_to": "{current_date_str}"}}

- "Dame el resumen de todas mis compras"
  → {{"is_query": true, "transaction_type": 0, "products": [], "date_from": null, "date_to": null}}

- "Vendí 5 camisas a 25 soles"
  → {{"is_query": false}}"""
            
            user_prompt = f"Analiza este mensaje: '{text_content}'"
            
            result_text = self._invoke_claude(system_prompt, user_prompt, max_tokens=500)
            
            if not result_text:
                return {"is_query": False}
            
            # Clean up response
            if result_text.startswith("```json\n"):
                result_text = result_text[len("```json\n"):]
            if result_text.endswith("\n```"):
                result_text = result_text[:-len("\n```")]
            
            logger.info(f"Bedrock Claude query response: {result_text}")
            
            try:
                result = json.loads(result_text)
                return result
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Bedrock query JSON response: {result_text}")
                return {"is_query": False}
                
        except Exception as e:
            logger.error(f"Error processing query with Bedrock: {str(e)}")
            return {"is_query": False}
