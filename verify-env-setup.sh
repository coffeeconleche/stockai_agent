#!/bin/bash

# Script to verify environment variable setup for Freemium Tier

set -e

FUNCTION_NAME="whatsapp-ai-agent"
REGION="us-east-1"

echo "🔍 Verifying Freemium Tier Environment Setup..."
echo ""

# Check local .env file
echo "📄 Checking local .env file..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    if grep -q "FREEMIUM_INTERACTIONS_TABLE_NAME" .env; then
        echo "✅ FREEMIUM_INTERACTIONS_TABLE_NAME found in .env"
        grep "FREEMIUM_INTERACTIONS_TABLE_NAME" .env
    else
        echo "❌ FREEMIUM_INTERACTIONS_TABLE_NAME not found in .env"
    fi
    
    if grep -q "FREEMIUM_DAILY_LIMIT" .env; then
        echo "✅ FREEMIUM_DAILY_LIMIT found in .env"
        grep "FREEMIUM_DAILY_LIMIT" .env
    else
        echo "❌ FREEMIUM_DAILY_LIMIT not found in .env"
    fi
else
    echo "❌ .env file not found"
fi

echo ""

# Check DynamoDB table
echo "🗄️  Checking DynamoDB table..."
if aws dynamodb describe-table --table-name whatsapp-freemium-interactions --region $REGION --no-cli-pager >/dev/null 2>&1; then
    echo "✅ whatsapp-freemium-interactions table exists"
    TABLE_STATUS=$(aws dynamodb describe-table --table-name whatsapp-freemium-interactions --region $REGION --query 'Table.TableStatus' --output text --no-cli-pager)
    echo "   Status: $TABLE_STATUS"
else
    echo "❌ whatsapp-freemium-interactions table not found"
    echo "   Run ./setup-infrastructure.sh to create it"
fi

echo ""

# Check Lambda environment variables
echo "⚡ Checking Lambda environment variables..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --no-cli-pager >/dev/null 2>&1; then
    echo "✅ Lambda function exists"
    
    ENV_VARS=$(aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION --query 'Environment.Variables' --output json --no-cli-pager)
    
    if echo "$ENV_VARS" | grep -q "FREEMIUM_INTERACTIONS_TABLE_NAME"; then
        FREEMIUM_TABLE=$(echo "$ENV_VARS" | grep -o '"FREEMIUM_INTERACTIONS_TABLE_NAME":"[^"]*"')
        echo "✅ FREEMIUM_INTERACTIONS_TABLE_NAME configured"
        echo "   $FREEMIUM_TABLE"
    else
        echo "❌ FREEMIUM_INTERACTIONS_TABLE_NAME not configured"
    fi
    
    if echo "$ENV_VARS" | grep -q "FREEMIUM_DAILY_LIMIT"; then
        FREEMIUM_LIMIT=$(echo "$ENV_VARS" | grep -o '"FREEMIUM_DAILY_LIMIT":"[^"]*"')
        echo "✅ FREEMIUM_DAILY_LIMIT configured"
        echo "   $FREEMIUM_LIMIT"
    else
        echo "❌ FREEMIUM_DAILY_LIMIT not configured"
    fi
else
    echo "❌ Lambda function not found"
    echo "   Deploy the function with ./deploy.sh"
fi

echo ""

# Check config.py
echo "⚙️  Checking config.py..."
if [ -f "src/config.py" ]; then
    echo "✅ config.py exists"
    
    if grep -q "FREEMIUM_INTERACTIONS_TABLE_NAME" src/config.py; then
        echo "✅ FREEMIUM_INTERACTIONS_TABLE_NAME defined in config.py"
    else
        echo "❌ FREEMIUM_INTERACTIONS_TABLE_NAME not found in config.py"
    fi
    
    if grep -q "FREEMIUM_DAILY_LIMIT" src/config.py; then
        echo "✅ FREEMIUM_DAILY_LIMIT defined in config.py"
    else
        echo "❌ FREEMIUM_DAILY_LIMIT not found in config.py"
    fi
    
    if grep -q "LIMA_TIMEZONE" src/config.py; then
        echo "✅ LIMA_TIMEZONE defined in config.py"
    else
        echo "❌ LIMA_TIMEZONE not found in config.py"
    fi
else
    echo "❌ config.py not found"
fi

echo ""
echo "✨ Verification complete!"
echo ""
echo "📋 Next steps if any checks failed:"
echo "1. For missing .env: File has been created, update with your credentials"
echo "2. For missing DynamoDB table: Run ./setup-infrastructure.sh"
echo "3. For missing Lambda config: Run ./setup-infrastructure.sh or update manually"
echo "4. For missing config.py entries: They should already be there from previous tasks"
