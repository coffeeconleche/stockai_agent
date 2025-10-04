# -*- coding: utf-8 -*-
"""
Pending transaction model and database operations
"""
import boto3
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class PendingTransaction:
    """Pending transaction model for confirmation workflow"""
    
    def __init__(self, phone_number: str, **kwargs):
        self.session_id = kwargs.get('session_id', str(uuid.uuid4()))
        self.phone_number = phone_number
        self.transactions_data = kwargs.get('transactions_data', [])  # List of transaction dicts
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.expires_at = kwargs.get('expires_at', None)  # Optional expiration
        self.message_type = kwargs.get('message_type', 'text')  # text, audio, image
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert pending transaction to dictionary for DynamoDB"""
        return {
            'phone_number': self.phone_number,
            'session_id': self.session_id,
            'transactions_data': json.dumps(self.transactions_data),  # Store as JSON string
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'message_type': self.message_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PendingTransaction':
        """Create PendingTransaction instance from dictionary"""
        transactions_data = data.get('transactions_data', '[]')
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)
        
        return cls(
            phone_number=data['phone_number'],
            session_id=data.get('session_id'),
            transactions_data=transactions_data,
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
            message_type=data.get('message_type', 'text')
        )

class PendingTransactionRepository:
    """Repository for pending transaction database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.PENDING_TRANSACTIONS_TABLE_NAME)
    
    def create_pending_transaction(self, pending_transaction: PendingTransaction) -> bool:
        """Create new pending transaction in database"""
        try:
            self.table.put_item(Item=pending_transaction.to_dict())
            logger.info(f"Created pending transaction session: {pending_transaction.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pending transaction {pending_transaction.session_id}: {str(e)}")
            return False
    
    def get_pending_transaction(self, phone_number: str) -> Optional[PendingTransaction]:
        """Get most recent pending transaction for a user"""
        try:
            response = self.table.get_item(Key={'phone_number': phone_number})
            
            if 'Item' in response:
                return PendingTransaction.from_dict(response['Item'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pending transaction for {phone_number}: {str(e)}")
            return None
    
    def update_pending_transaction(self, phone_number: str, transactions_data: List[Dict[str, Any]]) -> bool:
        """Update pending transaction data (for edits)"""
        try:
            self.table.update_item(
                Key={'phone_number': phone_number},
                UpdateExpression='SET transactions_data = :data, created_at = :timestamp',
                ExpressionAttributeValues={
                    ':data': json.dumps(transactions_data),
                    ':timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Updated pending transaction for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating pending transaction for {phone_number}: {str(e)}")
            return False
    
    def delete_pending_transaction(self, phone_number: str) -> bool:
        """Delete pending transaction after confirmation or cancellation"""
        try:
            self.table.delete_item(Key={'phone_number': phone_number})
            logger.info(f"Deleted pending transaction for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting pending transaction for {phone_number}: {str(e)}")
            return False
