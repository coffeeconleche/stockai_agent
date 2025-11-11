# Excel Reports - Timezone Update

## Changes Made

### 1. Filename Format Updated

**Before:**
```
report_20251111_213309_657522.xlsx
```

**After:**
```
reporte_transacciones_20251111_1637_stockai.xlsx
```

**Format:** `reporte_transacciones_YYYYMMDD_HHMM_stockai.xlsx`

**Benefits:**
- ✅ More descriptive filename in Spanish
- ✅ Lima timezone (UTC-5) for local context
- ✅ Shorter, cleaner format (no microseconds)
- ✅ Branded with "stockai" suffix
- ✅ Easy to identify and sort by date/time

### 2. Internal Timestamps Updated

**Before:**
```
Fecha Generación: 2025-11-11 21:33:09 UTC
```

**After:**
```
Fecha Generación: 2025-11-11 16:37:00 (Lima, UTC-5)
```

**Benefits:**
- ✅ Local time for Peruvian users
- ✅ Clear timezone indication
- ✅ Matches business hours context

## Implementation Details

### Code Changes

**File:** `src/services/excel_service.py`

```python
# Import timezone support
from pytz import timezone

# Get Lima timezone
lima_tz = timezone('America/Lima')
lima_time = datetime.now(lima_tz)

# Format filename
timestamp = lima_time.strftime('%Y%m%d_%H%M')
s3_key = f"{Config.S3_IMAGES_PREFIX}reporte_transacciones_{timestamp}_stockai.xlsx"

# Format generation time in summary
generation_time = lima_time.strftime('%Y-%m-%d %H:%M:%S')
summary_data.append(['Fecha Generación', f"{generation_time} (Lima, UTC-5)"])
```

### Dependencies

No new dependencies needed - `pytz` is already in requirements.txt:
```
pytz==2024.1
```

## Examples

### Example 1: Morning Report
```
Filename: reporte_transacciones_20251111_0845_stockai.xlsx
Timestamp: 2025-11-11 08:45:00 (Lima, UTC-5)
```

### Example 2: Afternoon Report
```
Filename: reporte_transacciones_20251111_1637_stockai.xlsx
Timestamp: 2025-11-11 16:37:00 (Lima, UTC-5)
```

### Example 3: Evening Report
```
Filename: reporte_transacciones_20251111_2115_stockai.xlsx
Timestamp: 2025-11-11 21:15:00 (Lima, UTC-5)
```

## User Experience

### WhatsApp Message
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

**Note:** Sent as WhatsApp document attachment for easy download.

### Excel File - Sheet 1 (Resumen)
```
Campo                    | Valor
-------------------------|----------------------------------
Tipo de Reporte          | Ventas
Período                  | 2025-01-01 al 2025-11-11
                         |
TOTALES                  |
Costo Total              | 5030.00 PEN
Total Transacciones      | 61
Total Productos          | 15
Fecha Generación         | 2025-11-11 16:37:00 (Lima, UTC-5)
```

## Testing

### Test Script Updated

**File:** `test_excel_simple.py`

```bash
$ python3 test_excel_simple.py
🧪 Testing Excel generation...
✅ Excel file created in memory (7199 bytes)
📤 Uploading to S3: s3://whatsapp-ai-agent-images/transaction-images/reporte_transacciones_20251111_1637_stockai.xlsx
✅ Upload successful!
📊 Excel Report Generated Successfully!
```

### Verification

1. **Filename check:** ✅ Uses Lima time
2. **Internal timestamp:** ✅ Shows Lima time with UTC-5 label
3. **S3 upload:** ✅ Works correctly
4. **Download:** ✅ File opens in Excel with correct data

## Timezone Reference

### Lima, Peru (UTC-5)
- **Timezone:** America/Lima
- **UTC Offset:** -5 hours (no DST)
- **Example:** When UTC is 21:37, Lima is 16:37

### Why UTC-5?
- Peru uses UTC-5 year-round (no daylight saving time)
- Matches local business hours
- Easier for users to understand report timing
- Consistent with Config.LIMA_TIMEZONE setting

## Documentation Updated

All documentation files updated to reflect timezone changes:

1. ✅ `docs/EXCEL_REPORTS_FEATURE.md`
2. ✅ `docs/EXCEL_FEATURE_SUMMARY.md`
3. ✅ `docs/EXCEL_QUICK_START.md`
4. ✅ `docs/EXCEL_TIMEZONE_UPDATE.md` (this file)

## File Organization

All Excel-related documentation now in `docs/` folder:

```
docs/
├── EXCEL_REPORTS_FEATURE.md      # Complete feature documentation
├── EXCEL_DEPLOYMENT_GUIDE.md     # Deployment instructions
├── EXCEL_FEATURE_SUMMARY.md      # Implementation summary
├── EXCEL_QUICK_START.md          # Quick reference
└── EXCEL_TIMEZONE_UPDATE.md      # This timezone update doc
```

## Deployment Notes

No additional deployment steps needed:
- ✅ `pytz` already in requirements.txt
- ✅ No new environment variables
- ✅ No Lambda configuration changes
- ✅ Just deploy updated code

## Benefits Summary

### For Users
- 📅 Filenames show local time (easier to identify)
- 🕐 Report timestamps match their timezone
- 📝 Clear timezone indication (no confusion)
- 🇵🇪 Localized for Peruvian context

### For System
- 🔍 Better file organization (sortable by local time)
- 📊 Consistent timezone across all reports
- 🏷️ Branded filenames with "stockai"
- 📁 Cleaner, more professional naming

## Backward Compatibility

✅ **Fully backward compatible**
- Old reports still accessible
- No breaking changes
- Only affects new reports
- Existing functionality unchanged

## Next Steps

1. ✅ Code updated with Lima timezone
2. ✅ Test script verified
3. ✅ Documentation updated
4. ⏳ Ready for deployment
5. ⏳ Monitor first reports in production

---

**Last Updated:** 2025-11-11 16:37:00 (Lima, UTC-5)
