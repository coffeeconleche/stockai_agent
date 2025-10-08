# Image Types Comparison

## Visual Differentiation Between Transaction and Report Tables

### 🔵 Transaction Tables (Blue Theme)

**Purpose:** Confirm transaction registrations

**When Used:**
- User registers a transaction via text, voice, or image
- System shows what was understood before final confirmation
- User can confirm or edit

**Visual Characteristics:**
- **Header Color:** Blue (#2980B9)
- **Title:** "✅ Transacciones Registradas"
- **Alt Row Color:** Light Gray (#ECF0F1)

**Columns:**
| Column | Width | Content |
|--------|-------|---------|
| Tipo | 140px | Venta/Compra |
| Producto | 220px | Product name + variation |
| Cantidad | 140px | Quantity + units |
| Costo | 140px | Total cost + currency |
| Perecedero | 140px | Sí/No |

**Footer:**
```
📊 Total: X transacciones
```

**Example Use Case:**
```
User: "Vendí 3 mesas a 600 soles, 1 kg de maní a 50 soles"
System: [Blue table showing 2 transactions]
        [Confirm/Edit buttons]
```

---

### 🟢 Report Tables (Green Theme)

**Purpose:** Display query/report results

**When Used:**
- User requests a report or summary
- System aggregates data by product
- Shows totals and statistics

**Visual Characteristics:**
- **Header Color:** Green (#27AE60)
- **Title:** "📊 Reporte de Ventas/Compras/Transacciones"
- **Alt Row Color:** Light Green (#E8F6EC)
- **Date Range:** Shown below title if specified

**Columns:**
| Column | Width | Content |
|--------|-------|---------|
| Producto | 280px | Product name (aggregated) |
| Cantidad | 200px | Total quantity + units |
| Costo Total | 200px | Sum of all costs |
| # Trans | 160px | Number of transactions |

**Footer:**
```
💰 Total: XXX.XX PEN  |  📝 X transacciones
```

**Example Use Case:**
```
User: "Dame el reporte de ventas de octubre"
System: [Green table showing aggregated products]
        [No buttons - just information]
```

---

## Side-by-Side Comparison

| Feature | Transaction Table (Blue) | Report Table (Green) |
|---------|-------------------------|---------------------|
| **Color Theme** | Blue (#2980B9) | Green (#27AE60) |
| **Purpose** | Confirm registrations | Display summaries |
| **Data Type** | Individual transactions | Aggregated by product |
| **Interaction** | Confirm/Edit buttons | Information only |
| **Trigger** | Registration (text/voice/image) | Query request |
| **Threshold** | `TRANSACTION_THRESHOLD` (4) | `QUERY_THRESHOLD` (3) |
| **Columns** | 5 (Tipo, Producto, Cantidad, Costo, Perecedero) | 4 (Producto, Cantidad, Costo Total, # Trans) |
| **Shows Variation** | Yes (in Producto column) | No (aggregated) |
| **Shows Type** | Yes (Venta/Compra) | In title only |
| **Shows Perishable** | Yes | No |
| **Shows Trans Count** | No | Yes |
| **Date Range** | No | Yes (if specified) |

---

## User Experience Benefits

### Visual Recognition

Users can instantly identify:
- **Blue = "I just registered something"** → Needs confirmation
- **Green = "Here's my report"** → Information to review

### Chat History

When scrolling through WhatsApp chat:
- Blue images = Past registrations
- Green images = Past reports
- Easy to find specific information

### Professional Appearance

Both themes:
- Clean, organized layout
- Mobile-optimized (3:4 ratio)
- High-quality rendering
- Professional fonts (DejaVu Sans)

---

## Configuration

### Transaction Tables
```bash
# .env
RESPONSE_MODE=auto
TRANSACTION_THRESHOLD=4
```

**Behavior:**
- `RESPONSE_MODE=text` → Always text
- `RESPONSE_MODE=image` → Always image
- `RESPONSE_MODE=auto` → Image if > 4 transactions

### Report Tables
```bash
# .env
QUERY_THRESHOLD=3
```

**Behavior:**
- Always uses threshold
- Image if >= 3 products
- Text if < 3 products

---

## Technical Details

### Color Definitions

```python
# Transaction Tables (Blue Theme)
header_color = (41, 128, 185)      # #2980B9
alt_row_color = (236, 240, 241)    # #ECF0F1

# Report Tables (Green Theme)
report_header_color = (39, 174, 96)    # #27AE60
report_alt_row_color = (232, 246, 236) # #E8F6EC

# Common Colors
text_color = (44, 62, 80)          # #2C3E50
border_color = (189, 195, 199)     # #BDC3C7
bg_color = (255, 255, 255)         # #FFFFFF
```

### File Naming

```python
# Transaction images
s3_key = f"transaction-images/{timestamp}.png"

# Report images
s3_key = f"transaction-images/report_{timestamp}.png"
```

### Methods

```python
# Generate transaction table
image_service.generate_transaction_image(transactions)

# Generate report table
image_service.generate_report_image(summary, query_params)
```

---

## Examples

### Example 1: Transaction Registration

**Input:**
```
"Vendí 3 mesas a 600 soles cada una, 1 kg de maní a 50 soles, 
4 libros a 500 soles, 3 cocinas a 2700 soles"
```

**Output:**
- **Blue table** with 4 rows
- Shows individual transactions
- Confirm/Edit buttons below

### Example 2: Simple Report (Text)

**Input:**
```
"Cuánto vendí de maní?"
```

**Output:**
- **Text message** (only 1 product)
```
📊 Reporte de Ventas

Resumen por Producto:

• Maní
  Cantidad: 1 kg
  Costo total: 50.00
  Transacciones: 1

Total General:
💰 Costo total: 50.00
📝 Total transacciones: 1
```

### Example 3: Complex Report (Image)

**Input:**
```
"Dame el reporte de ventas de maní, azúcar y café del mes de octubre"
```

**Output:**
- **Green table** with 3 rows
- Shows aggregated data per product
- Date range in header: "📅 2024-10-01 al 2024-10-31"
- Footer with totals

---

## Best Practices

### For Users

1. **Look for color** to identify image type
2. **Blue = Confirm** your registration
3. **Green = Review** your report
4. **Save images** for your records
5. **Share reports** with partners/accountants

### For Developers

1. **Use correct method** for each image type
2. **Test both themes** after changes
3. **Verify S3 uploads** work correctly
4. **Check mobile rendering** (3:4 ratio)
5. **Monitor CloudWatch** for errors

---

## Summary

| Aspect | Transaction (Blue) | Report (Green) |
|--------|-------------------|----------------|
| **Icon** | ✅ | 📊 |
| **Action** | Confirm/Edit | Review |
| **Data** | Individual | Aggregated |
| **Buttons** | Yes | No |
| **Purpose** | Verification | Analysis |
| **Frequency** | Every registration | On request |

Both image types work together to provide a complete, professional business management experience through WhatsApp!
