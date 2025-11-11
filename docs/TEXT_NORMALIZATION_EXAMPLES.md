# Text Normalization Examples

## Common Spanish Products - Before vs After

### Food Products (Perishable)

| User Input | Before (Inconsistent) | After (Normalized) |
|------------|----------------------|-------------------|
| "Vendí maní" | `"maní"` or `"mani"` | `"mani"` ✅ |
| "Compré azúcar" | `"azúcar"` or `"azucar"` | `"azucar"` ✅ |
| "Vendí café" | `"café"` or `"cafe"` | `"cafe"` ✅ |
| "Compré limón" | `"limón"` or `"limon"` | `"limon"` ✅ |
| "Vendí jamón" | `"jamón"` or `"jamon"` | `"jamon"` ✅ |
| "Compré atún" | `"atún"` or `"atun"` | `"atun"` ✅ |
| "Vendí plátano" | `"plátano"` or `"platano"` | `"platano"` ✅ |
| "Compré melocotón" | `"melocotón"` or `"melocoton"` | `"melocoton"` ✅ |

### Variations

| User Input | Before (Inconsistent) | After (Normalized) |
|------------|----------------------|-------------------|
| "Camisa azúl" | `"azúl"` or `"azul"` | `"azul"` ✅ |
| "Pantalón marrón" | `"marrón"` or `"marron"` | `"marron"` ✅ |
| "Sillón cómodo" | `"cómodo"` or `"comodo"` | `"comodo"` ✅ |

## Real-World Examples

### Example 1: Text Message Registration

**User Input:**
```
"Vendí 5 kg de maní a 20 soles el kilo"
```

**Before (Inconsistent):**
```json
{
  "product": "maní",  // Could be "mani" or "maní"
  "quantity": 5,
  "quantity_units": "kg",
  "cost": 100
}
```

**After (Normalized):**
```json
{
  "product": "mani",  // Always "mani"
  "quantity": 5,
  "quantity_units": "kg",
  "cost": 100
}
```

### Example 2: Image Registration

**User Input:**
```
[Image shows: "Azúcar - 2kg - S/15"]
```

**Before (Inconsistent):**
```json
{
  "product": "azúcar",  // Could be "azucar" or "azúcar"
  "quantity": 2,
  "quantity_units": "kg",
  "cost": 15
}
```

**After (Normalized):**
```json
{
  "product": "azucar",  // Always "azucar"
  "quantity": 2,
  "quantity_units": "kg",
  "cost": 15
}
```

### Example 3: Query Request

**User Input:**
```
"Dame el reporte de ventas de café y azúcar del mes de octubre"
```

**Before (Inconsistent):**
```json
{
  "is_query": true,
  "products": ["café", "azúcar"]  // Might not match database
}
```

**After (Normalized):**
```json
{
  "is_query": true,
  "products": ["cafe", "azucar"]  // Always matches database
}
```

### Example 4: Multiple Products

**User Input:**
```
"Hoy vendí maní, azúcar y café"
```

**Before (Inconsistent):**
```json
[
  {"product": "maní"},
  {"product": "azúcar"},
  {"product": "café"}
]
```

**After (Normalized):**
```json
[
  {"product": "mani"},
  {"product": "azucar"},
  {"product": "cafe"}
]
```

## Query Matching Examples

### Scenario: User registered "maní" with tilde

**Database has:**
```
- Transaction 1: product = "mani"
- Transaction 2: product = "mani"
- Transaction 3: product = "mani"
```

**User queries with tilde:**
```
"Cuánto vendí de maní?"
```

**AI normalizes to:**
```json
{"products": ["mani"]}
```

**Result:** ✅ Finds all 3 transactions

### Scenario: Mixed case sensitivity

**User Input:**
```
"Vendí MANÍ, Azúcar y CaFé"
```

**AI normalizes to:**
```json
[
  {"product": "mani"},
  {"product": "azucar"},
  {"product": "cafe"}
]
```

**Result:** ✅ All lowercase, no tildes

## Unit Normalization

### Before (Inconsistent)

```json
{
  "quantity_units": "piezas"  // Plural
}
```

### After (Normalized)

```json
{
  "quantity_units": "pieza"  // Singular
}
```

### Common Units

| Before | After |
|--------|-------|
| `"piezas"` | `"pieza"` ✅ |
| `"litros"` | `"litro"` ✅ |
| `"metros"` | `"metro"` ✅ |
| `"kilos"` | `"kg"` ✅ |
| `"gramos"` | `"kg"` (converted) ✅ |

## Testing Checklist

- [ ] Register transaction with "maní" → stored as "mani"
- [ ] Register transaction with "azúcar" → stored as "azucar"
- [ ] Register transaction with "café" → stored as "cafe"
- [ ] Query "maní" → finds all "mani" transactions
- [ ] Query "azúcar" → finds all "azucar" transactions
- [ ] Query "café" → finds all "cafe" transactions
- [ ] Image with "Maní" → stored as "mani"
- [ ] Multiple products with tildes → all normalized
- [ ] Units in plural → converted to singular

## Benefits Summary

✅ **Consistency** - Same product always stored the same way
✅ **Searchability** - Queries work regardless of user input
✅ **Data Quality** - No duplicate products due to spelling
✅ **User Experience** - Natural language works as expected
✅ **Analytics** - Accurate product aggregation

## Implementation Notes

- All normalization happens at the AI prompt level
- No code changes needed in repositories or models
- Works for text, voice (transcribed), and image inputs
- Applies to products, variations, and units
- Maintains lowercase for consistency
