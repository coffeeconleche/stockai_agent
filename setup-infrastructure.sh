#!/bin/bash

# Configuration
REGION="us-east-1"
USERS_TABLE="whatsapp-users"
TRANSACTIONS_TABLE="whatsapp-transactions"
FUNCTION_NAME="whatsapp-ai-agent"

echo "🚀 Setting up infrastructure..."

# Create Users DynamoDB table
echo "📊 Creating DynamoDB table: $USERS_TABLE"
aws dynamodb create-table \
    --table-name $USERS_TABLE \
    --attribute-definitions \
        AttributeName=phone_number,AttributeType=S \
    --key-schema \
        AttributeName=phone_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION

# Create Transactions DynamoDB table
# echo "📊 Creating DynamoDB table: $TRANSACTIONS_TABLE"
# aws dynamodb create-table \
#     --table-name $TRANSACTIONS_TABLE \
#     --attribute-definitions \
#         AttributeName=transaction_id,AttributeType=S \
#         AttributeName=phone_number,AttributeType=S \
#         AttributeName=date_registry,AttributeType=S \
#     --key-schema \
#         AttributeName=transaction_id,KeyType=HASH \
#     --global-secondary-indexes \
#         IndexName=phone_number-date_registry-index,KeySchema=[{AttributeName=phone_number,KeyType=HASH},{AttributeName=date_registry,KeyType=RANGE}],Projection={ProjectionType=ALL},BillingMode=PAY_PER_REQUEST \
#     --billing-mode PAY_PER_REQUEST \
#     --region $REGION

# Wait for tables to be active
echo "⏳ Waiting for tables to be active..."
aws dynamodb wait table-exists --table-name $USERS_TABLE --region $REGION
#aws dynamodb wait table-exists --table-name $TRANSACTIONS_TABLE --region $REGION

# Create IAM policy for DynamoDB access
echo "🔐 Creating IAM policy for DynamoDB access..."
cat > dynamodb-policy.json << EOF
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
                "arn:aws:dynamodb:$REGION:*:table/$USERS_TABLE",
                "arn:aws:dynamodb:$REGION:*:table/$TRANSACTIONS_TABLE",
                "arn:aws:dynamodb:$REGION:*:table/$TRANSACTIONS_TABLE/index/*"
            ]
        }
    ]
}
EOF

# Attach policy to Lambda execution role
aws iam put-role-policy \
    --role-name lambda-execution-role \
    --policy-name DynamoDBAccess \
    --policy-document file://dynamodb-policy.json

# Update Lambda environment variables
echo "⚙️ Updating Lambda environment variables..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables='{
        "VERIFY_TOKEN":"stockai_agent_2025",
        "USERS_TABLE_NAME":"'$USERS_TABLE'",
        "TRANSACTIONS_TABLE_NAME":"'$TRANSACTIONS_TABLE'",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_ACCESS_TOKEN_HERE",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_NUMBER_ID_HERE",
        "OPENAI_API_KEY":"YOUR_OPENAI_API_KEY_HERE"
    }' \
    --region $REGION

echo "✅ Infrastructure setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the WHATSAPP_ACCESS_TOKEN in Lambda environment variables"
echo "2. Update the WHATSAPP_PHONE_NUMBER_ID in Lambda environment variables"
echo "3. Update the OPENAI_API_KEY in Lambda environment variables"
echo "4. Deploy the updated Lambda function with: ./deploy.sh"
echo ""
echo "🔧 To update environment variables:"
echo "aws lambda update-function-configuration \\"
echo "    --function-name $FUNCTION_NAME \\"
echo "    --environment Variables='{"
echo "        \"VERIFY_TOKEN\":\"stockai_agent_2025\","
echo "        \"USERS_TABLE_NAME\":\"$USERS_TABLE\","
echo "        \"TRANSACTIONS_TABLE_NAME\":\"$TRANSACTIONS_TABLE\","
echo "        \"WHATSAPP_ACCESS_TOKEN\":\"your_actual_token\","
echo "        \"WHATSAPP_PHONE_NUMBER_ID\":\"your_actual_phone_id\","
echo "        \"OPENAI_API_KEY\":\"your_openai_key\""
echo "    }' \\"
echo "    --region $REGION"

# Clean up temporary files
rm -f dynamodb-policy.json