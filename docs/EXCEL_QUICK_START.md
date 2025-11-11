# Excel Reports - Quick Start Guide

## 🎯 What It Does

Automatically generates Excel files for large query reports (10+ products) instead of sending long text messages or images.

## 📊 How It Works

```
User asks: "Dame el reporte de todas mis ventas"
         ↓
System counts products in result
         ↓
    < 3 products  → Text message
    3-9 products  → Image table
    ≥ 10 products → Excel file ✨
```

## 🚀 Quick Deploy

```bash
# 1. Create Lambda layer with pandas + openpyxl
docker run --rm -v "$PWD/excel-layer":/var/task \
  public.ecr.aws/lambda/python:3.11 \
  pip install pandas==2.2.2 openpyxl==3.1.2 -t /var/task/python

cd excel-layer && zip -r ../excel-layer.zip python && cd ..

# 2. Upload layer
aws lambda publish-layer-version \
    --layer-name pandas-openpyxl-layer \
    --zip-file fileb://excel-layer.zip \
    --compatible-runtimes python3.11 \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro

# 3. Attach to Lambda (replace LAYER_ARN)
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --layers LAYER_ARN \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro

# 4. Add environment variable
# EXCEL_THRESHOLD=10

# 5. Deploy code
./deploy.sh
```

## 🧪 Quick Test

```bash
python3 test_excel_simple.py
```

Expected: Excel file uploaded to S3 with download URL.

## 📱 User Message Example

```
[Excel Document Attachment]
📊 Reporte de 15 productos
� re porte_transacciones_20251111_1637_stockai.xlsx

� Esl archivo Excel incluye:
• Resumen ejecutivo
• Detalle por producto
• Top 10 productos
• Datos listos para gráficos
```

**Note:** Sent as document attachment, not URL link.

## 📁 Excel File Contains

1. **Resumen** - Summary with totals (timestamps in Lima time, UTC-5)
2. **Detalle por Producto** - Full product details
3. **Top 10 Productos** - Top products by cost

**Filename format:** `reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx` (Lima time)

## ⚙️ Configuration

```bash
# .env
EXCEL_THRESHOLD=10  # Change threshold here
```

## 🔍 Troubleshooting

### "No module named 'pandas'"
→ Layer not attached or wrong Python version

### Excel generation fails
→ Check CloudWatch logs: `/aws/lambda/whatsapp-ai-agent`

### S3 upload fails
→ Verify Lambda role has `s3:PutObject` permission

## 📚 Full Documentation

- **Feature Details:** `docs/EXCEL_REPORTS_FEATURE.md`
- **Deployment Guide:** `docs/EXCEL_DEPLOYMENT_GUIDE.md`
- **Summary:** `docs/EXCEL_FEATURE_SUMMARY.md`

## ✅ Checklist

- [ ] Lambda layer created and attached
- [ ] Environment variable `EXCEL_THRESHOLD=10` added
- [ ] Code deployed
- [ ] S3 permissions verified
- [ ] Test script runs successfully
- [ ] WhatsApp test with 10+ products works

## 💡 Pro Tips

1. **Adjust threshold:** Change `EXCEL_THRESHOLD` to 15 if 10 is too low
2. **S3 lifecycle:** Add policy to auto-delete files after 7 days
3. **Memory:** Increase Lambda memory to 512MB for better performance
4. **Monitoring:** Watch CloudWatch logs for first week

## 🎉 That's It!

Your WhatsApp bot now generates professional Excel reports for large queries!
