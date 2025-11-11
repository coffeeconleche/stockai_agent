# WhatsApp Business Transaction Assistant

A WhatsApp AI assistant for small businesses to register sales and purchases using text, audio, and image messages. Built with AWS Lambda, DynamoDB, and OpenAI.

## Quick Start

1. **Record transactions** via text, voice, or photo
2. **Query reports** with natural language
3. **Get Excel files** for large reports (10+ products)
4. **Group users** for consolidated analytics
5. **Track everything** automatically in DynamoDB

```bash
# Example usage
User: "Vendí 5 camisas a 25 soles cada una"
Bot: ✅ Registered! [Shows transaction details]

User: "Dame el reporte de todas mis ventas"
Bot: 📊 [Sends Excel file with 15 products]
```

## Features

### Core Features
- ✅ **WhatsApp webhook verification** - Secure webhook integration
- ✅ **User registration and management** - Automatic user onboarding
- ✅ **Text message processing** - Process sales/purchase descriptions
- ✅ **Audio message processing** - Transcribe and process voice messages
- ✅ **Image message processing** - Extract data from photos of manual records
- ✅ **Transaction storage** - Save all transactions to DynamoDB
- ✅ **Multi-language support** - Spanish interface with English support
- ✅ **Smart data extraction** - AI identifies transaction type, products, quantities, prices, etc.

### Advanced Features
- ✅ **Query Reports** - Generate transaction summaries and reports
- ✅ **Smart Report Formatting** - Automatic format selection based on data size:
  - Small reports (1-2 products): Text message
  - Medium reports (3-9 products): Image table
  - Large reports (10+ products): Excel file attachment
- ✅ **Excel Reports** - Professional multi-sheet Excel files with:
  - Executive summary with totals
  - Detailed product breakdown
  - Top 10 products analysis
  - Lima timezone (UTC-5) timestamps
- ✅ **User Groups** - Combine multiple users for consolidated reports
- ✅ **Freemium Model** - Daily interaction limits with premium upgrade option
- ✅ **AI Provider Flexibility** - Support for OpenAI, DeepSeek, Gemini, and AWS Bedrock
- ✅ **Transaction Confirmation** - Interactive buttons for edit/confirm/cancel
- ✅ **S3 Integration** - Secure file storage and presigned URLs

## Recent Updates

### Excel Reports (November 2025)
- ✨ **Document Attachments** - Excel files sent as WhatsApp documents (no long URLs)
- 📅 **Lima Timezone** - All timestamps in UTC-5 for Peruvian users
- 📊 **Professional Formatting** - Auto-adjusted columns, currency formatting, sorted data
- 📁 **Multi-Sheet Workbooks** - Summary, details, and top 10 products
- 🔄 **Smart Fallback** - Excel → Image → Text if generation fails

### User Groups
- 👥 **Multi-User Reports** - Combine transactions from multiple users
- 🏷️ **Named Groups** - Custom group names for easy identification
- 📊 **Consolidated Analytics** - Group-wide transaction summaries

### Smart Report Formatting
- 🎯 **Automatic Selection** - Best format based on data size
- 📱 **Mobile Optimized** - Clean, readable reports on any device
- 🖼️ **Image Tables** - Professional green tables for medium reports

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
- `PENDING_TRANSACTIONS_TABLE_NAME`: Pending transactions table (default: "whatsapp-pending-transactions")
- `AUTHORIZED_USERS_TABLE_NAME`: Authorized users table (default: "whatsapp-authorized-users")
- `FREEMIUM_INTERACTIONS_TABLE_NAME`: Freemium tracking table (default: "whatsapp-freemium-interactions")
- `USER_GROUPS_TABLE_NAME`: User groups table (default: "whatsapp-user-groups")

### Required for S3 (Reports & Images)
- `S3_BUCKET_NAME`: S3 bucket for images and Excel files (default: "whatsapp-ai-agent-images")

### Optional Configuration
- `AWS_REGION`: AWS region (defaults to us-east-1)
- `AI_PROVIDER`: AI provider selection - "openai" or "bedrock" (default: "openai")
- `RESPONSE_MODE`: Response format - "text", "image", or "auto" (default: "auto")
- `TRANSACTION_THRESHOLD`: Image threshold for transactions (default: 4)
- `QUERY_THRESHOLD`: Image threshold for query reports (default: 3)
- `EXCEL_THRESHOLD`: Excel file threshold for large reports (default: 10)
- `FREEMIUM_DAILY_LIMIT`: Daily interaction limit for free users (default: 5)
- `MAX_GROUP_MEMBERS`: Maximum users per group (default: 10)
- `ENABLE_USER_GROUPS`: Enable/disable user groups feature (default: true)

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

### Recording Transactions

#### Text Messages
- "Vendí 5 camisas rojas a 25 soles cada una"
- "Compré 2 kg de manzanas a 8 soles el kilo"
- "Vendí 3 docenas de huevos a 10 soles la docena"

#### Audio Messages
Users can send voice messages describing their transactions in Spanish.

#### Image Messages
Users can send photos of their handwritten or printed transaction records.

### Querying Reports

#### Simple Queries
- "Cuánto vendí de mani?" → Text response (1-2 products)
- "Dame el reporte de ventas de esta semana" → Image table (3-9 products)
- "Reporte de todas mis ventas" → Excel file (10+ products)

#### Advanced Queries
- "Ventas de mani, azucar y cafe del 2025-01-01 al 2025-01-31"
- "Compras de enero"
- "Reporte de ventas de productos perecederos"

### Excel Reports (10+ Products)

When reports contain 10 or more products, users receive:
- **Document attachment** with filename: `reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx`
- **Three sheets:**
  1. Resumen - Executive summary with totals
  2. Detalle por Producto - Full product breakdown
  3. Top 10 Productos - Top products by cost
- **Lima timezone** (UTC-5) for all timestamps
- **Professional formatting** with auto-adjusted columns and currency formatting

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

### Transaction Recording Test
Send a test message to your WhatsApp Business number:
```
"Vendí 2 polos a 15 soles cada uno"
```

The assistant should respond with the processed transaction data and confirmation buttons.

### Query Report Test

#### Small Report (Text)
```
"Cuánto vendí de polos?"
```
Expected: Text message with summary

#### Medium Report (Image)
```
"Reporte de ventas de polos, camisas, pantalones"
```
Expected: Green table image

#### Large Report (Excel)
```
"Dame el reporte de todas mis ventas"
```
Expected: Excel file attachment with professional formatting

### Excel Generation Test
Run the included test script:
```bash
python3 test_excel_simple.py
```

This generates a test Excel file and uploads it to S3.

## Documentation

### Feature Documentation
- **[Excel Reports Feature](docs/EXCEL_REPORTS_FEATURE.md)** - Complete Excel reports documentation
- **[Excel Quick Start](docs/EXCEL_QUICK_START.md)** - Quick reference guide
- **[Excel Deployment Guide](docs/EXCEL_DEPLOYMENT_GUIDE.md)** - Step-by-step deployment
- **[Excel Document Attachment](docs/EXCEL_DOCUMENT_ATTACHMENT.md)** - Document attachment implementation
- **[User Groups](docs/USER_GROUPS_IMPLEMENTATION.md)** - User groups feature
- **[Query Images](docs/QUERY_REPORT_IMAGE_FEATURE.md)** - Image table reports
- **[AI Provider Comparison](docs/AI_PROVIDER_COMPARISON.md)** - OpenAI vs Bedrock
- **[Security Audit](docs/SECURITY_AUDIT_SUMMARY.md)** - Security review

### Quick References
- **[User Groups CLI Guide](docs/USER_GROUPS_CLI_GUIDE.md)** - Command-line tools
- **[Spelling Correction](docs/SPELLING_CORRECTION_FEATURE.md)** - Text normalization
- **[AI Prompt Standardization](docs/AI_PROMPT_STANDARDIZATION.md)** - Prompt engineering

## Architecture

### Services
- **WhatsAppService** - WhatsApp Business API integration
- **OpenAIService** - AI text/audio/image processing
- **BedrockService** - AWS Bedrock AI integration (alternative)
- **MessageService** - Message routing and processing
- **QueryService** - Transaction queries and reports
- **ImageService** - Image generation for reports
- **ExcelService** - Excel file generation
- **MercadoPagoService** - Payment processing
- **FreemiumService** - Usage tracking and limits

### Data Models
- **User** - User profiles and preferences
- **Transaction** - Sales and purchase records
- **PendingTransaction** - Unconfirmed transactions
- **AuthorizedUser** - License management
- **FreemiumInteraction** - Usage tracking
- **UserGroup** - Multi-user groups

## Report Format Selection

The system automatically selects the best format based on data size:

| Products | Format | Description | Example |
|----------|--------|-------------|---------|
| 1-2 | Text | Simple text summary | "Vendiste 150 kg de mani por 450 PEN" |
| 3-9 | Image | Green table image | Professional table with all products |
| 10+ | Excel | Multi-sheet Excel file | `reporte_transacciones_20251111_1645_stockai.xlsx` |

### Report Flow

```
User Query → Count Products → Select Format
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    < 3 products  3-9 products  10+ products
        ↓           ↓           ↓
    Text Message  Image Table  Excel File
```

### Excel File Structure
1. **Resumen** - Summary with filters, totals, and generation timestamp (Lima UTC-5)
2. **Detalle por Producto** - Sorted product details with averages and currency formatting
3. **Top 10 Productos** - Top products by cost, ready for charts

**Filename Format:** `reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx`

## Feature Comparison

| Feature | Free (Freemium) | Premium |
|---------|----------------|---------|
| Daily Interactions | 5 per day | Unlimited |
| Transaction Recording | ✅ | ✅ |
| Query Reports | ✅ | ✅ |
| Excel Reports | ✅ | ✅ |
| User Groups | ✅ | ✅ |
| Image Processing | ✅ | ✅ |
| Audio Processing | ✅ | ✅ |
| Priority Support | ❌ | ✅ |
| Price | Free | S/ 99.00 (3 months) |

## Dependencies

### Python Packages
- `requests==2.31.0` - HTTP requests
- `boto3==1.34.0` - AWS SDK
- `openai==1.107.2` - OpenAI API
- `google-genai==1.36.0` - Google Gemini API
- `Pillow==10.2.0` - Image processing
- `pytz==2024.1` - Timezone support
- `pandas==2.2.2` - Excel data manipulation
- `openpyxl==3.1.2` - Excel file generation

### AWS Services
- **Lambda** - Serverless compute
- **DynamoDB** - NoSQL database
- **S3** - File storage
- **Bedrock** - AI models (optional)

## Deployment

### Standard Deployment
```bash
./deploy.sh
```

### With Excel Support
1. Create Lambda layer with pandas and openpyxl
2. Attach layer to Lambda function
3. Add `EXCEL_THRESHOLD=10` environment variable
4. Deploy code

See [Excel Deployment Guide](docs/EXCEL_DEPLOYMENT_GUIDE.md) for details.

## Troubleshooting

### Excel Reports Not Generating
- Check Lambda has pandas and openpyxl layer attached
- Verify `EXCEL_THRESHOLD` environment variable is set
- Check CloudWatch logs for errors
- Ensure Lambda has S3 permissions

### Document Attachment Fails
- System automatically falls back to URL
- Check WhatsApp API credentials
- Verify S3 presigned URL is valid
- Check file size (must be < 100 MB)

### User Groups Not Working
- Verify `ENABLE_USER_GROUPS=true`
- Check `USER_GROUPS_TABLE_NAME` exists
- Use CLI tools to manage groups: `./manage-user-groups.sh`

### Common Issues
- **"No module named 'pandas'"** → Lambda layer not attached
- **"S3 upload failed"** → Check IAM permissions
- **"Query returns no data"** → Check date format (YYYY-MM-DD)
- **"Excel generation timeout"** → Increase Lambda timeout to 30s

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software for StockAI.

## Support

For issues or questions:
- Check [Documentation](docs/)
- Review [Troubleshooting](#troubleshooting)
- Contact support team

---

**Built with ❤️ for small businesses in Peru**