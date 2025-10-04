import json
import sys
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modular services
from src.config import Config
from src.services import MessageService

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for WhatsApp webhook verification and message processing
    """
    print("PRINT: entered", flush=True)
    logging.info("LOGGER: info alive")
    sys.stderr.write("STDERR: line\n"); sys.stderr.flush()
    try:
        # Lambda Function URLs use different event structure than API Gateway
        http_method = event.get('requestContext', {}).get('http', {}).get('method', '')
        query_params = event.get('queryStringParameters') or {}
        
        logger.info(f"Received {http_method} request")
        
        if http_method == 'GET':
            return handle_webhook_verification(query_params)
        elif http_method == 'POST':
            return handle_webhook_message(event)
        else:
            logger.warning(f"Unsupported method: {http_method}")
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_webhook_verification(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle WhatsApp webhook verification (GET request)
    """
    verify_token = Config.VERIFY_TOKEN
    
    if not verify_token:
        logger.error("VERIFY_TOKEN environment variable not set")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Server configuration error'})
        }
    
    # Extract verification parameters
    mode = query_params.get('hub.mode')
    token = query_params.get('hub.verify_token')
    challenge = query_params.get('hub.challenge')
    
    logger.info(f"Webhook verification attempt - mode: {mode}")
    
    # Verify the webhook
    if mode == 'subscribe' and token == verify_token:
        logger.info("Webhook verification successful")
        return {
            'statusCode': 200,
            'body': challenge,
            'headers': {
                'Content-Type': 'text/plain'
            }
        }
    else:
        logger.warning("Webhook verification failed")
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Forbidden'})
        }

def handle_webhook_message(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming WhatsApp messages (POST request)
    """
    try:
        body_str = event.get('body', '{}')
        body = json.loads(body_str)
        
        logger.info("Received WhatsApp webhook message")
        
        # Validate configuration
        if not Config.validate_required_config():
            logger.error("Required configuration missing")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Server configuration error'})
            }
        
        # Process message using our service
        message_service = MessageService()
        message_service.process_webhook_data(body)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'received'})
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except Exception as e:
        logger.error(f"Error processing webhook message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

# Test function locally - this won't run in Lambda
if __name__ == "__main__":
    print("Testing locally...")
    test_event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "hub.mode": "subscribe",
            "hub.verify_token": "stockai_agent_2025",
            "hub.challenge": "test_challenge_123"
        }
    }
    
    class MockContext:
        pass
    
    result = lambda_handler(test_event, MockContext())
    print(f"Test result: {result}")