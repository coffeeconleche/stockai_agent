# 💳 StockAI Payment Webhook Lambda

Standalone Lambda function for handling Mercado Pago payment notifications and auto-registering users.

## 🎯 Purpose

This lightweight Lambda function:
- Receives payment notifications from Mercado Pago
- Verifies payment status
- Auto-registers users in `whatsapp-authorized-users` table
- Sends welcome message via WhatsApp

## 📦 Structure

```
payment-webhook/
├── lambda_function.py          # Main handler
├── requirements.txt            # Dependencies (requests, boto3)
├── deploy-payment-webhook.sh  # Deployment script
└── README.md                   # This file
```

## 🚀 Deployment

### Quick Deploy:

```bash
cd payment-webhook
./deploy-payment-webhook.sh
```

### Manual Deploy:

1. **Install dependencies:**
```bash
pip install -r requirements.txt -t package/
```

2. **Create ZIP:**
```bash
cd package && zip -r ../payment-webhook.zip .
cd .. && zip -g payment-webhook.zip lambda_function.py
```

3. **Deploy to AWS:**
```bash
aws lambda create-function \
    --function-name stockai-payment-webhook \
    --runtime python3.12 \
    --role arn:aws:iam::ACCOUNT_ID:role/lambda-payment-webhook-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://payment-webhook.zip \
    --timeout 30 \
    --region us-east-1
```

4. **Create Function URL:**
```bash
aws lambda create-function-url-config \
    --function-name stockai-payment-webhook \
    --auth-type NONE \
    --region us-east-1
```

## ⚙️ Configuration

### Environment Variables:

```bash
MERCADOPAGO_ACCESS_TOKEN      # Your Mercado Pago access token
AUTHORIZED_USERS_TABLE_NAME   # DynamoDB table name (whatsapp-authorized-users)
WHATSAPP_ACCESS_TOKEN         # WhatsApp Business API token
WHATSAPP_PHONE_NUMBER_ID      # WhatsApp phone number ID
WHATSAPP_API_VERSION          # v20.0
AWS_REGION                    # us-east-1
```

### Update Configuration:

```bash
aws lambda update-function-configuration \
    --function-name stockai-payment-webhook \
    --environment Variables='{
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_TOKEN",
        "AUTHORIZED_USERS_TABLE_NAME":"whatsapp-authorized-users",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_ID",
        "WHATSAPP_API_VERSION":"v20.0",
        "AWS_REGION":"us-east-1"
    }' \
    --region us-east-1
```

## 🔐 IAM Permissions

The Lambda needs:

1. **Basic Execution**: `AWSLambdaBasicExecutionRole`
2. **DynamoDB Access**:
   - `dynamodb:PutItem` on `whatsapp-authorized-users`
   - `dynamodb:GetItem` on `whatsapp-authorized-users`
   - `dynamodb:UpdateItem` on `whatsapp-authorized-users`

## 🔗 Integration

### 1. Get Function URL:

```bash
aws lambda get-function-url-config \
    --function-name stockai-payment-webhook \
    --region us-east-1
```

### 2. Configure in Mercado Pago:

1. Go to https://www.mercadopago.com.pe/developers/panel
2. Navigate to "Webhooks"
3. Add your Lambda URL
4. Select "Payments" events

### 3. Update Main Lambda:

Update the main WhatsApp Lambda with the webhook URL:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{
        ...,
        "PAYMENT_WEBHOOK_URL":"https://YOUR_PAYMENT_LAMBDA_URL.lambda-url.us-east-1.on.aws/"
    }' \
    --region us-east-1
```

## 📊 Flow

```
Mercado Pago Payment
        ↓
Webhook Notification
        ↓
Payment Webhook Lambda
        ↓
Verify Payment Status
        ↓
Register User in DynamoDB
        ↓
Send Welcome Message
        ↓
User Can Use StockAI ✅
```

## 🧪 Testing

### Test with cURL:

```bash
curl -X POST https://YOUR_LAMBDA_URL.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "PAYMENT_ID"
    }
  }'
```

### Check Logs:

```bash
aws logs tail "/aws/lambda/stockai-payment-webhook" --follow --region us-east-1
```

### Verify User Registration:

```bash
aws dynamodb get-item \
    --table-name whatsapp-authorized-users \
    --key '{"phone_number": {"S": "+51949417273"}}' \
    --region us-east-1
```

## 📝 Logs

The function logs:
- Payment notifications received
- Payment verification results
- User registration status
- Welcome message delivery

## 🔧 Troubleshooting

### Payment Not Processed:
- Check Mercado Pago webhook is configured correctly
- Verify `MERCADOPAGO_ACCESS_TOKEN` is valid
- Check CloudWatch logs for errors

### User Not Registered:
- Verify DynamoDB table exists
- Check IAM permissions
- Ensure phone number is in `external_reference`

### Welcome Message Not Sent:
- Verify WhatsApp credentials
- Check phone number format
- Review CloudWatch logs

## 💡 Advantages of Separate Lambda

1. **Lightweight**: No heavy dependencies (no Pillow, OpenAI, etc.)
2. **Fast**: Quick cold start (~100ms vs ~2s)
3. **Cost-Effective**: Lower memory usage (256MB vs 1024MB)
4. **Isolated**: Payment logic separate from main app
5. **Easy to Update**: Deploy independently
6. **Better Monitoring**: Dedicated logs and metrics

## 📈 Performance

- **Cold Start**: ~100-200ms
- **Warm Execution**: ~50-100ms
- **Memory**: 256MB
- **Timeout**: 30 seconds

## 🔄 Updates

To update the function:

```bash
cd payment-webhook
./deploy-payment-webhook.sh
```

Or manually:

```bash
zip -g payment-webhook.zip lambda_function.py
aws lambda update-function-code \
    --function-name stockai-payment-webhook \
    --zip-file fileb://payment-webhook.zip \
    --region us-east-1
```

## 📞 Support

For issues or questions:
1. Check CloudWatch logs
2. Verify environment variables
3. Test with sample payload
4. Review Mercado Pago webhook logs

---

**Note**: This Lambda is completely independent from the main WhatsApp agent Lambda. It only shares the DynamoDB table for user registration.
