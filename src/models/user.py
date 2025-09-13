"""
User model and database operations
"""
import boto3
from datetime import datetime
from typing import Dict, Any, Optional
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class User:
    """User model for WhatsApp users"""
    
    def __init__(self, phone_number: str, profile_name: str = "", **kwargs):
        self.phone_number = self._normalize_phone_number(phone_number)
        self.profile_name = profile_name
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.last_interaction = kwargs.get('last_interaction', datetime.utcnow().isoformat())
        self.message_count = kwargs.get('message_count', 0)
        self.is_active = kwargs.get('is_active', True)
        self.language = kwargs.get('language', Config.DEFAULT_LANGUAGE)
        
    @staticmethod
    def _normalize_phone_number(phone_number: str) -> str:
        """Normalize phone number to include + prefix"""
        # Remove any existing + and whitespace
        clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        # Add + prefix
        return f"+{clean_number}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for DynamoDB"""
        return {
            'phone_number': self.phone_number,
            'profile_name': self.profile_name,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'message_count': self.message_count,
            'is_active': self.is_active,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            phone_number=data['phone_number'],
            profile_name=data.get('profile_name', ''),
            created_at=data.get('created_at'),
            last_interaction=data.get('last_interaction'),
            message_count=data.get('message_count', 0),
            is_active=data.get('is_active', True),
            language=data.get('language', Config.DEFAULT_LANGUAGE)
        )

class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.USERS_TABLE_NAME)
    
    def get_user(self, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            normalized_phone = User._normalize_phone_number(phone_number)
            response = self.table.get_item(Key={'phone_number': normalized_phone})
            
            if 'Item' in response:
                return User.from_dict(response['Item'])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {phone_number}: {str(e)}")
            return None
    
    def create_user(self, user: User) -> bool:
        """Create new user in database"""
        try:
            self.table.put_item(Item=user.to_dict())
            logger.info(f"Created new user: {user.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {user.phone_number}: {str(e)}")
            return False
    
    def update_user_interaction(self, phone_number: str) -> bool:
        """Update user's last interaction and increment message count"""
        try:
            normalized_phone = User._normalize_phone_number(phone_number)
            self.table.update_item(
                Key={'phone_number': normalized_phone},
                UpdateExpression='SET last_interaction = :timestamp, message_count = message_count + :inc',
                ExpressionAttributeValues={
                    ':timestamp': datetime.utcnow().isoformat(),
                    ':inc': 1
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating user interaction {phone_number}: {str(e)}")
            return False
    
    def user_exists(self, phone_number: str) -> bool:
        """Check if user exists in database"""
        return self.get_user(phone_number) is not None