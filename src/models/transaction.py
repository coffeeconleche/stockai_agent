"""
Transaction model and database operations
"""
import boto3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class Transaction:
    """Transaction model for sales and purchases"""
    
    def __init__(self, phone_number: str, **kwargs):
        self.transaction_id = kwargs.get('transaction_id', str(uuid.uuid4()))
        self.phone_number = phone_number
        self.transaction_type = kwargs.get('transaction_type', 0)  # 0=buy, 1=sell
        self.product = kwargs.get('product', '')
        self.product_variation = kwargs.get('product_variation', '')
        self.quantity = kwargs.get('quantity', 0)
        self.quantity_units = kwargs.get('quantity_units', '')
        self.currency = kwargs.get('currency', Config.DEFAULT_CURRENCY)
        self.cost = kwargs.get('cost', 0.0)
        self.is_perishable = kwargs.get('is_perishable', 0)  # 0=no, 1=yes
        self.date_registry = kwargs.get('date_registry', datetime.utcnow().isoformat())
        self.raw_message = kwargs.get('raw_message', '')
        self.message_type = kwargs.get('message_type', 'text')  # text, audio, image
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for DynamoDB"""
        return {
            'transaction_id': self.transaction_id,
            'phone_number': self.phone_number,
            'transaction_type': self.transaction_type,
            'product': self.product,
            'product_variation': self.product_variation,
            'quantity': Decimal(str(self.quantity)),
            'quantity_units': self.quantity_units,
            'currency': self.currency,
            'cost': Decimal(str(self.cost)),
            'is_perishable': self.is_perishable,
            'date_registry': self.date_registry,
            'raw_message': self.raw_message,
            'message_type': self.message_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create Transaction instance from dictionary"""
        return cls(
            phone_number=data['phone_number'],
            transaction_id=data.get('transaction_id'),
            transaction_type=data.get('transaction_type', 0),
            product=data.get('product', ''),
            product_variation=data.get('product_variation', ''),
            quantity=float(data.get('quantity', 0)) if isinstance(data.get('quantity'), Decimal) else data.get('quantity', 0),
            quantity_units=data.get('quantity_units', ''),
            currency=data.get('currency', Config.DEFAULT_CURRENCY),
            cost=float(data.get('cost', 0.0)) if isinstance(data.get('cost'), Decimal) else data.get('cost', 0.0),
            is_perishable=data.get('is_perishable', 0),
            date_registry=data.get('date_registry'),
            raw_message=data.get('raw_message', ''),
            message_type=data.get('message_type', 'text')
        )
    
    def get_transaction_type_text(self) -> str:
        """Get human readable transaction type"""
        return "Venta" if self.transaction_type == 1 else "Compra"
    
    def get_perishable_text(self) -> str:
        """Get human readable perishable status"""
        return "Sí" if self.is_perishable == 1 else "No"

class TransactionRepository:
    """Repository for transaction database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.TRANSACTIONS_TABLE_NAME)
    
    def create_transaction(self, transaction: Transaction) -> bool:
        """Create new transaction in database"""
        print(transaction)
        try:
            self.table.put_item(Item=transaction.to_dict())
            logger.info(f"Created transaction: {transaction.transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating transaction {transaction.transaction_id}: {str(e)}")
            return False
    
    def get_user_transactions(self, phone_number: str, limit: int = 10) -> list:
        """Get recent transactions for a user"""
        try:
            response = self.table.query(
                IndexName='phone_number-date_registry-index',  # We'll need to create this GSI
                KeyConditionExpression='phone_number = :phone',
                ExpressionAttributeValues={':phone': phone_number},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            return [Transaction.from_dict(item) for item in response.get('Items', [])]
            
        except Exception as e:
            logger.error(f"Error getting transactions for {phone_number}: {str(e)}")
            return []