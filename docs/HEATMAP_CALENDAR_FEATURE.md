# Heatmap Calendar Feature

## Overview

The Heatmap Calendar provides a visual representation of daily transaction amounts in a calendar format, making it easy to identify patterns, busy days, and trends at a glance.

## Visual Design

### Calendar Layout
```
Semana | L    | M    | X    | J    | V    | S    | D    | Rango
-------|------|------|------|------|------|------|------|-------------
S1     | 150  | 200  | 180  | 220  | 190  | 100  | 50   | 01/11 - 07/11
S2     | 160  | 210  | 175  | 230  | 195  | 110  | 60   | 08/11 - 14/11
...
```

**Note:** The "Rango" column shows the start and end dates (DD/MM format) for each week, making it easy to identify exact date ranges.

### Color Gradient
- **Light Green** (#E8F5E9) - Low transaction amounts
- **Medium Green** - Moderate amounts
- **Dark Green** (#1B5E20) - High transaction amounts
- **Light Gray** (#F0F0F0) - No data
- **Very Light Gray** (#FAFAFA) - Zero transactions

### Text Color
- **White text** - For dark backgrounds (high amounts)
- **Black text** - For light backgrounds (low amounts)
- **Gray text** - For no data or zero

## Features

### 1. Calendar Format
- **Rows**: Weeks (S1, S2, S3, ...)
- **Columns**: Days (L, M, X, J, V, S, D) + Date Range
  - L = Lunes (Monday)
  - M = Martes (Tuesday)
  - X = Miércoles (Wednesday)
  - J = Jueves (Thursday)
  - V = Viernes (Friday)
  - S = Sábado (Saturday)
  - D = Domingo (Sunday)
  - **Rango** = Week date range (DD/MM - DD/MM)

### 2. Data Visualization
- **Daily totals**: Sum of all transactions per day
- **Color intensity**: Proportional to transaction amount
- **Empty cells**: Days outside analysis period
- **Zero values**: Days with no transactions

### 3. Legend
- **Minimum value**: Lightest green color
- **Maximum value**: Darkest green color
- **No data**: Gray color
- **Value range**: Displayed in PEN

### 4. Summary Statistics
- **Period**: Start and end dates
- **Total days**: Number of days analyzed
- **Total amount**: Sum of all daily totals

## Use Cases

### Pattern Recognition
- **Weekly patterns**: Identify which days are busiest
- **Monthly trends**: See how activity varies across weeks
- **Seasonal patterns**: Spot seasonal variations
- **Anomalies**: Quickly identify unusual days

### Business Insights
- **Peak days**: Identify best sales days
- **Slow days**: Find opportunities for promotions
- **Consistency**: Assess business stability
- **Planning**: Schedule inventory based on patterns

### Examples

#### High Weekend Sales
```
If Saturdays and Sundays are dark green:
→ Focus marketing on weekends
→ Ensure adequate weekend inventory
```

#### Weekday Patterns
```
If Mondays are light green:
→ Consider Monday promotions
→ Adjust staffing for slower days
```

#### Consistent Activity
```
If all days are similar colors:
→ Stable business
→ Predictable inventory needs
```

## Technical Implementation

### Data Aggregation
```python
# Group transactions by date
daily_totals = {}
for transaction in transactions:
    date_key = transaction.date.strftime('%Y-%m-%d')
    daily_totals[date_key] += transaction.cost
```

### Calendar Generation
```python
# Start from Monday of first week
days_to_monday = start_date.weekday()
calendar_start = start_date - timedelta(days=days_to_monday)

# Generate weeks (rows of 7 days)
for week in weeks:
    for day in range(7):  # L, M, X, J, V, S, D
        amount = daily_totals.get(date_key, 0)
```

### Color Calculation
```python
# Normalize value between 0 and 1
normalized = (value - min_val) / (max_val - min_val)

# RGB interpolation
r = r_start + (r_end - r_start) * normalized
g = g_start + (g_end - g_start) * normalized
b = b_start + (b_end - b_start) * normalized

# Light green (232, 245, 233) → Dark green (27, 94, 32)
```

### Cell Formatting
```python
# Apply color fill
cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')

# Adjust text color for readability
if value > threshold:
    cell.font = Font(color='FFFFFF', bold=True)  # White for dark bg
else:
    cell.font = Font(color='000000')  # Black for light bg
```

## Excel Formatting

### Cell Styles
- **Header row**: Green background (#4CAF50), white text, bold
- **Week labels**: Gray background (#E0E0E0), bold
- **Data cells**: Color gradient based on value
- **Date range column**: Light gray background (#F5F5F5), gray text
- **Borders**: Thin gray borders (#CCCCCC)

### Dimensions
- **Column width**: 12 units for days, 10 for week labels, 15 for date range
- **Row height**: 25 units for better visibility
- **Alignment**: Center horizontal and vertical

### Legend Section
- **Position**: Below calendar
- **Content**: Min/max values with color samples
- **Format**: Clear labels with example colors

## Benefits

### Visual Clarity
- **Instant understanding**: See patterns at a glance
- **No analysis needed**: Visual representation is intuitive
- **Color coding**: Easy to identify high/low days

### Decision Making
- **Data-driven**: Base decisions on visual patterns
- **Quick insights**: No need to read numbers
- **Trend spotting**: Easily see changes over time

### Communication
- **Shareable**: Easy to share with team
- **Professional**: Polished visual presentation
- **Universal**: Color coding is universally understood

## Example Interpretations

### Pattern 1: Strong Weekend Sales
```
Calendar shows dark green on S and D columns
→ Insight: Weekend-focused business
→ Action: Increase weekend inventory, weekend promotions
```

### Pattern 2: Mid-Week Peak
```
Calendar shows dark green on X and J columns
→ Insight: Mid-week is busiest
→ Action: Ensure mid-week staffing, inventory
```

### Pattern 3: Declining Trend
```
Calendar shows darker colors in early weeks, lighter in later weeks
→ Insight: Sales declining over period
→ Action: Investigate causes, implement recovery strategy
```

### Pattern 4: Consistent Activity
```
Calendar shows uniform colors across all days
→ Insight: Stable, predictable business
→ Action: Maintain current strategy, optimize operations
```

## Integration

### Part of Trends Analysis
- **Sheet 5** in trends Excel workbook
- **Automatic generation** with trends analysis
- **90-day default** period
- **Lima timezone** (UTC-5)

### Data Source
- **Same transactions** used for trends analysis
- **Daily aggregation** of all transaction costs
- **Filtered by** query parameters (products, dates, type)

## Future Enhancements

Potential improvements:
- **Multiple metrics**: Quantity, count, profit
- **Product-specific**: Heatmap per product
- **Comparison**: Side-by-side periods
- **Interactive**: Clickable cells with details
- **Export**: Standalone heatmap image
- **Annotations**: Mark special events/holidays

## Conclusion

The Heatmap Calendar provides powerful visual insights into daily transaction patterns, making it easy to:
- ✅ Identify busy and slow days
- ✅ Spot weekly patterns
- ✅ Detect trends and anomalies
- ✅ Make data-driven decisions
- ✅ Communicate insights visually

**Key Features:**
- Calendar format (L, M, X, J, V, S, D)
- Color gradient (light to dark green)
- 90-day view
- Legend and summary stats
- Professional formatting

---

**Last Updated:** 2025-11-11 17:30:00 (Lima, UTC-5)
