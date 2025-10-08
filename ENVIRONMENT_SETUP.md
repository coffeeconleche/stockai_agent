# Environment Variables Setup Guide

This guide explains how to configure environment variables for the WhatsApp AI Agent with Freemium Tier support.

## Local Development (.env file)

For local development and testing, a `.env` file has been created in the project root with all required environment variables. Update the placeholder values with your actual credentials:

```bash
# WhatsApp Configuration
VERIFY_TOKEN=stockai_agent_2025
WHATSAPP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN_HERE
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID_HERE

# DynamoDB Tables
USERS_TABLE_NAME=whatsapp-users
TRANSACTIONS_TABLE_NAME=whatsapp-transactions
PENDING_TRANSACTIONS_TABLE_NAME=whatsapp-pending-transactions
AUTHORIZED_USERS_TABLE_NAME=whatsapp-authorized-users
FREEMIUM_INTERACTIONS_TABLE_NAME=whatsapp-freemium-interactions

# Freemium Configuration
FREEMIUM_DAILY_LIMIT=5

# OpenAI Configuration
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# Application Configuration
RESPONSE_MODE=auto
TRANSACTION_THRESHOLD=4

# Mercado Pago Configuration
LICENSE_PRICE=99.00
LICENSE_CURRENCY=PEN
MERCADOPAGO_ACCESS_TOKEN=YOUR_MP_ACCESS_TOKEN_HERE
PAYMENT_WEBHOOK_URL=YOUR_LAMBDA_URL/payment-webhook

# AWS Configuration
AWS_REGION=us-east-1
```

## AWS Lambda Configuration

The environment variables are automatically configured when you run the infrastructure setup script:

```bash
./setup-infrastructure.sh
```

This script will:
1. Create all required DynamoDB tables including `whatsapp-freemium-interactions`
2. Configure Lambda environment variables with freemium settings
3. Set `FREEMIUM_INTERACTIONS_TABLE_NAME=whatsapp-freemium-interactions`
4. Set `FREEMIUM_DAILY_LIMIT=5`

## Manual Lambda Environment Variable Update

If you need to manually update the Lambda environment variables, use the AWS CLI:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{
        "VERIFY_TOKEN":"stockai_agent_2025",
        "USERS_TABLE_NAME":"whatsapp-users",
        "TRANSACTIONS_TABLE_NAME":"whatsapp-transactions",
        "PENDING_TRANSACTIONS_TABLE_NAME":"whatsapp-pending-transactions",
        "AUTHORIZED_USERS_TABLE_NAME":"whatsapp-authorized-users",
        "FREEMIUM_INTERACTIONS_TABLE_NAME":"whatsapp-freemium-interactions",
        "FREEMIUM_DAILY_LIMIT":"5",
        "RESPONSE_MODE":"auto",
        "TRANSACTION_THRESHOLD":"4",
        "LICENSE_PRICE":"99.00",
        "LICENSE_CURRENCY":"PEN",
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_MP_ACCESS_TOKEN_HERE",
        "PAYMENT_WEBHOOK_URL":"YOUR_LAMBDA_URL/payment-webhook",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_ACCESS_TOKEN_HERE",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_NUMBER_ID_HERE",
        "OPENAI_API_KEY":"YOUR_OPENAI_API_KEY_HERE"
    }' \
    --region us-east-1
```

## Freemium Configuration Variables

### FREEMIUM_INTERACTIONS_TABLE_NAME
- **Value**: `whatsapp-freemium-interactions`
- **Purpose**: DynamoDB table name for tracking freemium user interactions
- **Required**: Yes

### FREEMIUM_DAILY_LIMIT
- **Value**: `5` (default)
- **Purpose**: Maximum number of free interactions per day for freemium users
- **Required**: Yes
- **Adjustable**: Change this value to modify the daily limit for all new freemium users

## Verification

After setting up environment variables, verify they are correctly configured:

### Local Development
```bash
# Check if .env file exists and contains freemium variables
grep FREEMIUM .env
```

### AWS Lambda
```bash
# Check Lambda environment variables
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --region us-east-1 \
    --query 'Environment.Variables' \
    --output json | grep -E "FREEMIUM"
```

## Troubleshooting

### Missing Environment Variables
If the application fails to start due to missing environment variables:
1. Verify `.env` file exists in project root (for local development)
2. Check Lambda configuration in AWS Console
3. Re-run `./setup-infrastructure.sh` to reconfigure

### Incorrect Table Names
If you get DynamoDB table not found errors:
1. Verify table exists: `aws dynamodb describe-table --table-name whatsapp-freemium-interactions --region us-east-1`
2. Check environment variable matches table name
3. Ensure IAM role has permissions to access the table

### Daily Limit Not Working
If the daily limit is not being enforced:
1. Verify `FREEMIUM_DAILY_LIMIT` is set in environment variables
2. Check that the value is a valid integer
3. Restart Lambda function after configuration changes

## Next Steps

After configuring environment variables:
1. Deploy the Lambda function: `./deploy.sh`
2. Test freemium functionality with a new user
3. Monitor CloudWatch logs for any configuration issues
4. Verify DynamoDB tables are being populated correctly
