# Excel Reports Feature

## Overview

Added Excel file generation for large query reports with 10+ products. When users request reports with many products, they now receive a downloadable Excel file with multiple sheets for detailed analysis.

## How It Works

### Report Format Selection

The system automatically selects the best format based on the number of products:

| Products | Format | Description |
|----------|--------|-------------|
| 1-2 | Text | Simple text message with summary |
| 3-9 | Image | Green table image (existing feature) |
| 10+ | **Excel** | Multi-sheet Excel file with download link |

### Configuration

```bash
# .env
EXCEL_THRESHOLD=10  # Generate Excel if >= 10 products
```

## Excel File Structure

The generated Excel file contains 3 sheets:

### Sheet 1: "Resumen" (Summary)
- Report type (Ventas/Compras/Transacciones)
- Group information (if user has groups enabled)
- Date range filters
- Product filters (if applied)
- **Totals:**
  - Total cost (PEN)
  - Total transactions
  - Total products
  - Generation timestamp

### Sheet 2: "Detalle por Producto" (Product Details)
- Product name
- Total quantity and units
- Total cost (PEN)
- Number of transactions
- Average cost per transaction
- Average quantity per transaction
- **Sorted by total cost (descending)**
- **Professional formatting with currency columns**

### Sheet 3: "Top 10 Productos" (Top 10 Products)
- Top 10 products by cost
- Ready for chart creation
- Visualization data

## User Experience

### Example: Large Report Request

**User:** "Dame el reporte de todas mis ventas"

**System Response:**
```
[Excel Document Attachment]
📊 Reporte de 15 productos
📄 reporte_transacciones_20251111_1637_stockai.xlsx

📋 El archivo Excel incluye:
• Resumen ejecutivo
• Detalle por producto
• Top 10 productos
• Datos listos para gráficos
```

**Note:** The Excel file is sent as a WhatsApp document attachment. Users can download it directly from the chat without seeing long URLs.

## Technical Implementation

### New Files

1. **`src/services/excel_service.py`** - Excel generation service
   - `ExcelService` class
   - Multi-sheet workbook creation
   - S3 upload with presigned URLs
   - Professional formatting

### Modified Files

1. **`src/config.py`**
   - Added `EXCEL_THRESHOLD` configuration

2. **`src/services/query_service.py`**
   - Added `should_use_excel()` method
   - Updated `should_use_image()` to respect Excel threshold

3. **`src/services/message_service.py`**
   - Integrated `ExcelService`
   - Updated `_process_query_request()` with Excel logic
   - Added fallback chain: Excel → Image → Text

4. **`requirements.txt`**
   - Added `pandas==2.2.2`
   - Added `openpyxl==3.1.2`

5. **`.env`**
   - Added `EXCEL_THRESHOLD=10`

### Code Flow

```python
# Query processing logic
if product_count >= EXCEL_THRESHOLD:  # >= 10
    try:
        send_excel_file()
    except:
        try:
            send_image_table()  # Fallback
        except:
            send_text_message()  # Final fallback
            
elif product_count >= QUERY_THRESHOLD:  # 3-9
    try:
        send_image_table()
    except:
        send_text_message()  # Fallback
        
else:  # < 3
    send_text_message()
```

## Excel Features

### Professional Formatting
- ✅ Auto-adjusted column widths for readability
- ✅ Currency formatting for PEN amounts
- ✅ Sorted data (by total cost, descending)
- ✅ Multiple sheets for organized information
- ✅ Clear headers and labels

### Data Analysis Ready
- ✅ Clean, structured data for pivot tables
- ✅ Top 10 products sheet ready for charts
- ✅ Calculated averages and totals
- ✅ Export-friendly format

### S3 Integration
- ✅ Automatic upload to S3 bucket
- ✅ Presigned URLs (valid for 24 hours)
- ✅ Proper content type and disposition headers
- ✅ Secure, temporary access
- ✅ Filename format: `reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx` (Lima time, UTC-5)
- ✅ Generation timestamp in Lima timezone (UTC-5)

## Deployment

### 1. Update Lambda Environment Variables

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{"EXCEL_THRESHOLD":"10",...}' \
    --region us-east-1 \
    --profile diego_macbook_pro_kiro
```

### 2. Update Lambda Layer (if needed)

The Lambda layer needs to include pandas and openpyxl:

```bash
# Create layer with dependencies
mkdir -p python/lib/python3.11/site-packages
pip install pandas==2.2.2 openpyxl==3.1.2 -t python/lib/python3.11/site-packages
zip -r excel-layer.zip python
```

### 3. Verify S3 Permissions

Ensure Lambda execution role has permissions:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::whatsapp-ai-agent-images/*"
}
```

## Testing

### Test Script

Run the included test script:

```bash
python3 test_excel_simple.py
```

This will:
1. Generate a test Excel file with 12 products
2. Upload to S3
3. Generate a presigned URL
4. Display the download link

### Manual Testing

1. **Small report (text):**
   - "Cuánto vendí de mani?"
   - Expected: Text message

2. **Medium report (image):**
   - "Reporte de ventas de mani, azucar, cafe, arroz, papa"
   - Expected: Green table image

3. **Large report (Excel):**
   - "Dame el reporte de todas mis ventas"
   - Expected: Excel download link

## Fallback Strategy

The system has a robust fallback chain:

1. **Primary:** Excel file (for 10+ products)
2. **Fallback 1:** Image table (if Excel fails)
3. **Fallback 2:** Text message (if both fail)

This ensures users always get their report, even if Excel generation fails.

## Benefits

### For Users
- 📊 Better visualization for large datasets
- 💾 Downloadable files for offline analysis
- 📈 Ready for charts and pivot tables
- 🔍 Easier to search and filter data

### For Business
- 🎯 Professional reporting
- 📉 Reduced message clutter
- ⚡ Better performance (no huge text messages)
- 🔒 Secure, temporary file sharing

## Limitations

- Excel files are valid for 24 hours only
- Requires pandas and openpyxl in Lambda layer
- Slightly larger Lambda package size
- S3 storage costs (minimal)

## Future Enhancements

Potential improvements:
- Add charts directly in Excel
- Support for custom date ranges in sheet names
- Email delivery option
- PDF export alternative
- Configurable threshold per user
