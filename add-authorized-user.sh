#!/bin/bash

# Script to add authorized users to the WhatsApp AI Agent

REGION="us-east-1"
AUTHORIZED_USERS_TABLE="whatsapp-authorized-users"

# Function to add a user
add_user() {
    local phone_number="$1"
    local country_code="${2:-}"
    local license_type="${3:-basic}"
    local company_name="${4:-}"
    local contact_name="${5:-}"
    local email="${6:-}"
    
    echo "📱 Adding authorized user: $phone_number"
    
    # Normalize phone number with country code
    if [[ ! $phone_number =~ ^\+ ]]; then
        if [[ -n "$country_code" ]]; then
            # Use provided country code
            phone_number="+${country_code}${phone_number}"
        elif [[ ${#phone_number} -eq 9 && $phone_number =~ ^[0-9]+$ ]]; then
            # Default to Peru (+51) for 9-digit numbers if no country code provided
            phone_number="+51$phone_number"
            echo "⚠️  No country code provided, defaulting to Peru (+51)"
        else
            echo "❌ Invalid phone number format. Please provide country code or use format: +[country][number]"
            return 1
        fi
    fi
    
    # Create a temporary JSON file to avoid escaping issues
    local temp_file=$(mktemp)
    local registration_date=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    cat > "$temp_file" << EOF
{
    "phone_number": {"S": "$phone_number"},
    "license_type": {"S": "$license_type"},
    "license_status": {"S": "active"},
    "registration_date": {"S": "$registration_date"},
    "company_name": {"S": "$company_name"},
    "contact_name": {"S": "$contact_name"},
    "email": {"S": "$email"}
}
EOF
    
    echo "📄 Item JSON:"
    cat "$temp_file"
    echo ""
    
    aws dynamodb put-item \
        --table-name "$AUTHORIZED_USERS_TABLE" \
        --item file://"$temp_file" \
        --region "$REGION"
    
    local result=$?
    rm -f "$temp_file"
    
    if [ $result -eq 0 ]; then
        echo "✅ Successfully added user: $phone_number"
    else
        echo "❌ Failed to add user: $phone_number"
    fi
}

# Function to list all authorized users
list_users() {
    echo "📋 Listing all authorized users:"
    aws dynamodb scan \
        --table-name $AUTHORIZED_USERS_TABLE \
        --region $REGION \
        --output table
}

# Function to remove a user
remove_user() {
    local phone_number="$1"
    local country_code="${2:-}"
    
    # Normalize phone number with country code
    if [[ ! $phone_number =~ ^\+ ]]; then
        if [[ -n "$country_code" ]]; then
            phone_number="+${country_code}${phone_number}"
        elif [[ ${#phone_number} -eq 9 && $phone_number =~ ^[0-9]+$ ]]; then
            phone_number="+51$phone_number"
            echo "⚠️  No country code provided, defaulting to Peru (+51)"
        else
            echo "❌ Invalid phone number format. Please provide country code or use format: +[country][number]"
            return 1
        fi
    fi
    
    echo "🗑️ Removing authorized user: $phone_number"
    
    aws dynamodb delete-item \
        --table-name $AUTHORIZED_USERS_TABLE \
        --key '{"phone_number": {"S": "'$phone_number'"}}' \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully removed user: $phone_number"
    else
        echo "❌ Failed to remove user: $phone_number"
    fi
}

# Function to suspend a user
suspend_user() {
    local phone_number="$1"
    local country_code="${2:-}"
    
    # Normalize phone number with country code
    if [[ ! $phone_number =~ ^\+ ]]; then
        if [[ -n "$country_code" ]]; then
            phone_number="+${country_code}${phone_number}"
        elif [[ ${#phone_number} -eq 9 && $phone_number =~ ^[0-9]+$ ]]; then
            phone_number="+51$phone_number"
            echo "⚠️  No country code provided, defaulting to Peru (+51)"
        else
            echo "❌ Invalid phone number format. Please provide country code or use format: +[country][number]"
            return 1
        fi
    fi
    
    echo "⏸️ Suspending user: $phone_number"
    
    aws dynamodb update-item \
        --table-name $AUTHORIZED_USERS_TABLE \
        --key '{"phone_number": {"S": "'$phone_number'"}}' \
        --update-expression "SET license_status = :status" \
        --expression-attribute-values '{":status": {"S": "suspended"}}' \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully suspended user: $phone_number"
    else
        echo "❌ Failed to suspend user: $phone_number"
    fi
}

# Function to reactivate a user
reactivate_user() {
    local phone_number="$1"
    local country_code="${2:-}"
    
    # Normalize phone number with country code
    if [[ ! $phone_number =~ ^\+ ]]; then
        if [[ -n "$country_code" ]]; then
            phone_number="+${country_code}${phone_number}"
        elif [[ ${#phone_number} -eq 9 && $phone_number =~ ^[0-9]+$ ]]; then
            phone_number="+51$phone_number"
            echo "⚠️  No country code provided, defaulting to Peru (+51)"
        else
            echo "❌ Invalid phone number format. Please provide country code or use format: +[country][number]"
            return 1
        fi
    fi
    
    echo "▶️ Reactivating user: $phone_number"
    
    aws dynamodb update-item \
        --table-name $AUTHORIZED_USERS_TABLE \
        --key '{"phone_number": {"S": "'$phone_number'"}}' \
        --update-expression "SET license_status = :status" \
        --expression-attribute-values '{":status": {"S": "active"}}' \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully reactivated user: $phone_number"
    else
        echo "❌ Failed to reactivate user: $phone_number"
    fi
}

# Main script logic
case "$1" in
    "add")
        if [ -z "$2" ]; then
            echo "Usage: $0 add <phone_number> [country_code] [license_type] [company_name] [contact_name] [email]"
            echo "Examples:"
            echo "  $0 add 987654321 51 premium 'Mi Empresa' 'Juan Perez' 'juan@empresa.com'  # Peru"
            echo "  $0 add 1234567890 1 basic 'US Company' 'John Doe' 'john@company.com'     # USA"
            echo "  $0 add +51987654321 '' premium 'Mi Empresa' 'Juan Perez' 'juan@empresa.com'  # Full format"
            exit 1
        fi
        add_user "$2" "$3" "$4" "$5" "$6" "$7"
        ;;
    "list")
        list_users
        ;;
    "remove")
        if [ -z "$2" ]; then
            echo "Usage: $0 remove <phone_number> [country_code]"
            echo "Examples:"
            echo "  $0 remove 987654321 51     # Peru"
            echo "  $0 remove +51987654321    # Full format"
            exit 1
        fi
        remove_user "$2" "$3"
        ;;
    "suspend")
        if [ -z "$2" ]; then
            echo "Usage: $0 suspend <phone_number> [country_code]"
            exit 1
        fi
        suspend_user "$2" "$3"
        ;;
    "reactivate")
        if [ -z "$2" ]; then
            echo "Usage: $0 reactivate <phone_number> [country_code]"
            exit 1
        fi
        reactivate_user "$2" "$3"
        ;;
    *)
        echo "🔧 WhatsApp AI Agent - Authorized Users Management"
        echo ""
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  add <phone> [country_code] [type] [company] [name] [email]  Add authorized user"
        echo "  list                                                        List all authorized users"
        echo "  remove <phone> [country_code]                               Remove authorized user"
        echo "  suspend <phone> [country_code]                              Suspend user license"
        echo "  reactivate <phone> [country_code]                           Reactivate user license"
        echo ""
        echo "Examples:"
        echo "  $0 add 987654321 51 premium 'Mi Empresa' 'Juan Perez' 'juan@empresa.com'  # Peru"
        echo "  $0 add 1234567890 1 basic 'US Company' 'John Doe' 'john@company.com'     # USA"
        echo "  $0 add +51987654321 '' premium 'Mi Empresa'                               # Full format"
        echo "  $0 list                                                                    # List all users"
        echo "  $0 suspend 987654321 51                                                    # Suspend user"
        echo "  $0 remove +51987654321                                                     # Remove user"
        echo ""
        echo "License types: basic, premium, enterprise"
        echo "Common country codes: 51 (Peru), 1 (USA/Canada), 52 (Mexico), 54 (Argentina), 55 (Brazil)"
        exit 1
        ;;
esac