# 💳 Mercado Pago Payment Integration Setup Guide

## 🎯 Overview

This system integrates Mercado Pago to handle automatic user registration and payment processing for StockAI licenses.

## 🔄 Payment Flow

```
1. Unauthorized user sends message
   ↓
2. System generates personalized Mercado Pago payment link
   ↓
3. User clicks "Registrarme" button → Opens Mercado Pago checkout
   ↓
4. User completes payment (phone number embedded in payment)
   ↓
5. Mercado Pago sends webhook notification to Lambda
   ↓
6. System verifies payment and auto-registers user
   ↓
7. User receives welcome message and can start using StockAI
```

## 📋 Prerequisites

### 1. Create Mercado Pago Account
1. Go to https://www.mercadopago.com.pe/
2. Create a business account
3. Complete verification process

### 2. Get API Credentials
1. Go to https://www.mercadopago.com.pe/developers/panel
2. Navigate to "Credenciales" (Credentials)
3. Copy your **Access Token** (Production or Test)
4. Copy your **Public Key** (optional, for frontend)

## 🛠️ Configuration Steps

### Step 1: Set Environment Variables

Update your Lambda function with Mercado Pago credentials:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{
        "VERIFY_TOKEN":"stockai_agent_2025",
        "USERS_TABLE_NAME":"whatsapp-users",
        "TRANSACTIONS_TABLE_NAME":"whatsapp-transactions",
        "PENDING_TRANSACTIONS_TABLE_NAME":"whatsapp-pending-transactions",
        "AUTHORIZED_USERS_TABLE_NAME":"whatsapp-authorized-users",
        "RESPONSE_MODE":"auto",
        "TRANSACTION_THRESHOLD":"4",
        "LICENSE_PRICE":"99.00",
        "LICENSE_CURRENCY":"PEN",
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_MERCADOPAGO_ACCESS_TOKEN",
        "PAYMENT_WEBHOOK_URL":"https://YOUR_LAMBDA_URL.lambda-url.us-east-1.on.aws/payment-webhook",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_ID",
        "OPENAI_API_KEY":"YOUR_OPENAI_KEY"
    }' \
    --region us-east-1
```

### Step 2: Configure Mercado Pago Webhook

1. Go to Mercado Pago Developer Panel
2. Navigate to "Webhooks" or "Notificaciones IPN"
3. Add your webhook URL:
   ```
   https://YOUR_LAMBDA_URL.lambda-url.us-east-1.on.aws/payment-webhook
   ```
4. Select events to receive:
   - ✅ Payments
   - ✅ Payment updates

### Step 3: Test Payment Flow

#### Test Mode (Recommended First):
1. Use test credentials from Mercado Pago
2. Use test cards: https://www.mercadopago.com.pe/developers/es/docs/checkout-api/testing
3. Test card: `4509 9535 6623 3704` (Visa)
4. CVV: Any 3 digits
5. Expiry: Any future date

#### Production Mode:
1. Switch to production credentials
2. Set `LICENSE_PRICE` to your desired amount
3. Test with real payment

## 💰 Pricing Configuration

### Default Price:
- **S/ 99.00 PEN** (Peruvian Soles)

### To Change Price:
Update the `LICENSE_PRICE` environment variable:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{..., "LICENSE_PRICE":"149.00"}' \
    --region us-east-1
```

## 🔐 Security Features

1. **Phone Number Verification**: Payment link is unique per phone number
2. **External Reference**: Phone number stored as external reference
3. **Webhook Verification**: Only processes approved payments
4. **Automatic Registration**: User added to authorized table only after payment

## 📊 Payment Data Stored

When payment is approved, the system stores:

```json
{
  "phone_number": "+51949417273",
  "license_type": "premium",
  "license_status": "active",
  "email": "user@example.com",  // From Mercado Pago payer info
  "registration_date": "2025-01-10T15:30:00.000Z"
}
```

## 🎨 User Experience

### Unauthorized User Receives:
```
✨ ¡Bienvenido a StockAI! 👋
Soy tu asistente inteligente para la optimización de inventarios...

Con StockAI podrás:
🌱 Ahorrar dinero
📊 Reducir desperdicios
♻️ Contribuir a la economía circular

💰 Precio de lanzamiento: S/ 99.00

[Registrarme] ← Opens Mercado Pago checkout
```

### After Payment Approval:
```
🎉 ¡Pago confirmado! Bienvenido a StockAI

Tu licencia ha sido activada exitosamente.

[Welcome message with instructions...]
```

## 🔍 Monitoring & Debugging

### Check Payment Webhook Logs:
```bash
aws logs tail "/aws/lambda/whatsapp-ai-agent" --follow --region us-east-1 | grep "payment"
```

### Verify User Registration:
```bash
./add-authorized-user.sh list
```

### Test Webhook Manually:
```bash
curl -X POST https://YOUR_LAMBDA_URL/payment-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "PAYMENT_ID"
    }
  }'
```

## 🚨 Troubleshooting

### Payment Link Not Generated:
- Check `MERCADOPAGO_ACCESS_TOKEN` is set
- Verify token is valid (not expired)
- Check CloudWatch logs for errors

### Webhook Not Received:
- Verify webhook URL is correct in Mercado Pago panel
- Check Lambda has public URL access
- Verify webhook is configured for "payment" events

### User Not Auto-Registered:
- Check payment status is "approved"
- Verify phone number in external_reference
- Check DynamoDB table permissions

## 📝 Additional Notes

- **Payment Link Expiration**: Mercado Pago links don't expire by default
- **Multiple Payments**: System handles duplicate payments gracefully
- **Refunds**: Manual process through Mercado Pago panel
- **Currency**: Currently supports PEN (Peruvian Soles)

## 🔗 Useful Links

- [Mercado Pago API Docs](https://www.mercadopago.com.pe/developers/es/docs)
- [Checkout Preferences](https://www.mercadopago.com.pe/developers/es/reference/preferences/_checkout_preferences/post)
- [Webhooks Guide](https://www.mercadopago.com.pe/developers/es/docs/your-integrations/notifications/webhooks)
- [Test Cards](https://www.mercadopago.com.pe/developers/es/docs/checkout-api/testing)

## ✅ Checklist

- [ ] Mercado Pago account created
- [ ] API credentials obtained
- [ ] Environment variables configured
- [ ] Webhook URL configured in Mercado Pago
- [ ] Test payment completed successfully
- [ ] User auto-registered after test payment
- [ ] Welcome message received
- [ ] Production credentials configured
- [ ] Real payment tested

---

**Need Help?** Check CloudWatch logs or contact support.
