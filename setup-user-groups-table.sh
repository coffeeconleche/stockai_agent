#!/bin/bash

# Configuration
REGION="us-east-1"
USER_GROUPS_TABLE="whatsapp-user-groups"
FUNCTION_NAME="whatsapp-ai-agent"

echo "🚀 Setting up User Groups infrastructure..."

# Create User Groups DynamoDB table
echo "📊 Creating DynamoDB table: $USER_GROUPS_TABLE"
aws dynamodb create-table \
    --table-name $USER_GROUPS_TABLE \
    --attribute-definitions \
        AttributeName=main_phone_number,AttributeType=S \
    --key-schema \
        AttributeName=main_phone_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION

# Wait for table to be active
echo "⏳ Waiting for table to be active..."
aws dynamodb wait table-exists --table-name $USER_GROUPS_TABLE --region $REGION

# Update IAM policy for DynamoDB access
echo "🔐 Updating IAM policy for DynamoDB access..."
cat > user-groups-policy.json << EOF
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
                "arn:aws:dynamodb:$REGION:*:table/$USER_GROUPS_TABLE"
            ]
        }
    ]
}
EOF

# Attach policy to Lambda execution role
aws iam put-role-policy \
    --role-name lambda-execution-role \
    --policy-name UserGroupsAccess \
    --policy-document file://user-groups-policy.json

# Update Lambda environment variables
echo "⚙️ Updating Lambda environment variables..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables='{
        "VERIFY_TOKEN":"stockai_agent_2025",
        "USERS_TABLE_NAME":"whatsapp-users",
        "TRANSACTIONS_TABLE_NAME":"whatsapp-transactions",
        "PENDING_TRANSACTIONS_TABLE_NAME":"whatsapp-pending-transactions",
        "AUTHORIZED_USERS_TABLE_NAME":"whatsapp-authorized-users",
        "FREEMIUM_INTERACTIONS_TABLE_NAME":"whatsapp-freemium-interactions",
        "USER_GROUPS_TABLE_NAME":"'$USER_GROUPS_TABLE'",
        "FREEMIUM_DAILY_LIMIT":"5",
        "MAX_GROUP_MEMBERS":"10",
        "ENABLE_USER_GROUPS":"true",
        "RESPONSE_MODE":"auto",
        "TRANSACTION_THRESHOLD":"2",
        "QUERY_THRESHOLD":"3",
        "LICENSE_PRICE":"2",
        "LICENSE_CURRENCY":"PEN",
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_MP_ACCESS_TOKEN",
        "PAYMENT_WEBHOOK_URL":"YOUR_LAMBDA_URL/payment-webhook",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_ID",
        "OPENAI_API_KEY":"YOUR_OPENAI_KEY",
        "DEEPSEEK_API_KEY":"YOUR_DEEPSEEK_KEY",
        "GEMINI_API_KEY":"YOUR_GEMINI_KEY"
    }' \
    --region $REGION

echo "✅ User Groups infrastructure setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the Lambda environment variables with your actual credentials"
echo "2. Deploy the updated Lambda function with: ./deploy.sh"
echo "3. Test the grouped query feature"
echo ""
echo "🔧 To manually update environment variables:"
echo "aws lambda update-function-configuration \\"
echo "    --function-name $FUNCTION_NAME \\"
echo "    --environment Variables='{...}' \\"
echo "    --region $REGION"

# Clean up temporary files
rm -f user-groups-policy.json

