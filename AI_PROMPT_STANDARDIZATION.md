# AI Prompt Standardization: Text Without Tildes (Accents)

## 🎯 Problem Identified

The AI was inconsistently handling Spanish words with tildes (accents) like:
- `maní` vs `mani`
- `azúcar` vs `azucar`
- `café` vs `cafe`
- `limón` vs `limon`

This caused issues when:
1. **Registering transactions** - Same product stored with different spellings
2. **Querying data** - Users couldn't find products due to spelling mismatches
3. **Data consistency** - Database had duplicate entries for the same product

## ✅ Solution Applied

Updated all AI prompts to **always normalize text without tildes (accents)** for consistency.

### Files Modified

- `src/services/openai_service.py` - All three AI prompts updated

### Prompts Updated

1. **Text Message Processing** (`process_text_message`)
2. **Image Processing** (`process_image_message`)
3. **Query/Report Processing** (`process_query_request`)

## 📝 Changes Made

### Added to All Prompts

```
NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos y variaciones SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Esto aplica a TODOS los campos de texto: product, product_variation, quantity_units
- Mantén las palabras en minúsculas
```

### 1. Transaction Registration Prompts

**Text Processing:**
```python
# Added normalization section
NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos y variaciones SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Esto aplica a TODOS los campos de texto: product, product_variation, quantity_units
- Mantén las palabras en minúsculas

# Added example
- Con tildes normalizadas: {"transaction_type": 1, "product": "mani", "quantity": 2, "quantity_units": "kg", "cost": 20, "is_perishable": 1}
```

**Image Processing:**
```python
# Same normalization section added
# Updated examples to show normalized text
```

### 2. Query/Report Processing Prompt

**Query Processing:**
```python
NORMALIZACIÓN DE TEXTO:
- **SIEMPRE** escribe los nombres de productos SIN TILDES (sin acentos)
- Ejemplos: "maní" → "mani", "azúcar" → "azucar", "café" → "cafe", "limón" → "limon"
- Mantén las palabras en minúsculas y en singular
- Esto asegura consistencia con los datos almacenados

# Updated examples
- "Cuánto vendí de maní esta semana"
  → {"is_query": true, "transaction_type": 1, "products": ["mani"], ...}

- "Mis ventas de azúcar y café de los últimos 30 días"
  → {"is_query": true, "transaction_type": 1, "products": ["azucar", "cafe"], ...}
```

### 3. Unit Standardization

Also fixed quantity_units to be singular:
- ❌ `"piezas"` → ✅ `"pieza"`
- ❌ `"litros"` → ✅ `"litro"`
- ❌ `"metros"` → ✅ `"metro"`

## 🔄 Expected Behavior

### Before Fix

**Registration:**
```json
// User says: "Vendí 2 kg de maní"
{"product": "maní", "quantity": 2}  // Sometimes with tilde

// User says: "Vendí 3 kg de mani"
{"product": "mani", "quantity": 3}  // Sometimes without tilde
```

**Query:**
```json
// User asks: "Cuánto vendí de maní?"
{"products": ["maní"]}  // Might not match "mani" in database
```

**Result:** ❌ Data inconsistency, queries fail to find products

### After Fix

**Registration:**
```json
// User says: "Vendí 2 kg de maní"
{"product": "mani", "quantity": 2}  // Always without tilde

// User says: "Vendí 3 kg de mani"
{"product": "mani", "quantity": 3}  // Always without tilde
```

**Query:**
```json
// User asks: "Cuánto vendí de maní?"
{"products": ["mani"]}  // Always normalized, matches database
```

**Result:** ✅ Consistent data, queries work correctly

## 📊 Impact

### Products Affected

Common Spanish products with tildes that are now standardized:
- `maní` → `mani` (peanuts)
- `azúcar` → `azucar` (sugar)
- `café` → `cafe` (coffee)
- `limón` → `limon` (lemon)
- `jamón` → `jamon` (ham)
- `atún` → `atun` (tuna)
- `plátano` → `platano` (banana)
- `melocotón` → `melocoton` (peach)

### Database Consistency

**Before:**
```
Products table:
- mani (5 transactions)
- maní (3 transactions)  ← Duplicate!
- azucar (2 transactions)
- azúcar (4 transactions)  ← Duplicate!
```

**After:**
```
Products table:
- mani (all transactions)
- azucar (all transactions)
```

## 🧪 Testing

### Test Case 1: Registration with Tildes
```
Input: "Vendí 5 kg de maní a 20 soles"
Expected Output: {"product": "mani", "quantity": 5, "cost": 20}
```

### Test Case 2: Query with Tildes
```
Input: "Dame el reporte de ventas de azúcar"
Expected Output: {"products": ["azucar"]}
```

### Test Case 3: Multiple Products
```
Input: "Vendí café y azúcar"
Expected Output: {"products": ["cafe", "azucar"]}
```

### Test Case 4: Image with Handwritten Tildes
```
Input: Image with "Maní - 2kg - S/20"
Expected Output: {"product": "mani", "quantity": 2, "cost": 20}
```

## 🚀 Deployment

The changes are in the code and will take effect immediately after deployment:

```bash
./deploy.sh
```

No database migration needed - new transactions will use normalized text automatically.

## 📋 Data Cleanup (Optional)

If you want to clean up existing data with tildes:

```python
# Example cleanup script (run manually if needed)
from src.repositories.transaction_repository import TransactionRepository
import unicodedata

def remove_accents(text):
    """Remove accents from text"""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# Update existing transactions
# repo = TransactionRepository()
# transactions = repo.get_all_transactions()
# for transaction in transactions:
#     transaction.product = remove_accents(transaction.product).lower()
#     transaction.product_variation = remove_accents(transaction.product_variation).lower()
#     repo.update_transaction(transaction)
```

## ✨ Benefits

1. **Data Consistency** - All products stored with same spelling
2. **Query Accuracy** - Users can find products regardless of how they type
3. **Simplified Search** - No need to handle accent variations
4. **Better Analytics** - Accurate product aggregation
5. **User Experience** - Queries work as expected

## 🔍 Verification

After deployment, verify the fix:

1. **Register a transaction with tildes:**
   ```
   "Vendí 2 kg de maní a 30 soles"
   ```

2. **Check the stored data:**
   ```bash
   aws dynamodb scan --table-name whatsapp-transactions --filter-expression "contains(product, :p)" --expression-attribute-values '{":p":{"S":"mani"}}' --no-cli-pager
   ```

3. **Query the data:**
   ```
   "Dame el reporte de ventas de maní"
   ```

4. **Verify results match** - Should find all "mani" transactions

## 📚 Related Files

- `src/services/openai_service.py` - All AI prompts (UPDATED)
- `src/models/transaction.py` - Transaction model
- `src/repositories/transaction_repository.py` - Database operations

## 🎉 Summary

All AI prompts now explicitly instruct the models to:
- Remove tildes (accents) from Spanish text
- Keep text in lowercase
- Use singular forms for units
- Maintain consistency across all text fields

This ensures that products like "maní", "azúcar", and "café" are always stored and queried as "mani", "azucar", and "cafe", eliminating data inconsistency issues!
