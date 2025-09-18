"""
Authorized user model and database operations
"""
import boto3
from datetime import datetime
from typing import Dict, Any, Optional
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class AuthorizedUser:
    """Authorized user model for WhatsApp access control"""
    
    def __init__(self, phone_number: str, **kwargs):
        self.phone_number = self._normalize_phone_number(phone_number)
        self.license_type = kwargs.get('license_type', 'basic')  # basic, premium, enterprise
        self.license_status = kwargs.get('license_status', 'active')  # active, suspended, expired
        self.registration_date = kwargs.get('registration_date', datetime.utcnow().isoformat())
        self.expiry_date = kwargs.get('expiry_date', None)
        self.company_name = kwargs.get('company_name', '')
        self.contact_name = kwargs.get('contact_name', '')
        self.email = kwargs.get('email', '')
    
    @staticmethod
    def _normalize_phone_number(phone_number: str) -> str:
        """Normalize phone number format"""
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if missing (assume Peru +51 if no country code)
        if len(digits_only) == 9:  # Peruvian mobile number without country code
            return f"+51{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('51'):  # With country code but no +
            return f"+{digits_only}"
        elif digits_only.startswith('51') and len(digits_only) > 11:  # International format
            return f"+{digits_only}"
        else:
            return f"+{digits_only}"  # Keep as is for other countries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authorized user to dictionary for DynamoDB"""
        return {
            'phone_number': self.phone_number,
            'license_type': self.license_type,
            'license_status': self.license_status,
            'registration_date': self.registration_date,
            'expiry_date': self.expiry_date,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'email': self.email
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthorizedUser':
        """Create AuthorizedUser instance from dictionary"""
        return cls(
            phone_number=data['phone_number'],
            license_type=data.get('license_type', 'basic'),
            license_status=data.get('license_status', 'active'),
            registration_date=data.get('registration_date'),
            expiry_date=data.get('expiry_date'),
            company_name=data.get('company_name', ''),
            contact_name=data.get('contact_name', ''),
            email=data.get('email', '')
        )
    
    def is_active(self) -> bool:
        """Check if the user's license is active"""
        if self.license_status != 'active':
            return False
        
        # Check expiry date if set
        if self.expiry_date:
            try:
                expiry = datetime.fromisoformat(self.expiry_date.replace('Z', '+00:00'))
                return datetime.utcnow() < expiry.replace(tzinfo=None)
            except:
                return True  # If date parsing fails, assume active
        
        return True

class AuthorizedUserRepository:
    """Repository for authorized user database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.AUTHORIZED_USERS_TABLE_NAME)
    
    def get_authorized_user(self, phone_number: str) -> Optional[AuthorizedUser]:
        """Get authorized user by phone number"""
        try:
            normalized_phone = AuthorizedUser._normalize_phone_number(phone_number)
            
            response = self.table.get_item(Key={'phone_number': normalized_phone})
            
            if 'Item' in response:
                return AuthorizedUser.from_dict(response['Item'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting authorized user {phone_number}: {str(e)}")
            return None
    
    def is_user_authorized(self, phone_number: str) -> bool:
        """Check if user is authorized and has active license"""
        try:
            user = self.get_authorized_user(phone_number)
            return user is not None and user.is_active()
            
        except Exception as e:
            logger.error(f"Error checking authorization for {phone_number}: {str(e)}")
            return False
    
    def create_authorized_user(self, user: AuthorizedUser) -> bool:
        """Create new authorized user"""
        try:
            self.table.put_item(Item=user.to_dict())
            logger.info(f"Created authorized user: {user.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating authorized user {user.phone_number}: {str(e)}")
            return False
    
    def update_license_status(self, phone_number: str, status: str) -> bool:
        """Update user's license status"""
        try:
            normalized_phone = AuthorizedUser._normalize_phone_number(phone_number)
            
            self.table.update_item(
                Key={'phone_number': normalized_phone},
                UpdateExpression='SET license_status = :status',
                ExpressionAttributeValues={':status': status}
            )
            
            logger.info(f"Updated license status for {normalized_phone} to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating license status for {phone_number}: {str(e)}")
            return False