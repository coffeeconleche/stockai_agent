#!/bin/bash

# Configuration
REGION="us-east-1"
FUNCTION_NAME="whatsapp-ai-agent"

# Check argument
if [ -z "$1" ]; then
    echo "Usage: $0 <text|image>"
    echo ""
    echo "Current mode:"
    aws lambda get-function-configuration \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query 'Environment.Variables.RESPONSE_MODE' \
        --output text
    exit 1
fi

MODE="$1"

if [ "$MODE" != "text" ] && [ "$MODE" != "image" ]; then
    echo "❌ Invalid mode. Use 'text' or 'image'"
    exit 1
fi

echo "🔄 Switching response mode to: $MODE"

# Get current environment variables
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json)

# Update RESPONSE_MODE
echo "$CURRENT_ENV" | jq '. + {"RESPONSE_MODE": "'$MODE'"}' > updated-env.json

aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment "Variables=$(cat updated-env.json)" \
    --region $REGION \
    > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Response mode updated to: $MODE"
    
    if [ "$MODE" == "text" ]; then
        echo "📝 Bot will now send text responses"
    else
        echo "🖼️ Bot will now send image table responses"
    fi
else
    echo "❌ Failed to update response mode"
fi

# Clean up
rm -f updated-env.json
