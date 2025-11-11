# User Groups CLI - Quick Reference

## 🚀 One-Line Commands

### Add Member
```bash
./manage-user-groups.sh add-member +51999999999 +51888888888
```

### Remove Member
```bash
./manage-user-groups.sh remove-member +51999999999 +51888888888
```

### Set Group Name
```bash
./manage-user-groups.sh set-name +51999999999 "Mi Tienda"
```

### View Group
```bash
./manage-user-groups.sh view +51999999999
```

### List All Groups
```bash
./manage-user-groups.sh list-all
```

### Create Group
```bash
./manage-user-groups.sh create +51999999999 "Mi Negocio"
```

### Delete Group
```bash
./manage-user-groups.sh delete +51999999999
```

---

## 💡 Quick Setup Example

```bash
# 1. Create group
./manage-user-groups.sh create +51999999999 "Tienda Principal"

# 2. Add employees
./manage-user-groups.sh add-member +51999999999 +51888888888
./manage-user-groups.sh add-member +51999999999 +51777777777

# 3. Verify
./manage-user-groups.sh view +51999999999
```

**Result:** Owner's queries now include all 3 users! 🎉

---

## 📖 Full Documentation

See `USER_GROUPS_CLI_GUIDE.md` for complete usage guide.
