#!/bin/bash

# Configuration
FUNCTION_NAME="stockai-payment-webhook"
REGION="us-east-1"
ROLE_NAME="lambda-payment-webhook-role"

echo "🚀 Deploying Payment Webhook Lambda Function..."

# Create deployment package
echo "📦 Creating deployment package..."
rm -f payment-webhook.zip
pip install -r requirements.txt -t package/
cd package
zip -r ../payment-webhook.zip .
cd ..
zip -g payment-webhook.zip lambda_function.py

# Check if Lambda function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "📝 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://payment-webhook.zip \
        --region $REGION
else
    echo "🆕 Creating new Lambda function..."
    
    # Create IAM role if it doesn't exist
    if ! aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
        echo "🔐 Creating IAM role..."
        
        cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
        
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json
        
        # Attach basic execution policy
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Create and attach DynamoDB policy
        cat > dynamodb-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:$REGION:*:table/whatsapp-authorized-users"
    }
  ]
}
EOF
        
        aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name DynamoDBAccess \
            --policy-document file://dynamodb-policy.json
        
        rm -f trust-policy.json dynamodb-policy.json
        
        echo "⏳ Waiting for IAM role to be ready..."
        sleep 10
    fi
    
    # Get role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    # Create Lambda function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.12 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://payment-webhook.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
fi

# Update environment variables
echo "⚙️ Updating environment variables..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables='{
        "MERCADOPAGO_ACCESS_TOKEN":"YOUR_MP_ACCESS_TOKEN",
        "AUTHORIZED_USERS_TABLE_NAME":"whatsapp-authorized-users",
        "WHATSAPP_ACCESS_TOKEN":"YOUR_WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID":"YOUR_PHONE_ID",
        "WHATSAPP_API_VERSION":"v20.0",
        "AWS_REGION":"'$REGION'"
    }' \
    --region $REGION

# Create Function URL
echo "🔗 Creating Function URL..."
FUNCTION_URL=$(aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --region $REGION \
    --query 'FunctionUrl' \
    --output text 2>/dev/null || \
    aws lambda get-function-url-config \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'FunctionUrl' \
    --output text)

# Add permission for public access
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region $REGION 2>/dev/null || echo "Permission already exists"

echo ""
echo "✅ Payment Webhook Lambda deployed successfully!"
echo ""
echo "📋 Function Details:"
echo "  Name: $FUNCTION_NAME"
echo "  Region: $REGION"
echo "  URL: $FUNCTION_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Update environment variables with your actual credentials:"
echo "   aws lambda update-function-configuration \\"
echo "       --function-name $FUNCTION_NAME \\"
echo "       --environment Variables='{...}' \\"
echo "       --region $REGION"
echo ""
echo "2. Configure this URL in Mercado Pago webhook settings:"
echo "   $FUNCTION_URL"
echo ""
echo "3. Update main Lambda with this webhook URL:"
echo "   PAYMENT_WEBHOOK_URL=\"$FUNCTION_URL\""

# Clean up
rm -rf package
rm -f payment-webhook.zip
