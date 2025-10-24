# -*- coding: utf-8 -*-
"""
User Group model for managing grouped phone numbers
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import boto3
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class UserGroup:
    """Model for user groups"""
    
    def __init__(
        self,
        main_phone_number: str,
        grouped_phone_numbers: List[str] = None,
        group_name: str = "",
        created_date: str = None,
        updated_date: str = None,
        max_members: int = 10,
        is_active: bool = True
    ):
        self.main_phone_number = main_phone_number
        self.grouped_phone_numbers = grouped_phone_numbers or []
        self.group_name = group_name
        self.created_date = created_date or datetime.utcnow().isoformat()
        self.updated_date = updated_date or datetime.utcnow().isoformat()
        self.max_members = max_members
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DynamoDB"""
        return {
            'main_phone_number': self.main_phone_number,
            'grouped_phone_numbers': self.grouped_phone_numbers,
            'group_name': self.group_name,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'max_members': self.max_members,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UserGroup':
        """Create UserGroup from DynamoDB item"""
        return UserGroup(
            main_phone_number=data.get('main_phone_number', ''),
            grouped_phone_numbers=data.get('grouped_phone_numbers', []),
            group_name=data.get('group_name', ''),
            created_date=data.get('created_date', ''),
            updated_date=data.get('updated_date', ''),
            max_members=data.get('max_members', 10),
            is_active=data.get('is_active', True)
        )
    
    def add_member(self, phone_number: str) -> bool:
        """Add a phone number to the group"""
        if phone_number in self.grouped_phone_numbers:
            return False  # Already in group
        
        if len(self.grouped_phone_numbers) >= self.max_members:
            return False  # Group is full
        
        self.grouped_phone_numbers.append(phone_number)
        self.updated_date = datetime.utcnow().isoformat()
        return True
    
    def remove_member(self, phone_number: str) -> bool:
        """Remove a phone number from the group"""
        if phone_number not in self.grouped_phone_numbers:
            return False  # Not in group
        
        self.grouped_phone_numbers.remove(phone_number)
        self.updated_date = datetime.utcnow().isoformat()
        return True
    
    def get_all_phone_numbers(self) -> List[str]:
        """Get all phone numbers including main user"""
        return [self.main_phone_number] + self.grouped_phone_numbers
    
    def get_member_count(self) -> int:
        """Get total number of members (including main user)"""
        return len(self.grouped_phone_numbers) + 1


class UserGroupRepository:
    """Repository for UserGroup operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.USER_GROUPS_TABLE_NAME)
    
    def get_user_group(self, main_phone_number: str) -> Optional[UserGroup]:
        """Get user group by main phone number"""
        try:
            response = self.table.get_item(Key={'main_phone_number': main_phone_number})
            
            if 'Item' in response:
                return UserGroup.from_dict(response['Item'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user group for {main_phone_number}: {str(e)}")
            return None
    
    def create_user_group(self, user_group: UserGroup) -> bool:
        """Create a new user group"""
        try:
            self.table.put_item(Item=user_group.to_dict())
            logger.info(f"Created user group for {user_group.main_phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user group for {user_group.main_phone_number}: {str(e)}")
            return False
    
    def update_user_group(self, user_group: UserGroup) -> bool:
        """Update an existing user group"""
        try:
            user_group.updated_date = datetime.utcnow().isoformat()
            self.table.put_item(Item=user_group.to_dict())
            logger.info(f"Updated user group for {user_group.main_phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user group for {user_group.main_phone_number}: {str(e)}")
            return False
    
    def add_phone_to_group(self, main_phone_number: str, phone_to_add: str) -> bool:
        """Add a phone number to a group"""
        try:
            # Get existing group or create new one
            user_group = self.get_user_group(main_phone_number)
            
            if not user_group:
                # Create new group
                user_group = UserGroup(main_phone_number=main_phone_number)
            
            # Add member
            if user_group.add_member(phone_to_add):
                return self.update_user_group(user_group)
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding {phone_to_add} to group {main_phone_number}: {str(e)}")
            return False
    
    def remove_phone_from_group(self, main_phone_number: str, phone_to_remove: str) -> bool:
        """Remove a phone number from a group"""
        try:
            user_group = self.get_user_group(main_phone_number)
            
            if not user_group:
                return False
            
            # Remove member
            if user_group.remove_member(phone_to_remove):
                return self.update_user_group(user_group)
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing {phone_to_remove} from group {main_phone_number}: {str(e)}")
            return False
    
    def update_group_name(self, main_phone_number: str, new_name: str) -> bool:
        """Update group name"""
        try:
            user_group = self.get_user_group(main_phone_number)
            
            if not user_group:
                # Create new group with name
                user_group = UserGroup(main_phone_number=main_phone_number, group_name=new_name)
                return self.create_user_group(user_group)
            
            user_group.group_name = new_name
            return self.update_user_group(user_group)
            
        except Exception as e:
            logger.error(f"Error updating group name for {main_phone_number}: {str(e)}")
            return False
    
    def delete_user_group(self, main_phone_number: str) -> bool:
        """Delete a user group"""
        try:
            self.table.delete_item(Key={'main_phone_number': main_phone_number})
            logger.info(f"Deleted user group for {main_phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user group for {main_phone_number}: {str(e)}")
            return False
    
    def is_phone_in_any_group(self, phone_number: str) -> Optional[str]:
        """
        Check if a phone number is already in another group
        Returns the main phone number if found, None otherwise
        """
        try:
            # Scan all groups to check if phone is already grouped
            response = self.table.scan()
            
            for item in response.get('Items', []):
                grouped_phones = item.get('grouped_phone_numbers', [])
                if phone_number in grouped_phones:
                    return item.get('main_phone_number')
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking if {phone_number} is in any group: {str(e)}")
            return None
