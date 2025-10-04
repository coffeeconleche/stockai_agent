#!/bin/bash

# Configuration
REGION="us-east-1"
BUCKET_NAME="whatsapp-ai-agent-images"
FUNCTION_NAME="whatsapp-ai-agent"

echo "🪣 Setting up S3 bucket for transaction images..."

# Create S3 bucket
echo "📦 Creating S3 bucket: $BUCKET_NAME"
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION

# Enable public access for images (needed for WhatsApp to display them)
echo "🔓 Configuring bucket for public read access..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
        "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Create bucket policy for public read
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/transaction-images/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json

# Create IAM policy for Lambda to access S3
echo "🔐 Creating IAM policy for S3 access..."
cat > s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME"
        }
    ]
}
EOF

# Attach policy to Lambda execution role
aws iam put-role-policy \
    --role-name lambda-execution-role \
    --policy-name S3ImageAccess \
    --policy-document file://s3-policy.json

# Update Lambda environment variables
echo "⚙️ Updating Lambda environment variables..."
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json)

# Add S3_BUCKET_NAME and RESPONSE_MODE to environment
echo "$CURRENT_ENV" | jq '. + {"S3_BUCKET_NAME": "'$BUCKET_NAME'", "RESPONSE_MODE": "text"}' > updated-env.json

aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment "Variables=$(cat updated-env.json)" \
    --region $REGION

echo "✅ S3 bucket setup complete!"
echo ""
echo "📋 Bucket details:"
echo "  Name: $BUCKET_NAME"
echo "  Region: $REGION"
echo "  Public URL: https://$BUCKET_NAME.s3.$REGION.amazonaws.com/"
echo ""
echo "🔧 To switch between text and image responses:"
echo "  Text mode: RESPONSE_MODE=text"
echo "  Image mode: RESPONSE_MODE=image"
echo ""
echo "Update with:"
echo "aws lambda update-function-configuration \\"
echo "    --function-name $FUNCTION_NAME \\"
echo "    --environment Variables='{...existing vars..., \"RESPONSE_MODE\":\"image\"}' \\"
echo "    --region $REGION"

# Clean up temporary files
rm -f bucket-policy.json s3-policy.json updated-env.json
