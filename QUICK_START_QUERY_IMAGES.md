# Quick Start: Query Report Images

## 🚀 Get Started in 3 Steps

### Step 1: Configure Threshold

Add to `.env`:
```bash
QUERY_THRESHOLD=3
```

### Step 2: Deploy

```bash
./deploy.sh
```

### Step 3: Test

Send a query with 3+ products:
```
"Dame el reporte de ventas de mani, azucar y cafe"
```

You should receive a **green table image**! 🟢

---

## 📊 How It Works

### Automatic Selection

```
Products < 3  →  Text Message
Products >= 3  →  Green Image
```

### Visual Identification

| Type | Color | Purpose |
|------|-------|---------|
| Transaction | 🔵 Blue | Confirm registrations |
| Report | 🟢 Green | View summaries |

---

## 💡 Quick Examples

### Example 1: Text (Small Report)

**Input:**
```
"Cuánto vendí de maní?"
```

**Output:** Text message
```
📊 Reporte de Ventas

• Maní
  Cantidad: 5 kg
  Costo total: 100.00
  Transacciones: 2
```

### Example 2: Image (Large Report)

**Input:**
```
"Reporte de ventas de maní, azúcar y café"
```

**Output:** Green table image with 3 rows

---

## ⚙️ Adjust Threshold

Want more or fewer images?

```bash
# More text, fewer images
QUERY_THRESHOLD=5

# Balanced (default)
QUERY_THRESHOLD=3

# More images, less text
QUERY_THRESHOLD=1
```

---

## 🔍 Verify It's Working

### Check Lambda Config

```bash
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --query 'Environment.Variables.QUERY_THRESHOLD'
```

Should return: `"3"`

### Check S3 Images

```bash
aws s3 ls s3://whatsapp-ai-agent-images/transaction-images/ | grep report_
```

Should see: `report_YYYYMMDD_*.png` files

### Check Logs

```bash
aws logs tail /aws/lambda/whatsapp-ai-agent --follow
```

Look for: `"Generated report image (presigned)"`

---

## 🎨 Color Reference

### Blue (Transactions)
- **Hex:** #2980B9
- **RGB:** (41, 128, 185)
- **Use:** Transaction confirmations

### Green (Reports)
- **Hex:** #27AE60
- **RGB:** (39, 174, 96)
- **Use:** Query reports

---

## 📱 Mobile Optimization

All images are:
- **Ratio:** 3:4 (perfect for mobile)
- **Width:** 900px
- **Format:** PNG
- **Quality:** High (95%)

---

## 🆘 Troubleshooting

### Not Getting Images?

1. Check threshold: `QUERY_THRESHOLD=3`
2. Query must have 3+ products
3. Check CloudWatch logs for errors

### Wrong Color?

1. Verify deployment: `./deploy.sh`
2. Check you're querying (not registering)
3. Clear Lambda cache (redeploy)

### Image Upload Fails?

1. Check S3 bucket exists
2. Verify Lambda has S3 permissions
3. Check bucket region matches Lambda

---

## ✅ Success Checklist

- [ ] `QUERY_THRESHOLD` added to `.env`
- [ ] Code deployed with `./deploy.sh`
- [ ] Lambda environment variable set
- [ ] Test query sent (3+ products)
- [ ] Green image received
- [ ] S3 bucket has `report_*.png` files
- [ ] CloudWatch shows success logs

---

## 🎯 Next Steps

1. **Test different thresholds** to find your preference
2. **Share reports** with team members
3. **Save images** for record keeping
4. **Monitor usage** in CloudWatch
5. **Adjust threshold** based on user feedback

---

## 📚 Full Documentation

For complete details, see:
- `QUERY_REPORT_IMAGE_FEATURE.md` - Full feature docs
- `IMAGE_TYPES_COMPARISON.md` - Blue vs Green comparison
- `QUERY_IMAGE_IMPLEMENTATION_SUMMARY.md` - Implementation details

---

## 🎉 You're All Set!

Your query reports will now automatically generate beautiful green table images when needed, while keeping simple reports as text. Enjoy! 🚀
