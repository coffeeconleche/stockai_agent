# Query Report Image Feature

## 🎯 Overview

The query service now automatically generates visual report tables as images when the number of products in a report exceeds a configurable threshold. This provides a better user experience for complex reports while keeping simple reports as text.

## ✨ Features

### Visual Differentiation

**Transaction Tables (Blue Theme)**
- Used for: Transaction registration confirmations
- Header Color: Blue (#2980B9)
- Alt Row Color: Light Gray (#ECF0F1)
- Columns: Tipo, Producto, Cantidad, Costo, Perecedero

**Report Tables (Green Theme)**
- Used for: Query/report responses
- Header Color: Green (#27AE60)
- Alt Row Color: Light Green (#E8F6EC)
- Columns: Producto, Cantidad, Costo Total, # Trans

### Automatic Mode Selection

The system automatically decides whether to send a report as:
- **Text** - For reports with fewer than `QUERY_THRESHOLD` products (default: 3)
- **Image** - For reports with `QUERY_THRESHOLD` or more products

## 🔧 Configuration

### Environment Variable

Add to `.env` file:
```bash
QUERY_THRESHOLD=3
```

### Lambda Environment Variable

Update Lambda configuration:
```bash
aws lambda update-function-configuration \
    --function-name whatsapp-ai-agent \
    --environment Variables='{
        ...existing variables...,
        "QUERY_THRESHOLD":"3"
    }' \
    --region us-east-1
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `QUERY_THRESHOLD` | `3` | Minimum number of products to trigger image generation |

**Examples:**
- `QUERY_THRESHOLD=3` - Reports with 3+ products sent as image
- `QUERY_THRESHOLD=5` - Reports with 5+ products sent as image
- `QUERY_THRESHOLD=1` - All reports sent as image

## 📊 Report Table Layout

### Columns

1. **Producto** (280px)
   - Product name in title case
   - Wraps if too long

2. **Cantidad** (200px)
   - Total quantity aggregated
   - Includes units (kg, pieza, litro, etc.)

3. **Costo Total** (200px)
   - Total cost for all transactions of this product
   - Format: `XX.XX PEN`

4. **# Trans** (160px)
   - Number of transactions for this product
   - Helps identify frequently traded items

### Footer

Displays overall totals:
```
💰 Total: XXX.XX PEN  |  📝 X transacciones
```

### Header Information

- **Title**: Report type (Ventas/Compras/Transacciones)
- **Date Range**: If specified in query
- **Color**: Green theme for easy identification

## 🎨 Visual Design

### Color Scheme

```python
# Green Theme (Reports)
header_color = (39, 174, 96)      # #27AE60 - Green
alt_row_color = (232, 246, 236)   # #E8F6EC - Light Green
text_color = (44, 62, 80)         # #2C3E50 - Dark Gray
border_color = (189, 195, 199)    # #BDC3C7 - Light Gray
bg_color = (255, 255, 255)        # #FFFFFF - White
```

### Dimensions

- **Width**: 900px
- **Height**: 1200px (adjusts based on content)
- **Aspect Ratio**: 3:4 (optimized for mobile)

## 📝 Usage Examples

### Example 1: Small Report (Text)

**User Query:**
```
"Dame el reporte de ventas de mani"
```

**Result:** Text message (1 product < threshold)
```
📊 Reporte de Ventas

Resumen por Producto:

• Mani
  Cantidad: 5 kg
  Costo total: 100.00
  Transacciones: 2

Total General:
💰 Costo total: 100.00
📝 Total transacciones: 2
```

### Example 2: Medium Report (Image)

**User Query:**
```
"Necesito el reporte de ventas de mani, azucar y cafe del mes de octubre"
```

**Result:** Image (3 products >= threshold)
- Green-themed table
- Shows all 3 products with aggregated data
- Includes date range in header
- Footer with totals

### Example 3: Large Report (Image)

**User Query:**
```
"Dame el reporte de todas mis ventas"
```

**Result:** Image (many products >= threshold)
- Scrollable table with all products
- Easy to save and share
- Professional appearance

## 🔄 Workflow

```mermaid
graph TD
    A[User Sends Query] --> B[Process Query]
    B --> C[Query Transactions]
    C --> D{Transactions Found?}
    D -->|No| E[Send "No Data" Message]
    D -->|Yes| F[Summarize Transactions]
    F --> G{Product Count >= QUERY_THRESHOLD?}
    G -->|No| H[Format as Text]
    G -->|Yes| I[Generate Report Image]
    I --> J{Image Generated?}
    J -->|Yes| K[Send Image with Caption]
    J -->|No| L[Fallback to Text]
    H --> M[Send Text Message]
    K --> N[End]
    L --> M
    M --> N
    E --> N
```

## 🚀 Implementation Details

### Files Modified

1. **`src/config.py`**
   - Added `QUERY_THRESHOLD` configuration

2. **`src/services/image_service.py`**
   - Added `generate_report_image()` method
   - Added green color theme for reports
   - Optimized table layout for report data

3. **`src/services/query_service.py`**
   - Added `should_use_image()` method
   - Integrated threshold checking

4. **`src/services/message_service.py`**
   - Updated `_process_query_request()` to use image generation
   - Added fallback to text if image generation fails

5. **`.env`**
   - Added `QUERY_THRESHOLD=3`

### Key Methods

#### `ImageService.generate_report_image()`
```python
def generate_report_image(self, summary: Dict[str, Any], query_params: Dict[str, Any]) -> str:
    """
    Generate a report table image and upload to S3
    
    Args:
        summary: Aggregated transaction summary
        query_params: Query parameters (dates, filters, etc.)
    
    Returns:
        Presigned S3 URL or None if failed
    """
```

#### `QueryService.should_use_image()`
```python
def should_use_image(self, summary: Dict[str, Any]) -> bool:
    """
    Determine if report should be sent as image
    
    Args:
        summary: Transaction summary with products
    
    Returns:
        True if product count >= QUERY_THRESHOLD
    """
```

## 📊 Benefits

### For Users

1. **Visual Clarity** - Tables easier to read than text for multiple products
2. **Easy Sharing** - Can save and share report images
3. **Professional Look** - Clean, organized presentation
4. **Quick Scanning** - Easier to spot trends and patterns
5. **Color Coding** - Green = Reports, Blue = Transactions

### For System

1. **Scalability** - Handles large reports better
2. **Consistency** - Standardized report format
3. **Storage** - Images stored in S3 with 24-hour expiry
4. **Fallback** - Automatic text fallback if image fails

## 🧪 Testing

### Test Case 1: Small Report (Text)
```
Query: "Cuanto vendi de mani?"
Expected: Text message (1 product)
```

### Test Case 2: Threshold Report (Image)
```
Query: "Dame el reporte de ventas de mani, azucar y cafe"
Expected: Green table image (3 products)
```

### Test Case 3: Large Report (Image)
```
Query: "Necesito el reporte de todas mis ventas"
Expected: Green table image (many products)
```

### Test Case 4: Date Range Report (Image)
```
Query: "Reporte de ventas del mes de octubre"
Expected: Green table with date range in header
```

### Test Case 5: Fallback to Text
```
Scenario: S3 upload fails
Expected: Text report sent instead
```

## 🔍 Verification

After deployment:

1. **Test small report:**
   ```
   "Cuanto vendi de mani?"
   ```
   Should receive text message

2. **Test medium report:**
   ```
   "Dame el reporte de ventas de mani, azucar y cafe"
   ```
   Should receive green table image

3. **Check S3 bucket:**
   ```bash
   aws s3 ls s3://whatsapp-ai-agent-images/transaction-images/ --recursive
   ```
   Should see `report_*.png` files

4. **Verify color difference:**
   - Transaction tables = Blue header
   - Report tables = Green header

## 📋 Troubleshooting

### Image Not Generated

**Symptoms:** Always receiving text reports

**Solutions:**
1. Check `QUERY_THRESHOLD` is set correctly
2. Verify product count >= threshold
3. Check CloudWatch logs for errors
4. Verify S3 bucket permissions

### Wrong Color Theme

**Symptoms:** Reports showing blue instead of green

**Solutions:**
1. Verify using `generate_report_image()` not `generate_transaction_image()`
2. Check `message_service.py` calls correct method
3. Redeploy Lambda function

### Image Upload Fails

**Symptoms:** Fallback to text every time

**Solutions:**
1. Check S3 bucket exists
2. Verify Lambda IAM role has S3 permissions
3. Check S3 bucket region matches Lambda region
4. Review CloudWatch logs for S3 errors

## 🎯 Future Enhancements

Potential improvements:

1. **Charts** - Add pie charts or bar graphs
2. **Trends** - Show growth/decline indicators
3. **Comparisons** - Compare periods side-by-side
4. **Export** - PDF or Excel export options
5. **Customization** - User-selectable themes
6. **Caching** - Cache frequently requested reports

## ✨ Summary

The query report image feature provides:
- ✅ Automatic image generation for complex reports
- ✅ Green color theme for easy identification
- ✅ Professional table layout
- ✅ Configurable threshold
- ✅ Automatic fallback to text
- ✅ Mobile-optimized design
- ✅ S3 storage with presigned URLs

Users can now easily view, save, and share their business reports with a professional, visually appealing format!
