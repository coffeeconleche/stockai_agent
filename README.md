# WhatsApp AI Agent Lambda

A WhatsApp AI agent built with AWS Lambda using Docker images to handle large dependencies.

## Environment Variables Required

Set these environment variables in your Lambda function:

### Required for Webhook Verification
- `VERIFY_TOKEN`: "stockai_agent_2025"

### Required for WhatsApp API (add these later)
- `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID
- `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp Business API access token
- `WEBHOOK_VERIFY_TOKEN`: Same as VERIFY_TOKEN for consistency

### Optional
- `AWS_REGION`: AWS region (defaults to us-east-1)

## Project Structure

```
.
├── app.py              # Main Lambda function
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── deploy.sh          # Deployment script
└── README.md          # This file
```

## Features

- ✅ WhatsApp webhook verification
- ✅ Message receipt handling
- 🔄 AI message processing (to be implemented)
- 🔄 WhatsApp API integration (to be implemented)

## Deployment

Run the deployment script:
```bash
./deploy.sh
```

## Testing

After deployment, use the Lambda function URL as your WhatsApp webhook callback URL.