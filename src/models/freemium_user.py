"""
FreemiumUser model and database operations for interaction tracking
"""
import boto3
from datetime import datetime
from typing import Dict, Any, Optional
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class FreemiumUser:
    """FreemiumUser model for tracking daily interaction limits"""
    
    def __init__(
        self, 
        phone_number: str, 
        interaction_count: int = 0,
        last_reset_date: str = "",
        daily_limit: int = None
    ):
        self.phone_number = phone_number
        self.interaction_count = interaction_count
        self.last_reset_date = last_reset_date or datetime.utcnow().strftime('%Y-%m-%d')
        self.daily_limit = daily_limit if daily_limit is not None else Config.FREEMIUM_DAILY_LIMIT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert freemium user to dictionary for DynamoDB"""
        return {
            'phone_number': self.phone_number,
            'interaction_count': self.interaction_count,
            'last_reset_date': self.last_reset_date,
            'daily_limit': self.daily_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FreemiumUser':
        """Create FreemiumUser instance from dictionary"""
        return cls(
            phone_number=data['phone_number'],
            interaction_count=data.get('interaction_count', 0),
            last_reset_date=data.get('last_reset_date', ''),
            daily_limit=data.get('daily_limit', Config.FREEMIUM_DAILY_LIMIT)
        )
    
    def needs_reset(self, lima_date: str) -> bool:
        """Check if interaction count needs to be reset based on Lima date"""
        return self.last_reset_date < lima_date
    
    def has_interactions_remaining(self) -> bool:
        """Check if user has interactions remaining for the day"""
        return self.interaction_count < self.daily_limit
    
    def increment_count(self) -> None:
        """Increment interaction count by 1"""
        self.interaction_count += 1
    
    def reset_count(self, lima_date: str) -> None:
        """Reset interaction count to 0 and update last reset date"""
        self.interaction_count = 0
        self.last_reset_date = lima_date


class FreemiumUserRepository:
    """Repository for freemium user interaction tracking database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.FREEMIUM_INTERACTIONS_TABLE_NAME)
    
    def get_freemium_user(self, phone_number: str) -> Optional[FreemiumUser]:
        """Get freemium user interaction data by phone number"""
        try:
            response = self.table.get_item(Key={'phone_number': phone_number})
            
            if 'Item' in response:
                return FreemiumUser.from_dict(response['Item'])
            return None
            
        except Exception as e:
            logger.error(f"Error getting freemium user {phone_number}: {str(e)}")
            return None
    
    def create_freemium_user(self, user: FreemiumUser) -> bool:
        """Create new freemium user interaction tracking record"""
        try:
            self.table.put_item(Item=user.to_dict())
            logger.info(f"Created freemium tracking for user: {user.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating freemium user {user.phone_number}: {str(e)}")
            return False
    
    def update_interaction_count(self, phone_number: str, count: int) -> bool:
        """Update user's interaction count"""
        try:
            self.table.update_item(
                Key={'phone_number': phone_number},
                UpdateExpression='SET interaction_count = :count',
                ExpressionAttributeValues={
                    ':count': count
                }
            )
            logger.info(f"Updated interaction count for {phone_number} to {count}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating interaction count for {phone_number}: {str(e)}")
            return False
    
    def reset_interaction_count(self, phone_number: str, date: str) -> bool:
        """Reset interaction count to 0 and update last reset date"""
        try:
            self.table.update_item(
                Key={'phone_number': phone_number},
                UpdateExpression='SET interaction_count = :zero, last_reset_date = :date',
                ExpressionAttributeValues={
                    ':zero': 0,
                    ':date': date
                }
            )
            logger.info(f"Reset interaction count for {phone_number} on {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting interaction count for {phone_number}: {str(e)}")
            return False
