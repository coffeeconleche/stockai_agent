"""
FreemiumService for managing freemium tier business logic
"""
import pytz
from datetime import datetime
from typing import Tuple, Optional
import logging

from src.models.freemium_user import FreemiumUser, FreemiumUserRepository
from src.models.authorized_user import AuthorizedUser, AuthorizedUserRepository
from src.config import Config

logger = logging.getLogger(__name__)


class FreemiumService:
    """Service for managing freemium tier interactions and user registration"""
    
    def __init__(self):
        self.freemium_repo = FreemiumUserRepository()
        self.authorized_repo = AuthorizedUserRepository()
    
    @staticmethod
    def get_lima_date() -> str:
        """
        Get current date in Lima, Peru timezone (America/Lima, UTC-5)
        
        Returns:
            str: Current date in YYYY-MM-DD format
        """
        try:
            lima_tz = pytz.timezone(Config.LIMA_TIMEZONE)
            lima_now = datetime.now(lima_tz)
            return lima_now.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"Error getting Lima date: {str(e)}, falling back to UTC")
            # Fallback to UTC if timezone calculation fails
            return datetime.utcnow().strftime('%Y-%m-%d')
    
    def check_and_register_user(self, phone_number: str) -> AuthorizedUser:
        """
        Check if user exists in authorized users table, create as freemium if not
        
        Args:
            phone_number: User's phone number
            
        Returns:
            AuthorizedUser: The user object (existing or newly created)
        """
        # Check if user already exists
        user = self.authorized_repo.get_authorized_user(phone_number)
        
        if user is not None:
            logger.info(f"User {phone_number} already exists with license_type={user.license_type}")
            return user
        
        # Create new freemium user
        logger.info(f"Creating new freemium user: {phone_number}")
        new_user = AuthorizedUser(
            phone_number=phone_number,
            license_type='freemium',
            license_status='active',
            registration_date=datetime.utcnow().isoformat(),
            expiry_date='',  # Empty for freemium users
            company_name='',
            contact_name='',
            email=''
        )
        
        success = self.authorized_repo.create_authorized_user(new_user)
        
        if success:
            logger.info(f"Successfully created freemium user: {phone_number}")
        else:
            logger.error(f"Failed to create freemium user: {phone_number}")
        
        return new_user
    
    def can_user_interact(self, phone_number: str) -> Tuple[bool, str]:
        """
        Check if user can interact based on their license type and daily limits
        
        Args:
            phone_number: User's phone number
            
        Returns:
            Tuple[bool, str]: (can_interact, status)
                - can_interact: True if user can interact, False if limit reached
                - status: "premium", "freemium", or "limit_reached"
        """
        # Get user from authorized users table
        user = self.authorized_repo.get_authorized_user(phone_number)
        
        if user is None:
            logger.warning(f"User {phone_number} not found in can_user_interact")
            return (False, "not_found")
        
        # Premium users have unlimited access
        if user.license_type == 'premium' and user.is_active():
            logger.info(f"Premium user {phone_number} has unlimited access")
            return (True, "premium")
        
        # Freemium users need interaction tracking
        if user.license_type == 'freemium':
            return self._check_freemium_limits(phone_number)
        
        # Unknown license type or inactive premium
        logger.warning(f"User {phone_number} has license_type={user.license_type}, status={user.license_status}")
        return (False, "unauthorized")
    
    def _check_freemium_limits(self, phone_number: str) -> Tuple[bool, str]:
        """
        Check freemium user's interaction limits with daily reset logic
        
        Args:
            phone_number: User's phone number
            
        Returns:
            Tuple[bool, str]: (can_interact, "freemium" or "limit_reached")
        """
        # Get or create freemium tracking record
        freemium_user = self.freemium_repo.get_freemium_user(phone_number)
        
        if freemium_user is None:
            # Create new tracking record
            logger.info(f"Creating freemium tracking for {phone_number}")
            lima_date = self.get_lima_date()
            freemium_user = FreemiumUser(
                phone_number=phone_number,
                interaction_count=0,
                last_reset_date=lima_date,
                daily_limit=Config.FREEMIUM_DAILY_LIMIT
            )
            self.freemium_repo.create_freemium_user(freemium_user)
            return (True, "freemium")
        
        # Check if reset is needed (new day in Lima timezone)
        lima_date = self.get_lima_date()
        if freemium_user.needs_reset(lima_date):
            logger.info(f"Resetting interaction count for {phone_number} (new day)")
            freemium_user.reset_count(lima_date)
            self.freemium_repo.reset_interaction_count(phone_number, lima_date)
        
        # Check if user has interactions remaining
        if freemium_user.has_interactions_remaining():
            remaining = freemium_user.daily_limit - freemium_user.interaction_count
            logger.info(f"Freemium user {phone_number} has {remaining} interactions remaining")
            return (True, "freemium")
        else:
            logger.info(f"Freemium user {phone_number} has reached daily limit")
            return (False, "limit_reached")
    
    def record_interaction(self, phone_number: str, interaction_type: str) -> int:
        """
        Record an interaction and return remaining interactions
        
        Args:
            phone_number: User's phone number
            interaction_type: Type of interaction ("transaction_confirmation" or "query_response")
            
        Returns:
            int: Number of remaining interactions
        """
        logger.info(f"Recording {interaction_type} for {phone_number}")
        
        # Get freemium tracking record
        freemium_user = self.freemium_repo.get_freemium_user(phone_number)
        
        if freemium_user is None:
            logger.error(f"No freemium tracking record found for {phone_number}")
            return 0
        
        # Increment count
        freemium_user.increment_count()
        
        # Update in database
        self.freemium_repo.update_interaction_count(
            phone_number, 
            freemium_user.interaction_count
        )
        
        # Calculate and return remaining
        remaining = freemium_user.daily_limit - freemium_user.interaction_count
        logger.info(f"User {phone_number} now has {remaining} interactions remaining")
        
        return max(0, remaining)
    
    def get_remaining_interactions(self, phone_number: str) -> int:
        """
        Get number of remaining interactions for a freemium user
        
        Args:
            phone_number: User's phone number
            
        Returns:
            int: Number of remaining interactions (0 if none or user not found)
        """
        freemium_user = self.freemium_repo.get_freemium_user(phone_number)
        
        if freemium_user is None:
            logger.warning(f"No freemium tracking record found for {phone_number}")
            return 0
        
        # Check if reset is needed
        lima_date = self.get_lima_date()
        if freemium_user.needs_reset(lima_date):
            # After reset, user has full daily limit
            return freemium_user.daily_limit
        
        remaining = freemium_user.daily_limit - freemium_user.interaction_count
        return max(0, remaining)
