#!/bin/bash

# Configuration
REGION="us-east-1"
FUNCTION_NAME="whatsapp-ai-agent"

# Check argument
if [ -z "$1" ]; then
    echo "Usage: $0 <text|image|auto> [threshold]"
    echo ""
    echo "Modes:"
    echo "  text  - Always use text responses"
    echo "  image - Always use image responses"
    echo "  auto  - Use text for ≤4 transactions, image for >4 (default)"
    echo ""
    echo "Current configuration:"
    echo -n "  Mode: "
    aws lambda get-function-configuration \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query 'Environment.Variables.RESPONSE_MODE' \
        --output text
    echo -n "  Threshold: "
    aws lambda get-function-configuration \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query 'Environment.Variables.TRANSACTION_THRESHOLD' \
        --output text
    exit 1
fi

MODE="$1"
THRESHOLD="${2:-4}"

if [ "$MODE" != "text" ] && [ "$MODE" != "image" ] && [ "$MODE" != "auto" ]; then
    echo "❌ Invalid mode. Use 'text', 'image', or 'auto'"
    exit 1
fi

echo "🔄 Switching response mode to: $MODE"

# Get current env (might be null if none set)
CURRENT_ENV=$(aws lambda get-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --region "$REGION" \
  --query 'Environment.Variables' \
  --output json)

# 1) Build a compact JSON of your env vars
UPDATED_ENV=$(aws lambda get-function-configuration \
  --function-name "whatsapp-ai-agent" \
  --region "us-east-1" \
  --query 'Environment.Variables' \
  --output json | jq -c \
  '. + {RESPONSE_MODE:"'$MODE'", TRANSACTION_THRESHOLD:"'$THRESHOLD'"}')

# 2) Wrap it with the "Variables" object required by the CLI
printf '{"Variables":%s}\n' "$UPDATED_ENV" > env.json

# 3) Update Lambda (JSON file avoids quoting issues)
aws lambda update-function-configuration \
  --function-name "whatsapp-ai-agent" \
  --region "us-east-1" \
  --environment file://env.json


if [ $? -eq 0 ]; then
  echo "✅ Response mode updated to: $MODE"
  if [ "$MODE" = "text" ]; then
    echo "📝 Bot will now always send text responses"
  elif [ "$MODE" = "image" ]; then
    echo "🖼️ Bot will now always send image table responses"
  else
    echo "🤖 Bot will now automatically choose:"
    echo "   • Text for ≤$THRESHOLD transactions"
    echo "   • Image for >$THRESHOLD transactions"
  fi
else
  echo "❌ Failed to update response mode"
fi


# Clean up
rm -f env.json
rm -f updated-env.json
