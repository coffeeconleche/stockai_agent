# 🎁 Freemium Tier Deployment Guide

## 🎯 Overview

The freemium tier system allows users to interact with StockAI with a daily limit of 5 interactions before requiring a premium license purchase. This guide covers the deployment and configuration of the freemium tier feature.

## 📊 DynamoDB Table: Freemium Interactions

### Table Details

- **Table Name**: `whatsapp-freemium-interactions`
- **Partition Key**: `phone_number` (String)
- **Billing Mode**: PAY_PER_REQUEST (on-demand)
- **Region**: us-east-1 (or your configured region)

### Table Schema

```json
{
  "phone_number": "+51949417273",
  "interaction_count": 3,
  "last_reset_date": "2025-10-07",
  "daily_limit": 5
}
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `phone_number` | String | User's phone number (partition key) |
| `interaction_count` | Number | Current day's interaction count |
| `last_reset_date` | String | Date of last reset (YYYY-MM-DD format) |
| `daily_limit` | Number | Maximum interactions per day (default: 5) |

## 🚀 Deployment Steps

### Option 1: Automated Setup (Recommended)

Run the infrastructure setup script which now includes the freemium interactions table:

```bash
./setup-infrastructure.sh
```

This script will:
1. Create the `whatsapp-freemium-interactions` DynamoDB table
2. Configure IAM policies for table access
3. Set up Lambda environment variables including `FREEMIUM_INTERACTIONS_TABLE_NAME` and `FREEMIUM_DAILY_LIMIT`

### Option 2: Manual Table Creation

If you need to create the table manually or separately:

```bash
aws dynamodb create-table \
    --table-name whatsapp-freemium-interactions \
    --attribute-definitions \
        AttributeName=phone_number,AttributeType=S \
    --key-schema \
        AttributeName=phone_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

Wait for the table to be active:

```bash
aws dynamodb wait table-exists \
    --table-name whatsapp-freemium-interactions \
    --region us-east-1
```

## ⚙️ Environment Variables

### Required Variables

Add these environment variables to your Lambda function:

```bash
FREEMIUM_INTERACTIONS_TABLE_NAME=whatsapp-freemium-interactions
FREEMIUM_DAILY_LIMIT=5
```

### Update Lambda Configuration

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
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_MP_ACCESS_TOKEN",
        "PAYMENT_WEBHOOK_URL":"YOUR_LAMBDA_URL/payment-webhook",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_ID",
        "OPENAI_API_KEY":"YOUR_OPENAI_KEY"
    }' \
    --region us-east-1
```

## 🔐 IAM Permissions

Ensure your Lambda execution role has permissions to access the freemium interactions table:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:*:table/whatsapp-freemium-interactions"
            ]
        }
    ]
}
```

## 🔄 How It Works

### User Flow

1. **New User**: Automatically registered as freemium in `whatsapp-authorized-users` table
2. **First Interaction**: Creates record in `whatsapp-freemium-interactions` with count=0
3. **Each Interaction**: Increments count, sends remaining interactions message
4. **Limit Reached**: Sends Mercado Pago payment link to upgrade to premium
5. **Daily Reset**: At midnight Lima time (UTC-5), count resets to 0

### Interaction Types

Only these actions count as interactions:
- ✅ **Transaction Confirmation**: Moving data from pending to permanent storage
- ✅ **Query Response**: Successful information query from the system

These do NOT count:
- ❌ Transaction edits
- ❌ Failed queries
- ❌ Error messages
- ❌ Welcome messages

## 📝 Configuration Options

### Changing Daily Limit

To change the default daily limit from 5 to another value:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{..., "FREEMIUM_DAILY_LIMIT":"10"}' \
    --region us-east-1
```

**Note**: This only affects NEW users. Existing users retain their current `daily_limit` value.

### Timezone Configuration

The system uses Lima, Peru timezone (America/Lima, UTC-5) for daily resets. This is configured in `src/config.py`:

```python
LIMA_TIMEZONE: str = 'America/Lima'
```

## 🔍 Monitoring & Verification

### Check Table Status

```bash
aws dynamodb describe-table \
    --table-name whatsapp-freemium-interactions \
    --region us-east-1
```

### View User Interaction Data

```bash
aws dynamodb get-item \
    --table-name whatsapp-freemium-interactions \
    --key '{"phone_number": {"S": "+51949417273"}}' \
    --region us-east-1
```

### Scan All Freemium Users

```bash
aws dynamodb scan \
    --table-name whatsapp-freemium-interactions \
    --region us-east-1
```

### Monitor Lambda Logs

```bash
aws logs tail "/aws/lambda/whatsapp-ai-agent" --follow --region us-east-1 | grep "freemium"
```

## 🧪 Testing

### Test Freemium Flow

1. Send a message from a new phone number
2. Verify user is auto-registered as freemium
3. Confirm a transaction (count = 1)
4. Check remaining interactions message
5. Repeat until limit reached (5 interactions)
6. Verify payment prompt is sent

### Test Daily Reset

1. Set user to limit (5 interactions)
2. Manually update `last_reset_date` to yesterday:
   ```bash
   aws dynamodb update-item \
       --table-name whatsapp-freemium-interactions \
       --key '{"phone_number": {"S": "+51949417273"}}' \
       --update-expression "SET last_reset_date = :date" \
       --expression-attribute-values '{":date": {"S": "2025-10-06"}}' \
       --region us-east-1
   ```
3. Send new message
4. Verify count is reset to 0

### Test Premium Upgrade

1. Complete payment as freemium user
2. Verify `license_type` updated to "premium" in `whatsapp-authorized-users`
3. Send message
4. Verify no interaction counting or remaining messages

## 🚨 Troubleshooting

### Table Not Found Error

**Symptom**: Lambda logs show "ResourceNotFoundException"

**Solution**:
```bash
# Verify table exists
aws dynamodb list-tables --region us-east-1 | grep freemium

# If not found, create it
./setup-infrastructure.sh
```

### Interaction Count Not Resetting

**Symptom**: Users still at limit after midnight

**Solution**:
- Check `last_reset_date` format is YYYY-MM-DD
- Verify timezone calculation in `FreemiumService.get_lima_date()`
- Check `pytz` is installed in Lambda layer

### Users Not Auto-Registering

**Symptom**: New users get unauthorized message

**Solution**:
- Verify `FreemiumService.check_and_register_user()` is called
- Check `whatsapp-authorized-users` table permissions
- Review Lambda logs for errors

## 📋 Deployment Checklist

- [ ] DynamoDB table `whatsapp-freemium-interactions` created
- [ ] IAM policies updated with table permissions
- [ ] Lambda environment variables configured
  - [ ] `FREEMIUM_INTERACTIONS_TABLE_NAME`
  - [ ] `FREEMIUM_DAILY_LIMIT`
- [ ] `pytz` dependency added to requirements.txt
- [ ] Lambda function redeployed with updated code
- [ ] Test freemium user flow completed
- [ ] Test daily reset verified
- [ ] Test premium upgrade verified
- [ ] Monitoring and alerts configured

## 🔗 Related Documentation

- [Main README](README.md) - General setup and usage
- [Mercado Pago Setup](MERCADOPAGO_SETUP.md) - Payment integration
- [Infrastructure Setup Script](setup-infrastructure.sh) - Automated deployment

## 💡 Best Practices

1. **Monitor Table Costs**: Use PAY_PER_REQUEST billing to avoid over-provisioning
2. **Set CloudWatch Alarms**: Alert on high interaction counts or errors
3. **Regular Backups**: Enable point-in-time recovery for the table
4. **Test in Staging**: Always test changes in a non-production environment first
5. **Log Analysis**: Regularly review logs for unusual patterns

---

**Need Help?** Check CloudWatch logs or review the design document at `.kiro/specs/freemium-tier/design.md`
