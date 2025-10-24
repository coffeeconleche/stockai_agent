# User Groups CLI Management Guide

## 🚀 Quick Start

The `manage-user-groups.sh` script provides an easy command-line interface to manage user groups.

## 📋 Commands

### 1. Add Member to Group

Add a phone number to a main user's group:

```bash
./manage-user-groups.sh add-member <main_phone> <member_phone>
```

**Example:**
```bash
./manage-user-groups.sh add-member +51999999999 +51888888888
```

**Output:**
```
Adding member to group...
✓ Successfully added +51888888888 to group +51999999999
```

---

### 2. Remove Member from Group

Remove a phone number from a group:

```bash
./manage-user-groups.sh remove-member <main_phone> <member_phone>
```

**Example:**
```bash
./manage-user-groups.sh remove-member +51999999999 +51888888888
```

**Output:**
```
Removing member from group...
✓ Successfully removed +51888888888 from group +51999999999
```

---

### 3. Set Group Name

Set or update the group name:

```bash
./manage-user-groups.sh set-name <main_phone> "<group_name>"
```

**Example:**
```bash
./manage-user-groups.sh set-name +51999999999 "Mi Tienda"
```

**Output:**
```
Setting group name...
✓ Successfully set group name to "Mi Tienda" for +51999999999
```

---

### 4. View Group Details

View all details of a group:

```bash
./manage-user-groups.sh view <main_phone>
```

**Example:**
```bash
./manage-user-groups.sh view +51999999999
```

**Output:**
```
Fetching group details...

Group Details:
  Main User: +51999999999
  Group Name: Mi Tienda
  Status: Active
  Max Members: 10
  Created: 2024-10-25T10:30:00Z
  Updated: 2024-10-25T11:45:00Z

Grouped Members:
  1. +51888888888
  2. +51777777777

  Total: 2 member(s)
```

---

### 5. List All Groups

List all groups in the system:

```bash
./manage-user-groups.sh list-all
```

**Output:**
```
Fetching all groups...

Found 3 group(s):

Main User: +51999999999
Group Name: Mi Tienda
Members: 2
Status: Active
---
Main User: +51888888888
Group Name: Restaurante
Members: 3
Status: Active
---
Main User: +51777777777
Group Name: No name
Members: 1
Status: Active
---
```

---

### 6. Create New Group

Create a new empty group:

```bash
./manage-user-groups.sh create <main_phone> "<group_name>"
```

**Example:**
```bash
./manage-user-groups.sh create +51999999999 "Mi Negocio"
```

**Output:**
```
Creating new group...
✓ Successfully created group for +51999999999
  Group name: Mi Negocio
```

---

### 7. Delete Group

Delete a group completely:

```bash
./manage-user-groups.sh delete <main_phone>
```

**Example:**
```bash
./manage-user-groups.sh delete +51999999999
```

**Output:**
```
Are you sure you want to delete the group for +51999999999? (yes/no)
yes
Deleting group...
✓ Successfully deleted group for +51999999999
```

---

## 💡 Common Workflows

### Workflow 1: Setup New Store Group

```bash
# 1. Create group with name
./manage-user-groups.sh create +51999999999 "Tienda Principal"

# 2. Add employees
./manage-user-groups.sh add-member +51999999999 +51888888888
./manage-user-groups.sh add-member +51999999999 +51777777777

# 3. Verify
./manage-user-groups.sh view +51999999999
```

### Workflow 2: Setup Restaurant Group

```bash
# 1. Add first waiter (creates group automatically)
./manage-user-groups.sh add-member +51999999999 +51888888888

# 2. Set group name
./manage-user-groups.sh set-name +51999999999 "Restaurante"

# 3. Add more waiters
./manage-user-groups.sh add-member +51999999999 +51777777777
./manage-user-groups.sh add-member +51999999999 +51666666666

# 4. View final group
./manage-user-groups.sh view +51999999999
```

### Workflow 3: Update Existing Group

```bash
# 1. View current group
./manage-user-groups.sh view +51999999999

# 2. Remove old member
./manage-user-groups.sh remove-member +51999999999 +51888888888

# 3. Add new member
./manage-user-groups.sh add-member +51999999999 +51555555555

# 4. Update name
./manage-user-groups.sh set-name +51999999999 "Nuevo Nombre"

# 5. Verify changes
./manage-user-groups.sh view +51999999999
```

---

## 🎯 Real-World Examples

### Example 1: Retail Store Owner

```bash
# Owner: +51999999999
# Employee 1: +51888888888
# Employee 2: +51777777777

# Setup
./manage-user-groups.sh create +51999999999 "Tienda de Ropa"
./manage-user-groups.sh add-member +51999999999 +51888888888
./manage-user-groups.sh add-member +51999999999 +51777777777

# Result: Owner's queries now include all 3 users
```

### Example 2: Restaurant Manager

```bash
# Manager: +51999999999
# Waiters: +51888888888, +51777777777, +51666666666

# Setup
./manage-user-groups.sh add-member +51999999999 +51888888888
./manage-user-groups.sh add-member +51999999999 +51777777777
./manage-user-groups.sh add-member +51999999999 +51666666666
./manage-user-groups.sh set-name +51999999999 "Restaurante El Sabor"

# Result: Manager sees all orders from all 4 users
```

### Example 3: Market Vendor Family

```bash
# Main Vendor: +51999999999
# Family Member: +51888888888

# Setup
./manage-user-groups.sh create +51999999999 "Puesto de Frutas"
./manage-user-groups.sh add-member +51999999999 +51888888888

# Result: Combined sales from both family members
```

---

## 🔧 Advanced Usage

### Batch Operations

Create multiple groups at once:

```bash
#!/bin/bash
# batch-create-groups.sh

./manage-user-groups.sh create +51999999999 "Tienda 1"
./manage-user-groups.sh add-member +51999999999 +51888888888
./manage-user-groups.sh add-member +51999999999 +51777777777

./manage-user-groups.sh create +51666666666 "Tienda 2"
./manage-user-groups.sh add-member +51666666666 +51555555555
./manage-user-groups.sh add-member +51666666666 +51444444444
```

### Export Group List

Export all groups to a file:

```bash
./manage-user-groups.sh list-all > groups-backup.txt
```

### Check if Group Exists

```bash
./manage-user-groups.sh view +51999999999 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Group exists"
else
    echo "Group doesn't exist"
fi
```

---

## 🆘 Troubleshooting

### Error: "Group not found"

**Problem:** Trying to remove member or view non-existent group

**Solution:**
```bash
# Create the group first
./manage-user-groups.sh create +51999999999 "My Group"
```

### Error: "AWS CLI not found"

**Problem:** AWS CLI not installed

**Solution:**
```bash
# Install AWS CLI
brew install awscli  # macOS
# or
pip install awscli  # Python
```

### Error: "Access Denied"

**Problem:** AWS credentials not configured

**Solution:**
```bash
aws configure
# Enter your AWS credentials
```

### Error: "Table not found"

**Problem:** DynamoDB table doesn't exist

**Solution:**
```bash
./setup-user-groups-table.sh
```

---

## 📊 Verification

### Verify Group in DynamoDB

```bash
aws dynamodb get-item \
    --table-name whatsapp-user-groups \
    --key '{"main_phone_number":{"S":"+51999999999"}}' \
    --region us-east-1
```

### Count Total Groups

```bash
aws dynamodb scan \
    --table-name whatsapp-user-groups \
    --select COUNT \
    --region us-east-1
```

### List All Main Users

```bash
aws dynamodb scan \
    --table-name whatsapp-user-groups \
    --projection-expression "main_phone_number" \
    --region us-east-1
```

---

## 🎨 Script Features

✅ **Color-coded output** - Easy to read
✅ **Error handling** - Clear error messages
✅ **Confirmation prompts** - For destructive operations
✅ **Auto-creation** - Creates group if doesn't exist
✅ **Detailed views** - Complete group information
✅ **Batch support** - Can be used in scripts

---

## 📋 Command Reference

| Command | Arguments | Description |
|---------|-----------|-------------|
| `add-member` | `<main_phone> <member_phone>` | Add member to group |
| `remove-member` | `<main_phone> <member_phone>` | Remove member from group |
| `set-name` | `<main_phone> "<name>"` | Set group name |
| `view` | `<main_phone>` | View group details |
| `list-all` | None | List all groups |
| `create` | `<main_phone> "<name>"` | Create new group |
| `delete` | `<main_phone>` | Delete group |

---

## ✨ Tips

💡 **Use quotes for group names with spaces:**
```bash
./manage-user-groups.sh set-name +51999999999 "Mi Tienda Principal"
```

💡 **View before deleting:**
```bash
./manage-user-groups.sh view +51999999999
./manage-user-groups.sh delete +51999999999
```

💡 **List all groups regularly:**
```bash
./manage-user-groups.sh list-all
```

💡 **Create group before adding members (optional):**
```bash
./manage-user-groups.sh create +51999999999 "My Group"
./manage-user-groups.sh add-member +51999999999 +51888888888
```

---

## 🎉 You're Ready!

You can now easily manage user groups from the command line. No Python code needed! 🚀

For more information, see:
- `USER_GROUPS_IMPLEMENTATION.md` - Full documentation
- `USER_GROUPS_QUICK_START.md` - Quick start guide
