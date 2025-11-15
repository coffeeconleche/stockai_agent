# Trends Analysis Feature

## Overview

The Trends Analysis feature provides comprehensive time-series analysis of transaction data, helping users understand patterns, growth rates, and make data-driven decisions.

## How It Works

### Activation
Users can request trends analysis by using keywords like:
- "tendencias"
- "trends"
- "análisis de tendencias"
- "cómo van mis ventas"
- "evolución de compras"

### Default Behavior
- **Automatic 90-day period**: If no dates specified, analyzes last 90 days
- **Minimum data requirement**: At least 5 transactions needed
- **Weekly aggregation**: Data grouped by week for trend calculation

## Analysis Components

### 1. Time-Series Analysis
- **Weekly aggregation** of transactions
- **Growth rate calculation** (week-over-week)
- **Trend direction** identification (increasing, decreasing, stable)

### 2. Statistical Metrics
- **Average weekly cost/quantity**
- **Volatility** (standard deviation)
- **Recent vs historical comparison** (last 4 weeks vs earlier)
- **Total cost and quantity** over period

### 3. Trend Classification
- **INCREASING**: Positive growth trend (slope > 0.1)
- **DECREASING**: Negative growth trend (slope < -0.1)
- **STABLE**: Minimal change (slope between -0.1 and 0.1)

### 4. Top Performers
- **Top 5 growing products** by growth rate
- **Top 5 declining products** by negative growth rate

### 5. AI-Generated Insights
- Overall trend assessment
- Best/worst performers
- Volatility warnings
- Actionable recommendations

## Excel Report Structure

The trends analysis generates a comprehensive 6-sheet Excel workbook:

### Sheet 1: Resumen Ejecutivo (Executive Summary)
- Analysis type and period
- Group information (if applicable)
- Total products analyzed
- Top 5 growing products
- Top 5 declining products
- Generation timestamp (Lima UTC-5)

### Sheet 2: Detalle de Tendencias (Trends Details)
For each product:
- Trend direction (INCREASING/DECREASING/STABLE)
- Weeks analyzed
- Weekly growth rate (%)
- Recent change (%)
- Total cost and quantity
- Average weekly metrics
- Volatility
- First and last week comparison

### Sheet 3: Serie Temporal Semanal (Weekly Time Series)
- Week-by-week cost data for all products
- Ready for chart creation
- Pivot table friendly format

### Sheet 4: Top Performers
- Side-by-side comparison
- Top 5 growing products
- Top 5 declining products
- Growth rates and total costs

### Sheet 5: Mapa de Calor (Heatmap Calendar)
- **Visual calendar heatmap** showing daily transaction amounts
- **Calendar format**: Rows of 7 days (L, M, X, J, V, S, D)
- **Color gradient**: Light green (low) to dark green (high)
- **90-day view**: Complete period visualization
- **Legend**: Min/max values and color scale
- **Summary stats**: Total days, total amount
- **Easy pattern recognition**: Identify busy days, slow days, weekly patterns

### Sheet 6: Insights
- AI-generated insights
- Interpretation guide
- General recommendations
- How to use the analysis

## Usage Examples

### Example 1: General Trends
```
User: "Muéstrame las tendencias de mis ventas"

System:
- Queries last 90 days of sales
- Analyzes all products
- Generates Excel with trends
- Sends document + insights summary
```

### Example 2: Specific Product Trends
```
User: "Análisis de tendencias de maní y azúcar"

System:
- Queries last 90 days
- Filters for maní and azúcar only
- Analyzes trends for these products
- Generates focused Excel report
```

### Example 3: Custom Period
```
User: "Tendencias de compras de enero a marzo 2025"

System:
- Uses specified date range
- Analyzes purchase transactions
- Generates trends for that period
```

## Technical Implementation

### AI Prompt Updates
```python
# New parameter in query processing
is_trend_analysis: true/false

# Automatic 90-day range for trends without dates
if is_trend_analysis and not date_from:
    date_from = current_date - 90 days
    date_to = current_date
```

### Services

#### TrendsService
**File:** `src/services/trends_service.py`

**Key Methods:**
- `analyze_trends()` - Main analysis orchestrator
- `_aggregate_by_week()` - Weekly data aggregation
- `_calculate_product_trend()` - Per-product metrics
- `_calculate_growth_rate()` - Growth rate calculation
- `_determine_trend_direction()` - Linear regression slope
- `_generate_insights()` - AI insights generation

#### ExcelService (Extended)
**File:** `src/services/excel_service.py`

**New Methods:**
- `generate_trends_excel()` - Main trends Excel generator
- `_create_trends_summary_sheet()` - Executive summary
- `_create_trends_details_sheet()` - Detailed metrics
- `_create_weekly_timeseries_sheet()` - Time series data
- `_create_top_performers_sheet()` - Top/bottom performers
- `_create_insights_sheet()` - Insights and recommendations

#### MessageService (Extended)
**File:** `src/services/message_service.py`

**New Method:**
- `_process_trends_analysis()` - Trends request handler

### Data Flow

```
User Request
    ↓
AI detects "tendencias" keyword
    ↓
Set is_trend_analysis = true
    ↓
Auto-set 90-day range (if no dates)
    ↓
Query transactions
    ↓
Check minimum data (5+ transactions)
    ↓
TrendsService.analyze_trends()
    ↓
Weekly aggregation
    ↓
Calculate metrics per product
    ↓
Generate insights
    ↓
ExcelService.generate_trends_excel()
    ↓
Create 5-sheet workbook
    ↓
Upload to S3
    ↓
Send document attachment
    ↓
Send insights summary
```

## Statistical Methods

### Growth Rate Calculation
```python
growth_rate = ((current_value - previous_value) / previous_value) * 100
average_growth = mean(all_growth_rates)
```

### Trend Direction (Linear Regression)
```python
slope = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)

if slope > 0.1: INCREASING
elif slope < -0.1: DECREASING
else: STABLE
```

### Volatility
```python
volatility = standard_deviation(weekly_costs)
```

### Recent Change
```python
recent_avg = mean(last_4_weeks)
historical_avg = mean(earlier_weeks)
recent_change = ((recent_avg - historical_avg) / historical_avg) * 100
```

## Insights Generation

### Automatic Insights
1. **Overall trend** - Percentage of products growing/declining/stable
2. **Top performer** - Product with highest growth rate
3. **Volatility warning** - Products with high variability
4. **Recent changes** - Products with significant recent shifts
5. **Transaction-specific** - Recommendations based on sales vs purchases

### Example Insights
```
📈 Tendencia general positiva: 12 de 15 productos en crecimiento

🌟 Mejor desempeño: Maní con 15.3% de crecimiento semanal

⚠️ Alta volatilidad detectada en: Azúcar, Café, Arroz

🔔 3 producto(s) con cambios significativos en las últimas 4 semanas

💡 Considera aumentar inventario de productos en crecimiento
```

## User Experience

### Request
```
User: "Análisis de tendencias de mis ventas"
```

### Response
```
[Excel Document Attachment]
📈 Análisis de Tendencias - 15 productos
📄 analisis_tendencias_20251111_1700_stockai.xlsx

📊 **Insights Principales:**

• 📈 Tendencia general positiva: 12 de 15 productos en crecimiento
• 🌟 Mejor desempeño: Maní con 15.3% de crecimiento semanal
• ⚠️ Alta volatilidad detectada en: Azúcar, Café
• 🔔 3 producto(s) con cambios significativos en las últimas 4 semanas
• 💡 Considera aumentar inventario de productos en crecimiento

📋 El archivo Excel incluye:
• Resumen ejecutivo
• Tendencias por producto
• Serie temporal semanal
• Top performers
• Mapa de calor (calendario visual)
• Insights y recomendaciones
```

## Minimum Requirements

### Data Requirements
- **Minimum transactions**: 5
- **Recommended period**: 30-90 days
- **Optimal period**: 90 days (default)

### Why 90 Days?
- Sufficient data for trend detection
- Captures seasonal patterns
- Reduces noise from outliers
- Provides meaningful growth rates
- Balances recency with historical context

## Error Handling

### No Data
```
No se encontraron transacciones para análisis de tendencias. 🔍

💡 El análisis de tendencias requiere datos históricos de al menos 2 semanas.
```

### Insufficient Data
```
⚠️ Datos insuficientes para análisis de tendencias.

Se encontraron 3 transacciones, pero se necesitan al menos 5 para un análisis significativo.

💡 Intenta con un período más amplio o sin filtros de productos.
```

### Generation Error
```
No se pudo generar el archivo de análisis. Por favor, intenta de nuevo.
```

## Benefits

### For Users
- **Understand patterns** - See which products are growing/declining
- **Make decisions** - Data-driven inventory and pricing decisions
- **Identify opportunities** - Spot high-growth products early
- **Manage risk** - Detect declining products before losses
- **Plan ahead** - Use trends for forecasting

### For Business
- **Inventory optimization** - Stock based on trends
- **Pricing strategy** - Adjust prices for growing products
- **Product lifecycle** - Identify products to promote or discontinue
- **Supplier management** - Negotiate based on purchase trends
- **Revenue forecasting** - Project future sales

## Configuration

### Environment Variables
```bash
# No new variables needed
# Uses existing EXCEL_THRESHOLD and S3 configuration
```

### Thresholds
```python
MINIMUM_TRANSACTIONS = 5  # Hardcoded in trends_service.py
DEFAULT_PERIOD_DAYS = 90  # Hardcoded in openai_service.py
```

## Testing

### Test Trends Analysis
```
User: "Tendencias de ventas"
```

Expected:
1. AI detects trend request
2. Sets 90-day date range
3. Queries transactions
4. Generates trends analysis
5. Creates 5-sheet Excel
6. Sends document attachment
7. Sends insights summary

### Test with Specific Products
```
User: "Análisis de tendencias de maní y azúcar"
```

Expected:
1. Filters for maní and azúcar
2. Analyzes only those products
3. Generates focused report

### Test with Custom Dates
```
User: "Tendencias de enero a marzo"
```

Expected:
1. Uses specified date range
2. Analyzes that period
3. Generates report

## Deployment

### No Additional Configuration
- ✅ Uses existing Excel service
- ✅ Uses existing S3 integration
- ✅ No new environment variables
- ✅ No new dependencies (uses pandas/openpyxl)

### Just Deploy Code
```bash
./deploy.sh
```

## Future Enhancements

Potential improvements:
- **Forecasting** - Predict future values
- **Seasonality detection** - Identify seasonal patterns
- **Anomaly detection** - Flag unusual spikes/drops
- **Comparative analysis** - Compare periods
- **Charts in Excel** - Embedded visualizations
- **PDF reports** - Alternative format
- **Email delivery** - Send reports via email

## Conclusion

The Trends Analysis feature provides powerful insights into transaction patterns, helping users make data-driven decisions about inventory, pricing, and product management.

**Key Features:**
- ✅ Automatic 90-day analysis
- ✅ Weekly aggregation
- ✅ Growth rate calculation
- ✅ Trend direction classification
- ✅ AI-generated insights
- ✅ Comprehensive 5-sheet Excel
- ✅ Document attachment delivery

---

**Last Updated:** 2025-11-11 17:00:00 (Lima, UTC-5)
