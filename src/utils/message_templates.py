"""
Message templates for different languages and scenarios
"""

class MessageTemplates:
    """Templates for various message types"""
    
    def __init__(self):
        self.templates = {
            'es': {
                'welcome': """¡Hola! 👋 Bienvenido/a a StockAI Agent.

Soy tu asistente de inteligencia artificial especializado en análisis de mercados financieros y trading. 

🔹 Puedo ayudarte con:
• Análisis técnico de acciones
• Información de mercados en tiempo real  
• Estrategias de inversión
• Noticias financieras relevantes
• Educación sobre trading

Simplemente envíame el símbolo de una acción (ej: AAPL, TSLA) o pregúntame sobre cualquier tema financiero.

¿En qué puedo ayudarte hoy? 📈""",
                
                'processing': "Gracias por tu mensaje. Estoy procesando tu consulta... 🤖",
                
                'unsupported_message': "He recibido tu mensaje. Por ahora solo proceso mensajes de texto. 📝",
                
                'error': "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor, inténtalo de nuevo. 🔄",
                
                'help': """🆘 Comandos disponibles:

• Envía un símbolo de acción (ej: AAPL, MSFT)
• Pregunta sobre análisis técnico
• Solicita noticias del mercado
• Pide estrategias de inversión

Ejemplo: "¿Cómo está TESLA hoy?" o "Análisis de AAPL" """
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