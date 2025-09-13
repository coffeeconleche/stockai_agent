#!/bin/bash

set -euo pipefail
#export AWS_PAGER=""

# Config
FUNCTION_NAME="whatsapp-ai-agent"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --no-cli-pager)
REPOSITORY_NAME="whatsapp-ai-agent"
IMAGE_TAG="latest"
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG"

echo "🚀 Starting deployment process..."

# Create ECR repo if needed
echo "📦 Creating ECR repository..."
aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region "$REGION" --no-cli-pager >/dev/null 2>&1 || echo "Repository already exists"

# ECR login
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region "$REGION" --no-cli-pager | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Ensure buildx is available
docker buildx create --use >/dev/null 2>&1 || true

# Build SINGLE-ARCH image for Lambda x86_64 and load into classic docker image store
echo "🏗️  Building Docker image (linux/amd64 single-arch)..."
docker buildx build --platform linux/amd64 -t "$REPOSITORY_NAME:$IMAGE_TAG" --load .

# Tag & push
echo "🏷️  Tagging image..."
docker tag "$REPOSITORY_NAME:$IMAGE_TAG" "$ECR_URI"

echo "⬆️  Pushing image to ECR..."
docker push "$ECR_URI"

# Create or update Lambda function
echo "⚡ Creating/updating Lambda function..."
if aws lambda get-function --function-name "$FUNCTION_NAME" --region "$REGION" --no-cli-pager >/dev/null 2>&1; then
  echo "Function exists, updating..."
  aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --image-uri "$ECR_URI" \
    --region "$REGION" \
    --no-cli-pager >/dev/null
else
  echo "Creating new function..."
  aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --package-type Image \
    --code ImageUri="$ECR_URI" \
    --role "arn:aws:iam::$ACCOUNT_ID:role/lambda-execution-role" \
    --timeout 30 \
    --memory-size 512 \
    --architectures x86_64 \
    --region "$REGION" \
    --no-cli-pager >/dev/null
fi

echo "✅ Deployment complete!"
echo "📋 Function ARN: arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$FUNCTION_NAME"