# Excel Feature Deployment Guide

## Prerequisites

- AWS CLI configured with profile: `diego_macbook_pro_kiro`
- Lambda function: `whatsapp-ai-agent`
- S3 bucket: `whatsapp-ai-agent-images`
- Python 3.11 runtime

## Step 1: Create Lambda Layer with Excel Dependencies

### Option A: Using Docker (Recommended for Lambda compatibility)

```bash
# Create a directory for the layer
mkdir -p excel-layer/python

# Use Docker to install dependencies for Lambda environment
docker run --rm -v "$PWD/excel-layer":/var/task \
  public.ecr.aws/lambda/python:3.11 \
  pip install pandas==2.2.2 openpyxl==3.1.2 -t /var/task/python

# Create the layer zip
cd excel-layer
zip -r ../excel-layer.zip python
cd ..

# Upload to AWS Lambda
aws lambda publish-layer-version \
    --layer-name pandas-openpyxl-layer \
    --description "Pandas and openpyxl for Excel generation" \
    --zip-file fileb://excel-layer.zip \
    --compatible-runtimes python3.11 \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

### Option B: Local Installation (May have compatibility issues)

```bash
# Create layer directory
mkdir -p excel-layer/python/lib/python3.11/site-packages

# Install dependencies
pip install pandas==2.2.2 openpyxl==3.1.2 \
  -t excel-layer/python/lib/python3.11/site-packages

# Create zip
cd excel-layer
zip -r ../excel-layer.zip python
cd ..

# Upload to AWS Lambda
aws lambda publish-layer-version \
    --layer-name pandas-openpyxl-layer \
    --description "Pandas and openpyxl for Excel generation" \
    --zip-file fileb://excel-layer.zip \
    --compatible-runtimes python3.11 \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

**Note the Layer ARN from the output!**

## Step 2: Attach Layer to Lambda Function

```bash
# Replace LAYER_ARN with the ARN from Step 1
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --layers arn:aws:lambda:us-east-1:ACCOUNT_ID:layer:pandas-openpyxl-layer:1 \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

## Step 3: Update Lambda Environment Variables

```bash
# Get current environment variables
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro \
    --query 'Environment.Variables' > current-env.json

# Edit current-env.json to add EXCEL_THRESHOLD=10

# Update Lambda with new environment
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment file://current-env.json \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

Or manually add via AWS Console:
- Key: `EXCEL_THRESHOLD`
- Value: `10`

## Step 4: Deploy Updated Code

```bash
# Package the application
./deploy.sh

# Or manually:
zip -r function.zip src/ lambda_function.py
aws lambda update-function-code \
    --function-name whatsapp-ai-agent \
    --zip-file fileb://function.zip \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

## Step 5: Verify S3 Permissions

Check Lambda execution role has S3 permissions:

```bash
# Get Lambda role
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro \
    --query 'Role'
```

Ensure the role has this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::whatsapp-ai-agent-images/*"
    }
  ]
}
```

## Step 6: Test the Deployment

### Test 1: Local Test

```bash
python3 test_excel_simple.py
```

Expected output:
```
✅ Excel file created in memory
✅ Upload successful!
📊 Excel Report Generated Successfully!
📥 Download URL: https://...
```

### Test 2: Lambda Test

Create a test event in Lambda console or use AWS CLI:

```bash
# Create test event file
cat > test-event.json << 'EOF'
{
  "body": "{\"entry\":[{\"changes\":[{\"field\":\"messages\",\"value\":{\"messages\":[{\"from\":\"51999999999\",\"id\":\"test123\",\"type\":\"text\",\"text\":{\"body\":\"dame el reporte de todas mis ventas\"}}]}}]}]}"
}
EOF

# Invoke Lambda
aws lambda invoke \
    --function-name whatsapp-ai-agent \
    --payload file://test-event.json \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro \
    response.json

# Check response
cat response.json
```

### Test 3: WhatsApp Test

Send a message to your WhatsApp bot:
```
"Dame el reporte de todas mis ventas"
```

Expected response:
```
[Excel Document Attachment]
📊 Reporte de X productos
📄 reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx

📋 El archivo Excel incluye:
• Resumen ejecutivo
• Detalle por producto
• Top 10 productos
• Datos listos para gráficos
```

**Note:** Sent as document attachment, not URL.

## Troubleshooting

### Issue: "No module named 'pandas'"

**Solution:** Layer not attached or incorrect Python version
```bash
# Verify layer is attached
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro \
    --query 'Layers'
```

### Issue: "Unable to import module 'lambda_function'"

**Solution:** Check package structure
```bash
# Verify structure
unzip -l function.zip | head -20
```

Should show:
```
src/
src/services/
src/services/excel_service.py
...
```

### Issue: Excel generation fails silently

**Solution:** Check CloudWatch logs
```bash
aws logs tail /aws/lambda/whatsapp-ai-agent \
    --follow \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

### Issue: S3 upload fails

**Solution:** Verify IAM permissions
```bash
# Test S3 access
aws s3 ls s3://whatsapp-ai-agent-images/ \
    --profile diego_macbook_pro_kiro
```

### Issue: Presigned URL doesn't work

**Solution:** Check S3 bucket policy and CORS settings

## Rollback Plan

If issues occur, rollback:

```bash
# Remove layer
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --layers [] \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro

# Remove environment variable
# (Edit current-env.json to remove EXCEL_THRESHOLD)
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment file://current-env.json \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro

# Deploy previous code version
aws lambda update-function-code \
    --function-name whatsapp-ai-agent \
    --zip-file fileb://previous-function.zip \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

## Monitoring

### CloudWatch Metrics to Watch

- Lambda Duration (should not increase significantly)
- Lambda Errors (should remain low)
- S3 PutObject requests
- Lambda Memory Usage (pandas increases memory)

### CloudWatch Logs

Search for:
- `"Generated Excel report"`
- `"Error generating Excel report"`
- `"Excel generation failed"`

## Cost Considerations

### Lambda Layer
- Storage: ~50MB (pandas + openpyxl)
- Cost: Minimal (included in Lambda free tier)

### S3 Storage
- Per Excel file: ~10-50KB
- Lifecycle policy: Delete after 7 days
- Cost: < $0.01/month for typical usage

### Lambda Execution
- Increased memory usage: ~256MB → ~512MB
- Increased duration: +1-2 seconds per Excel generation
- Cost: Minimal increase

## Next Steps

1. Monitor CloudWatch logs for first week
2. Gather user feedback
3. Adjust EXCEL_THRESHOLD if needed
4. Consider adding S3 lifecycle policy to auto-delete old files

## Support

If issues persist:
1. Check CloudWatch logs
2. Verify all environment variables
3. Test with `test_excel_simple.py`
4. Review IAM permissions
