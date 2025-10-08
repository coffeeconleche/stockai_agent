# Payment Webhook Fix: Freemium to Premium Upgrade

## 🐛 Issue Identified

The payment webhook was incorrectly rejecting payments from freemium users trying to upgrade to premium. The issue was in the `check_existing_license()` function, which was checking for ANY active license without distinguishing between freemium and premium license types.

### Root Cause
```python
# OLD CODE - INCORRECT
if license_status == 'active' and expiry_date_str:
    # This blocked freemium users from upgrading!
```

The function was checking `license_status == 'active'` without checking `license_type`. Since freemium users have an active license (just with limited interactions), they were being blocked from upgrading to premium.

## ✅ Fix Applied

### 1. Updated `check_existing_license()` Function

**Before:**
- Checked if user has ANY active license
- Did not consider license type
- Blocked freemium users from upgrading

**After:**
- Checks specifically for active **PREMIUM** licenses
- Allows freemium users to upgrade
- Only blocks users who already have active premium licenses

```python
# NEW CODE - CORRECT
if license_type == 'premium' and license_status == 'active' and expiry_date_str:
    # Only blocks if user already has active PREMIUM license
```

### 2. Enhanced Payment Processing Logic

**Added:**
- License type checking in the payment approval flow
- Upgrade detection (freemium → premium)
- Better logging to distinguish between new users and upgrades

```python
# Now correctly identifies upgrades
is_upgrade = existing_license['exists'] and existing_license['license_type'] == 'freemium'
```

### 3. Improved Return Values

The `check_existing_license()` function now returns:
```python
{
    'exists': bool,           # Does user exist in system?
    'is_active': bool,        # Is PREMIUM license active?
    'license_type': str,      # 'freemium', 'premium', or None
    'expiry_date': str,       # ISO format date
    'days_remaining': int     # Days until premium expiry
}
```

## 🔄 Payment Flow After Fix

### Scenario 1: New User (No License)
```
Payment Received → No existing license → Create premium account → Send welcome message
✅ ALLOWED
```

### Scenario 2: Freemium User Upgrading
```
Payment Received → Has freemium license → Upgrade to premium → Send welcome message
✅ ALLOWED (This was previously blocked!)
```

### Scenario 3: Active Premium User
```
Payment Received → Has active premium license → Reject payment → Send "already active" message
❌ BLOCKED (Correct behavior)
```

### Scenario 4: Expired Premium User
```
Payment Received → Has expired premium license → Renew premium → Send welcome message
✅ ALLOWED
```

## 📝 Code Changes Summary

### Modified Functions

1. **`check_existing_license(phone_number)`**
   - Added `license_type` check
   - Only returns `is_active=True` for active **premium** licenses
   - Returns license type in response

2. **Payment Processing Logic**
   - Added license type validation
   - Detects freemium upgrades
   - Enhanced logging for better debugging

3. **Return Values**
   - Added `license_type` to response
   - Added `upgrade` flag to success response

## 🧪 Testing Scenarios

### Test Case 1: Freemium User Upgrade ✅
```
Given: User has used all 5 freemium interactions
When: User completes payment
Then: User is upgraded to premium with 90-day license
```

### Test Case 2: Active Premium User ❌
```
Given: User has active premium license (30 days remaining)
When: User tries to pay again
Then: Payment is rejected with "already active" message
```

### Test Case 3: New User ✅
```
Given: User has never used the system
When: User completes payment
Then: User is registered as premium with 90-day license
```

### Test Case 4: Expired Premium User ✅
```
Given: User's premium license expired 10 days ago
When: User completes payment
Then: User's premium license is renewed for 90 days
```

## 🚀 Deployment

To deploy the fix:

```bash
cd payment-webhook
./deploy-payment-webhook.sh
```

This will update the Lambda function with the corrected logic.

## 📊 Expected Behavior

### Before Fix
- ❌ Freemium users blocked from upgrading
- ❌ "Already have active license" error for freemium users
- ❌ Users stuck in freemium tier after payment

### After Fix
- ✅ Freemium users can upgrade to premium
- ✅ Only active premium users are blocked from duplicate payments
- ✅ Proper upgrade flow from freemium to premium
- ✅ Better logging and error messages

## 🔍 Verification

After deployment, verify the fix works:

1. **Check logs for freemium upgrade:**
   ```bash
   aws logs tail /aws/lambda/stockai-payment-webhook --follow
   ```

2. **Look for log message:**
   ```
   User +51XXXXXXXXX upgraded from freemium
   ```

3. **Verify user record in DynamoDB:**
   ```bash
   aws dynamodb get-item \
     --table-name whatsapp-authorized-users \
     --key '{"phone_number":{"S":"+51XXXXXXXXX"}}' \
     --query 'Item.license_type.S'
   ```
   Should return: `"premium"`

## 📋 Related Files

- `payment-webhook/lambda_function.py` - Main webhook handler (FIXED)
- `src/services/freemium_service.py` - Freemium service logic
- `src/models/freemium_user.py` - Freemium user model
- `.kiro/specs/freemium-tier/requirements.md` - Requirements document

## ✨ Summary

The fix ensures that:
1. Freemium users can successfully upgrade to premium
2. Only users with active premium licenses are blocked from duplicate payments
3. The system correctly distinguishes between license types
4. Proper logging tracks upgrades vs new registrations

The payment webhook now correctly handles all upgrade scenarios! 🎉
