# User Groups - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup Infrastructure

```bash
./setup-user-groups-table.sh
```

This creates the DynamoDB table and updates permissions.

### Step 2: Deploy Code

```bash
./deploy.sh
```

### Step 3: Create a Group

```python
from src.models import UserGroupRepository

repo = UserGroupRepository()

# Add members to main user's group
repo.add_phone_to_group("+51999999999", "+51888888888")
repo.add_phone_to_group("+51999999999", "+51777777777")

# Set group name
repo.update_group_name("+51999999999", "Mi Negocio")
```

Done! Now when the main user queries, they'll see data from all 3 users.

---

## 📊 How It Works

### Without Group

```
User: "Dame el reporte de ventas"
↓
Query: Only user's transactions
↓
Result: Individual report
```

### With Group

```
Main User: "Dame el reporte de ventas"
↓
Query: Main user + 2 grouped members
↓
Result: Combined report
        "👥 Grupo: Mi Negocio (3 usuarios)"
```

---

## 💡 Common Use Cases

### Retail Store

```python
# Owner groups 2 employees
repo.add_phone_to_group("+51999999999", "+51888888888")
repo.add_phone_to_group("+51999999999", "+51777777777")
repo.update_group_name("+51999999999", "Tienda Principal")
```

**Result:** Owner sees combined sales from all 3 users

### Restaurant

```python
# Manager groups 3 waiters
repo.add_phone_to_group("+51999999999", "+51888888888")
repo.add_phone_to_group("+51999999999", "+51777777777")
repo.add_phone_to_group("+51999999999", "+51666666666")
repo.update_group_name("+51999999999", "Restaurante")
```

**Result:** Manager sees all orders from all 4 users

---

## 🔧 Management Functions

### Create Group

```python
from src.models import UserGroup, UserGroupRepository

repo = UserGroupRepository()

# Create new group
group = UserGroup(
    main_phone_number="+51999999999",
    grouped_phone_numbers=["+51888888888", "+51777777777"],
    group_name="Mi Negocio"
)
repo.create_user_group(group)
```

### Add Member

```python
repo.add_phone_to_group("+51999999999", "+51666666666")
```

### Remove Member

```python
repo.remove_phone_from_group("+51999999999", "+51666666666")
```

### Update Name

```python
repo.update_group_name("+51999999999", "Nuevo Nombre")
```

### View Group

```python
group = repo.get_user_group("+51999999999")
print(f"Group: {group.group_name}")
print(f"Members: {group.get_member_count()}")
print(f"Phones: {group.get_all_phone_numbers()}")
```

### Delete Group

```python
repo.delete_user_group("+51999999999")
```

---

## 🧪 Testing

### Test 1: Create Group

```python
repo = UserGroupRepository()
repo.add_phone_to_group("+51999999999", "+51888888888")
repo.update_group_name("+51999999999", "Test Group")

# Verify
group = repo.get_user_group("+51999999999")
assert group.group_name == "Test Group"
assert len(group.grouped_phone_numbers) == 1
```

### Test 2: Query with Group

```
Main User: "Dame el reporte de ventas"
Expected: Report shows "👥 Grupo: Test Group (2 usuarios)"
```

### Test 3: Remove Member

```python
repo.remove_phone_from_group("+51999999999", "+51888888888")

# Verify
group = repo.get_user_group("+51999999999")
assert len(group.grouped_phone_numbers) == 0
```

---

## ⚙️ Configuration

### Enable/Disable

```bash
# .env
ENABLE_USER_GROUPS=true  # Enable
ENABLE_USER_GROUPS=false # Disable
```

### Adjust Limits

```bash
# .env
MAX_GROUP_MEMBERS=10  # Default
MAX_GROUP_MEMBERS=20  # Increase limit
```

---

## 🔍 Verification

### Check Table Exists

```bash
aws dynamodb describe-table \
    --table-name whatsapp-user-groups \
    --region us-east-1
```

### Check Lambda Config

```bash
aws lambda get-function-configuration \
    --function-name whatsapp-ai-agent \
    --query 'Environment.Variables.USER_GROUPS_TABLE_NAME'
```

### Check Group in DynamoDB

```bash
aws dynamodb get-item \
    --table-name whatsapp-user-groups \
    --key '{"main_phone_number":{"S":"+51999999999"}}'
```

---

## 📋 Checklist

- [ ] Run `./setup-user-groups-table.sh`
- [ ] Deploy with `./deploy.sh`
- [ ] Create test group
- [ ] Add members
- [ ] Set group name
- [ ] Test query
- [ ] Verify group info in report

---

## 🎯 Key Points

✅ **Automatic** - Grouped queries happen automatically
✅ **Transparent** - No special commands needed
✅ **Private** - Grouped members don't know they're grouped
✅ **Flexible** - Add/remove members anytime
✅ **Scalable** - Up to 10 members per group (configurable)

---

## 🆘 Troubleshooting

### Group Not Working

1. Check `ENABLE_USER_GROUPS=true` in Lambda
2. Verify table exists
3. Check group was created correctly
4. Redeploy Lambda

### Members Not Included

1. Verify members added to group
2. Check `is_active=true` on group
3. Check CloudWatch logs

### Report Not Showing Group Info

1. Verify group has name set
2. Check phone_number passed to format functions
3. Redeploy Lambda

---

## ✨ You're All Set!

Your user groups feature is ready to use. Create groups programmatically and enjoy consolidated reports! 🎉

For full documentation, see `USER_GROUPS_IMPLEMENTATION.md`
