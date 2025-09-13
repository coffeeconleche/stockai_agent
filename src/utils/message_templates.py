"""
Message templates for different languages and scenarios
"""
from typing import Dict, Any

class MessageTemplates:
    """Templates for various message types"""
    
    def __init__(self):
        self.templates = {
            'es': {
                'welcome': """¡Hola! 👋 Bienvenido/a a tu Asistente de Registro de Ventas.

Soy tu asistente de inteligencia artificial que te ayudará a registrar tus ventas y compras de manera fácil y rápida.

📝 Puedo procesar:
• Mensajes de texto
• Mensajes de voz 🎤
• Fotos de tus registros escritos 📸

💼 Registra tus transacciones diciendo algo como:
• "Vendí 5 camisas a 25 soles cada una"
• "Compré 2 kg de manzanas a 8 soles el kilo"
• O envía una foto de tu registro manual

¡Empecemos a registrar tus ventas! 🚀""",
                
                'processing': "Procesando tu registro... 🤖",
                
                'unsupported_message': "He recibido tu mensaje. Puedes enviar texto, audio o imágenes de tus registros. 📝🎤📸",
                
                'error': "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor, inténtalo de nuevo. 🔄",
                
                'not_understood': "No te entendí. Por favor, reenvía tu mensaje.",
                
                'transaction_success': "Hola. Estos son los datos que he procesado:",
                
                'help': """🆘 Cómo usar el asistente:

• Describe tu venta: "Vendí 3 polos a 20 soles cada uno"
• Describe tu compra: "Compré 5 kg de arroz a 4 soles el kilo"
• Envía audio describiendo la transacción 🎤
• Envía foto de tu registro manual 📸

Ejemplos:
✅ "Vendí 2 docenas de huevos a 8 soles la docena"
✅ "Compré 10 panes a 0.50 céntimos cada uno" """
            },
            
            'en': {
                'welcome': """Hello! 👋 Welcome to StockAI Agent.

I'm your artificial intelligence assistant specialized in financial market analysis and trading.

🔹 I can help you with:
• Technical analysis of stocks
• Real-time market information
• Investment strategies
• Relevant financial news
• Trading education

Simply send me a stock symbol (e.g., AAPL, TSLA) or ask me about any financial topic.

How can I help you today? 📈""",
                
                'processing': "Thank you for your message. I'm processing your query... 🤖",
                
                'unsupported_message': "I received your message. For now, I only process text messages. 📝",
                
                'error': "Sorry, an error occurred processing your message. Please try again. 🔄",
                
                'help': """🆘 Available commands:

• Send a stock symbol (e.g., AAPL, MSFT)
• Ask about technical analysis
• Request market news
• Ask for investment strategies

Example: "How is TESLA today?" or "AAPL analysis" """
            }
        }
    
    def get_welcome_message(self, language: str = 'es') -> str:
        """Get welcome message in specified language"""
        return self.templates.get(language, self.templates['es'])['welcome']
    
    def get_processing_message(self, language: str = 'es') -> str:
        """Get processing message in specified language"""
        return self.templates.get(language, self.templates['es'])['processing']
    
    def get_unsupported_message_response(self, language: str = 'es') -> str:
        """Get unsupported message response in specified language"""
        return self.templates.get(language, self.templates['es'])['unsupported_message']
    
    def get_error_message(self, language: str = 'es') -> str:
        """Get error message in specified language"""
        return self.templates.get(language, self.templates['es'])['error']
    
    def get_help_message(self, language: str = 'es') -> str:
        """Get help message in specified language"""
        return self.templates.get(language, self.templates['es'])['help']
    
    def get_transaction_success_message(self, language: str = 'es') -> str:
        """Get transaction success message in specified language"""
        return self.templates.get(language, self.templates['es'])['transaction_success']
    
    def get_not_understood_message(self, language: str = 'es') -> str:
        """Get not understood message in specified language"""
        return self.templates.get(language, self.templates['es'])['not_understood']
    
    def format_transaction_response(self, transaction_data: Dict[str, Any], language: str = 'es') -> str:
        """Format transaction data into a readable response"""
        try:
            transaction_type = "Venta" if transaction_data.get('transaction_type') == 1 else "Compra"
            product = transaction_data.get('product', '')
            variation = transaction_data.get('product_variation', '')
            quantity = transaction_data.get('quantity', 0)
            units = transaction_data.get('quantity_units', '')
            currency = transaction_data.get('currency', 'PEN')
            cost = transaction_data.get('cost', 0)
            perishable = "Sí" if transaction_data.get('is_perishable') == 1 else "No"
            
            product_full = f"{product}"
            if variation:
                product_full += f" ({variation})"
            
            response = f"""Hola. Estos son los datos que he procesado:

📋 **Tipo de transacción:** {transaction_type}
🛍️ **Producto:** {product_full}
📊 **Cantidad:** {quantity} {units}
💰 **Costo total:** {cost} {currency}
🥬 **Perecedero:** {perishable}

✅ Registro guardado exitosamente."""
            
            return response
            
        except Exception as e:
            return "Error al formatear la respuesta de la transacción."