# WhatsApp Business Transaction Assistant

A WhatsApp AI assistant for small businesses to register sales and purchases using text, audio, and image messages. Built with AWS Lambda, DynamoDB, and OpenAI.

## Features

- ✅ WhatsApp webhook verification
- ✅ User registration and management
- ✅ **Text message processing** - Process sales/purchase descriptions
- ✅ **Audio message processing** - Transcribe and process voice messages
- ✅ **Image message processing** - Extract data from photos of manual records
- ✅ **Transaction storage** - Save all transactions to DynamoDB
- ✅ **Multi-language support** - Spanish interface with English support
- ✅ **Smart data extraction** - AI identifies transaction type, products, quantities, prices, etc.

## Business Logic

The AI assistant processes business transactions and extracts:

- **Transaction Type**: Sale (1) or Purchase (0)
- **Product**: General product name (e.g., "camisa" from "camisa roja")
- **Product Variation**: Specific attributes (e.g., "roja" from "camisa roja")
- **Quantity**: Numeric amount
- **Quantity Units**: kg, pieces, liters, etc.
- **Currency**: Default PEN (Peruvian Soles)
- **Total Cost**: Calculated total price
- **Perishable**: Whether product expires (food = 1, electronics = 0)
- **Date**: Automatic timestamp

## Environment Variables Required

### Required for Webhook Verification
- `VERIFY_TOKEN`: "stockai_agent_2025"

### Required for WhatsApp API
- `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID
- `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp Business API access token

### Required for OpenAI
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_TEXT_MODEL`: Text processing model (default: "gpt-4o-mini")
- `OPENAI_AUDIO_MODEL`: Audio transcription model (default: "whisper-1")
- `OPENAI_IMAGE_MODEL`: Image processing model (default: "gpt-4o")

### Required for Database
- `USERS_TABLE_NAME`: DynamoDB users table (default: "whatsapp-users")
- `TRANSACTIONS_TABLE_NAME`: DynamoDB transactions table (default: "whatsapp-transactions")

### Optional
- `AWS_REGION`: AWS region (defaults to us-east-1)

## Project Structure

```
.
├── app.py                          # Main Lambda handler
├── src/
│   ├── config.py                   # Configuration management
│   ├── models/
│   │   ├── user.py                 # User model and database operations
│   │   └── transaction.py          # Transaction model and database operations
│   ├── services/
│   │   ├── whatsapp_service.py     # WhatsApp Business API integration
│   │   ├── openai_service.py       # OpenAI API integration
│   │   └── message_service.py      # Message processing logic
│   └── utils/
│       └── message_templates.py    # Multi-language message templates
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── setup-infrastructure.sh         # Infrastructure setup script
└── deploy.sh                      # Deployment script
```

## Setup Instructions

### 1. Infrastructure Setup
```bash
./setup-infrastructure.sh
```

This creates:
- DynamoDB tables for users and transactions
- IAM policies for Lambda access
- Basic environment variables

### 2. Update Environment Variables
```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{
        "VERIFY_TOKEN":"stockai_agent_2025",
        "USERS_TABLE_NAME":"whatsapp-users",
        "TRANSACTIONS_TABLE_NAME":"whatsapp-transactions",
        "WHATSAPP_ACCESS_TOKEN":"your_whatsapp_token",
        "WHATSAPP_PHONE_NUMBER_ID":"your_phone_number_id",
        "OPENAI_API_KEY":"your_openai_api_key"
    }' \
    --region us-east-1
```

### 3. Deploy Lambda Function
```bash
./deploy.sh
```

### 4. Configure WhatsApp Webhook
Use the Lambda Function URL as your webhook callback URL in Facebook Developer Console.

## Usage Examples

### Text Messages
- "Vendí 5 camisas rojas a 25 soles cada una"
- "Compré 2 kg de manzanas a 8 soles el kilo"
- "Vendí 3 docenas de huevos a 10 soles la docena"

### Audio Messages
Users can send voice messages describing their transactions in Spanish.

### Image Messages
Users can send photos of their handwritten or printed transaction records.

## Response Format

The AI responds with structured data:

```
Hola. Estos son los datos que he procesado:

📋 Tipo de transacción: Venta
🛍️ Producto: camisa (roja)
📊 Cantidad: 5 piezas
💰 Costo total: 125 PEN
🥬 Perecedero: No

✅ Registro guardado exitosamente.
```

## Error Handling

If the AI cannot process a message, it responds:
"No te entendí. Por favor, reenvía tu mensaje."

With specific guidance based on the error type.

## Testing

After deployment, send a test message to your WhatsApp Business number:
"Vendí 2 polos a 15 soles cada uno"

The assistant should respond with the processed transaction data.