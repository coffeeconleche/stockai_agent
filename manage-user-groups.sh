#!/bin/bash

# User Groups Management CLI
# Manage user groups for WhatsApp AI Agent

REGION="us-east-1"
TABLE_NAME="whatsapp-user-groups"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}User Groups Management CLI${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  add-member <main_phone> <member_phone>     Add a member to a group"
    echo "  remove-member <main_phone> <member_phone>  Remove a member from a group"
    echo "  set-name <main_phone> <group_name>         Set group name"
    echo "  view <main_phone>                          View group details"
    echo "  list-all                                   List all groups"
    echo "  delete <main_phone>                        Delete a group"
    echo "  create <main_phone> <group_name>           Create a new group"
    echo ""
    echo "Examples:"
    echo "  $0 add-member +51999999999 +51888888888"
    echo "  $0 set-name +51999999999 \"Mi Tienda\""
    echo "  $0 view +51999999999"
    echo "  $0 list-all"
    exit 1
}

# Function to add a member to a group
add_member() {
    local main_phone=$1
    local member_phone=$2
    
    if [ -z "$main_phone" ] || [ -z "$member_phone" ]; then
        echo -e "${RED}Error: Both main phone and member phone are required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Adding member to group...${NC}"
    
    # Get existing group
    GROUP=$(aws dynamodb get-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --region $REGION \
        --output json 2>/dev/null)
    
    if [ -z "$GROUP" ] || [ "$GROUP" == "{}" ]; then
        # Create new group
        echo -e "${YELLOW}Group doesn't exist. Creating new group...${NC}"
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        aws dynamodb put-item \
            --table-name $TABLE_NAME \
            --item "{
                \"main_phone_number\": {\"S\": \"$main_phone\"},
                \"grouped_phone_numbers\": {\"L\": [{\"S\": \"$member_phone\"}]},
                \"group_name\": {\"S\": \"\"},
                \"created_date\": {\"S\": \"$TIMESTAMP\"},
                \"updated_date\": {\"S\": \"$TIMESTAMP\"},
                \"max_members\": {\"N\": \"10\"},
                \"is_active\": {\"BOOL\": true}
            }" \
            --region $REGION
    else
        # Update existing group
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        aws dynamodb update-item \
            --table-name $TABLE_NAME \
            --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
            --update-expression "SET grouped_phone_numbers = list_append(if_not_exists(grouped_phone_numbers, :empty_list), :new_member), updated_date = :timestamp" \
            --expression-attribute-values "{
                \":new_member\": {\"L\": [{\"S\": \"$member_phone\"}]},
                \":empty_list\": {\"L\": []},
                \":timestamp\": {\"S\": \"$TIMESTAMP\"}
            }" \
            --region $REGION
    fi
    
    echo -e "${GREEN}✓ Successfully added $member_phone to group $main_phone${NC}"
}

# Function to remove a member from a group
remove_member() {
    local main_phone=$1
    local member_phone=$2
    
    if [ -z "$main_phone" ] || [ -z "$member_phone" ]; then
        echo -e "${RED}Error: Both main phone and member phone are required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Removing member from group...${NC}"
    
    # Get current group
    GROUP=$(aws dynamodb get-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --region $REGION \
        --output json)
    
    if [ -z "$GROUP" ] || [ "$GROUP" == "{}" ]; then
        echo -e "${RED}Error: Group not found${NC}"
        exit 1
    fi
    
    # Extract current members
    MEMBERS=$(echo $GROUP | jq -r '.Item.grouped_phone_numbers.L[].S' 2>/dev/null)
    
    # Build new member list (excluding the one to remove)
    NEW_MEMBERS="["
    FIRST=true
    for member in $MEMBERS; do
        if [ "$member" != "$member_phone" ]; then
            if [ "$FIRST" = true ]; then
                NEW_MEMBERS="${NEW_MEMBERS}{\"S\":\"$member\"}"
                FIRST=false
            else
                NEW_MEMBERS="${NEW_MEMBERS},{\"S\":\"$member\"}"
            fi
        fi
    done
    NEW_MEMBERS="${NEW_MEMBERS}]"
    
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Update group
    aws dynamodb update-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --update-expression "SET grouped_phone_numbers = :members, updated_date = :timestamp" \
        --expression-attribute-values "{
            \":members\": {\"L\": $NEW_MEMBERS},
            \":timestamp\": {\"S\": \"$TIMESTAMP\"}
        }" \
        --region $REGION
    
    echo -e "${GREEN}✓ Successfully removed $member_phone from group $main_phone${NC}"
}

# Function to set group name
set_name() {
    local main_phone=$1
    local group_name=$2
    
    if [ -z "$main_phone" ] || [ -z "$group_name" ]; then
        echo -e "${RED}Error: Both main phone and group name are required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Setting group name...${NC}"
    
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Check if group exists
    GROUP=$(aws dynamodb get-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --region $REGION \
        --output json 2>/dev/null)
    
    if [ -z "$GROUP" ] || [ "$GROUP" == "{}" ]; then
        # Create new group with name
        echo -e "${YELLOW}Group doesn't exist. Creating new group with name...${NC}"
        
        aws dynamodb put-item \
            --table-name $TABLE_NAME \
            --item "{
                \"main_phone_number\": {\"S\": \"$main_phone\"},
                \"grouped_phone_numbers\": {\"L\": []},
                \"group_name\": {\"S\": \"$group_name\"},
                \"created_date\": {\"S\": \"$TIMESTAMP\"},
                \"updated_date\": {\"S\": \"$TIMESTAMP\"},
                \"max_members\": {\"N\": \"10\"},
                \"is_active\": {\"BOOL\": true}
            }" \
            --region $REGION
    else
        # Update existing group
        aws dynamodb update-item \
            --table-name $TABLE_NAME \
            --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
            --update-expression "SET group_name = :name, updated_date = :timestamp" \
            --expression-attribute-values "{
                \":name\": {\"S\": \"$group_name\"},
                \":timestamp\": {\"S\": \"$TIMESTAMP\"}
            }" \
            --region $REGION
    fi
    
    echo -e "${GREEN}✓ Successfully set group name to \"$group_name\" for $main_phone${NC}"
}

# Function to view group details
view_group() {
    local main_phone=$1
    
    if [ -z "$main_phone" ]; then
        echo -e "${RED}Error: Main phone number is required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Fetching group details...${NC}"
    echo ""
    
    GROUP=$(aws dynamodb get-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --region $REGION \
        --output json)
    
    if [ -z "$GROUP" ] || [ "$GROUP" == "{}" ] || [ "$(echo $GROUP | jq -r '.Item')" == "null" ]; then
        echo -e "${YELLOW}No group found for $main_phone${NC}"
        exit 0
    fi
    
    # Extract details
    GROUP_NAME=$(echo $GROUP | jq -r '.Item.group_name.S // "No name set"')
    CREATED=$(echo $GROUP | jq -r '.Item.created_date.S // "Unknown"')
    UPDATED=$(echo $GROUP | jq -r '.Item.updated_date.S // "Unknown"')
    IS_ACTIVE=$(echo $GROUP | jq -r '.Item.is_active.BOOL // true')
    MAX_MEMBERS=$(echo $GROUP | jq -r '.Item.max_members.N // "10"')
    
    echo -e "${GREEN}Group Details:${NC}"
    echo -e "  Main User: ${BLUE}$main_phone${NC}"
    echo -e "  Group Name: ${BLUE}$GROUP_NAME${NC}"
    echo -e "  Status: ${BLUE}$([ "$IS_ACTIVE" == "true" ] && echo "Active" || echo "Inactive")${NC}"
    echo -e "  Max Members: ${BLUE}$MAX_MEMBERS${NC}"
    echo -e "  Created: ${BLUE}$CREATED${NC}"
    echo -e "  Updated: ${BLUE}$UPDATED${NC}"
    echo ""
    echo -e "${GREEN}Grouped Members:${NC}"
    
    MEMBERS=$(echo $GROUP | jq -r '.Item.grouped_phone_numbers.L[]?.S' 2>/dev/null)
    
    if [ -z "$MEMBERS" ]; then
        echo -e "  ${YELLOW}No members in group${NC}"
    else
        COUNT=0
        for member in $MEMBERS; do
            COUNT=$((COUNT + 1))
            echo -e "  $COUNT. ${BLUE}$member${NC}"
        done
        echo ""
        echo -e "  ${GREEN}Total: $COUNT member(s)${NC}"
    fi
    echo ""
}

# Function to list all groups
list_all() {
    echo -e "${BLUE}Fetching all groups...${NC}"
    echo ""
    
    GROUPS=$(aws dynamodb scan \
        --table-name $TABLE_NAME \
        --region $REGION \
        --output json)
    
    COUNT=$(echo $GROUPS | jq -r '.Items | length')
    
    if [ "$COUNT" -eq 0 ]; then
        echo -e "${YELLOW}No groups found${NC}"
        exit 0
    fi
    
    echo -e "${GREEN}Found $COUNT group(s):${NC}"
    echo ""
    
    echo $GROUPS | jq -r '.Items[] | 
        "Main User: \(.main_phone_number.S)\n" +
        "Group Name: \(.group_name.S // "No name")\n" +
        "Members: \((.grouped_phone_numbers.L | length) // 0)\n" +
        "Status: \(if .is_active.BOOL then "Active" else "Inactive" end)\n" +
        "---"'
}

# Function to delete a group
delete_group() {
    local main_phone=$1
    
    if [ -z "$main_phone" ]; then
        echo -e "${RED}Error: Main phone number is required${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Are you sure you want to delete the group for $main_phone? (yes/no)${NC}"
    read -r confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${BLUE}Cancelled${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}Deleting group...${NC}"
    
    aws dynamodb delete-item \
        --table-name $TABLE_NAME \
        --key "{\"main_phone_number\":{\"S\":\"$main_phone\"}}" \
        --region $REGION
    
    echo -e "${GREEN}✓ Successfully deleted group for $main_phone${NC}"
}

# Function to create a new group
create_group() {
    local main_phone=$1
    local group_name=$2
    
    if [ -z "$main_phone" ]; then
        echo -e "${RED}Error: Main phone number is required${NC}"
        exit 1
    fi
    
    if [ -z "$group_name" ]; then
        group_name=""
    fi
    
    echo -e "${BLUE}Creating new group...${NC}"
    
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    aws dynamodb put-item \
        --table-name $TABLE_NAME \
        --item "{
            \"main_phone_number\": {\"S\": \"$main_phone\"},
            \"grouped_phone_numbers\": {\"L\": []},
            \"group_name\": {\"S\": \"$group_name\"},
            \"created_date\": {\"S\": \"$TIMESTAMP\"},
            \"updated_date\": {\"S\": \"$TIMESTAMP\"},
            \"max_members\": {\"N\": \"10\"},
            \"is_active\": {\"BOOL\": true}
        }" \
        --region $REGION
    
    echo -e "${GREEN}✓ Successfully created group for $main_phone${NC}"
    if [ -n "$group_name" ]; then
        echo -e "  Group name: ${BLUE}$group_name${NC}"
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    usage
fi

COMMAND=$1
shift

case $COMMAND in
    add-member)
        add_member "$@"
        ;;
    remove-member)
        remove_member "$@"
        ;;
    set-name)
        set_name "$@"
        ;;
    view)
        view_group "$@"
        ;;
    list-all)
        list_all
        ;;
    delete)
        delete_group "$@"
        ;;
    create)
        create_group "$@"
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        usage
        ;;
esac
