# -*- coding: utf-8 -*-
"""
Query service for transaction reports
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class QueryService:
    """Service for querying transaction reports"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        self.table = self.dynamodb.Table(Config.TRANSACTIONS_TABLE_NAME)
        self.query_threshold = Config.QUERY_THRESHOLD
        
        # Import here to avoid circular dependency
        from src.models import UserGroupRepository
        self.user_group_repo = UserGroupRepository()
    
    def get_all_phone_numbers_for_query(self, phone_number: str) -> List[str]:
        """
        Get all phone numbers to query (main user + grouped members)
        
        Args:
            phone_number: The requesting user's phone number
            
        Returns:
            List of phone numbers including the main user and grouped members
        """
        try:
            # Always include the requesting user
            phone_numbers = [phone_number]
            
            # Check if user groups feature is enabled
            if not Config.ENABLE_USER_GROUPS:
                return phone_numbers
            
            # Check if user has a group
            user_group = self.user_group_repo.get_user_group(phone_number)
            
            if user_group and user_group.is_active and user_group.grouped_phone_numbers:
                phone_numbers.extend(user_group.grouped_phone_numbers)
                logger.info(f"User {phone_number} has group with {len(user_group.grouped_phone_numbers)} members")
            
            return phone_numbers
            
        except Exception as e:
            logger.error(f"Error getting phone numbers for query: {str(e)}")
            # Return at least the requesting user
            return [phone_number]
    
    def query_transactions(self, phone_number: str, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query transactions based on parameters - supports grouped queries"""
        try:
            # Get all phone numbers to query (main + grouped)
            phone_numbers = self.get_all_phone_numbers_for_query(phone_number)
            
            logger.info(f"Querying transactions for {len(phone_numbers)} phone number(s)")
            
            # Query transactions for all phone numbers
            all_transactions = []
            
            for phone in phone_numbers:
                transactions = self._query_single_phone(phone, query_params)
                all_transactions.extend(transactions)
            
            logger.info(f"Total transactions found: {len(all_transactions)}")
            return all_transactions
            
        except Exception as e:
            logger.error(f"Error querying transactions: {str(e)}")
            return []
    
    def _query_single_phone(self, phone_number: str, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query transactions for a single phone number"""
        try:
            date_from = query_params.get('date_from')
            date_to = query_params.get('date_to')
            
            # Scenario analysis for optimal query strategy:
            # 1. With date range: Use GSI with KeyConditionExpression on date_registry
            # 2. Without date range: Query all by phone_number
            # 3. Apply additional filters (transaction_type, products) after retrieval
            
            transactions = []
            
            if date_from or date_to:
                # Scenario: Date range specified - use GSI efficiently
                key_condition = Key('phone_number').eq(phone_number)
                
                # Add date range to key condition if both dates provided
                if date_from and date_to:
                    # Use BETWEEN for efficient range query
                    end_date = date_to + 'T23:59:59.999Z'
                    key_condition = key_condition & Key('date_registry').between(date_from, end_date)
                elif date_from:
                    # Only start date
                    key_condition = key_condition & Key('date_registry').gte(date_from)
                elif date_to:
                    # Only end date
                    end_date = date_to + 'T23:59:59.999Z'
                    key_condition = key_condition & Key('date_registry').lte(end_date)
                
                try:
                    response = self.table.query(
                        IndexName='phone_number-date_registry-index',
                        KeyConditionExpression=key_condition
                    )
                    transactions = response.get('Items', [])
                    
                    # Handle pagination if needed
                    while 'LastEvaluatedKey' in response:
                        response = self.table.query(
                            IndexName='phone_number-date_registry-index',
                            KeyConditionExpression=key_condition,
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        transactions.extend(response.get('Items', []))
                    
                    logger.info(f"Queried with date range using GSI: {len(transactions)} items")
                    
                except Exception as e:
                    logger.error(f"GSI query failed: {str(e)}, falling back to scan")
                    # Fallback to scan
                    filter_expr = Attr('phone_number').eq(phone_number)
                    if date_from:
                        filter_expr = filter_expr & Attr('date_registry').gte(date_from)
                    if date_to:
                        end_date = date_to + 'T23:59:59.999Z'
                        filter_expr = filter_expr & Attr('date_registry').lte(end_date)
                    
                    response = self.table.scan(FilterExpression=filter_expr)
                    transactions = response.get('Items', [])
            else:
                # Scenario: No date range - query all transactions for user
                try:
                    response = self.table.query(
                        IndexName='phone_number-date_registry-index',
                        KeyConditionExpression=Key('phone_number').eq(phone_number)
                    )
                    transactions = response.get('Items', [])
                    
                    # Handle pagination
                    while 'LastEvaluatedKey' in response:
                        response = self.table.query(
                            IndexName='phone_number-date_registry-index',
                            KeyConditionExpression=Key('phone_number').eq(phone_number),
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        transactions.extend(response.get('Items', []))
                    
                    logger.info(f"Queried all transactions using GSI: {len(transactions)} items")
                    
                except Exception as e:
                    logger.error(f"GSI query failed: {str(e)}, falling back to scan")
                    response = self.table.scan(
                        FilterExpression=Attr('phone_number').eq(phone_number)
                    )
                    transactions = response.get('Items', [])
            
            # Apply transaction type filter
            if query_params.get('transaction_type') is not None:
                transaction_type = query_params['transaction_type']
                transactions = [
                    t for t in transactions 
                    if t.get('transaction_type') == transaction_type
                ]
                logger.info(f"Filtered by transaction_type={transaction_type}: {len(transactions)} items")
            
            # Apply product filter
            products = query_params.get('products', [])
            if products:
                # Convert products to lowercase for case-insensitive matching
                products_lower = [p.lower() for p in products]
                transactions = [
                    t for t in transactions 
                    if t.get('product', '').lower() in products_lower
                ]
                logger.info(f"Filtered by products={products}: {len(transactions)} items")
            
            logger.info(f"Final result for {phone_number}: {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Error querying transactions for {phone_number}: {str(e)}")
            return []
    
    def summarize_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize transactions by product"""
        try:
            summary = {}
            total_cost = Decimal('0')
            
            for transaction in transactions:
                product = transaction.get('product', 'Desconocido')
                quantity = Decimal(str(transaction.get('quantity', 0)))
                quantity_units = transaction.get('quantity_units', 'piezas')
                cost = Decimal(str(transaction.get('cost', 0)))
                
                # Create product key
                product_key = product.lower()
                
                if product_key not in summary:
                    summary[product_key] = {
                        'product': product,
                        'total_quantity': Decimal('0'),
                        'quantity_units': quantity_units,
                        'total_cost': Decimal('0'),
                        'transaction_count': 0
                    }
                
                summary[product_key]['total_quantity'] += quantity
                summary[product_key]['total_cost'] += cost
                summary[product_key]['transaction_count'] += 1
                total_cost += cost
            
            return {
                'products': list(summary.values()),
                'total_cost': total_cost,
                'total_transactions': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Error summarizing transactions: {str(e)}")
            return {
                'products': [],
                'total_cost': Decimal('0'),
                'total_transactions': 0
            }
    
    def should_use_image(self, summary: Dict[str, Any]) -> bool:
        """Determine if report should be sent as image based on number of products"""
        try:
            product_count = len(summary.get('products', []))
            return product_count >= self.query_threshold and product_count < Config.EXCEL_THRESHOLD
        except Exception as e:
            logger.error(f"Error checking if should use image: {str(e)}")
            return False
    
    def should_use_excel(self, summary: Dict[str, Any]) -> bool:
        """Determine if report should be sent as Excel file based on number of products"""
        try:
            product_count = len(summary.get('products', []))
            return product_count >= Config.EXCEL_THRESHOLD
        except Exception as e:
            logger.error(f"Error checking if should use Excel: {str(e)}")
            return False
    
    def format_summary_text(self, summary: Dict[str, Any], query_params: Dict[str, Any], phone_number: str = None) -> str:
        """Format summary as text message"""
        try:
            # Header
            transaction_type_text = ""
            if query_params.get('transaction_type') == 1:
                transaction_type_text = "Ventas"
            elif query_params.get('transaction_type') == 0:
                transaction_type_text = "Compras"
            else:
                transaction_type_text = "Transacciones"
            
            # Group information
            group_text = ""
            if phone_number and Config.ENABLE_USER_GROUPS:
                user_group = self.user_group_repo.get_user_group(phone_number)
                if user_group and user_group.is_active and user_group.grouped_phone_numbers:
                    member_count = user_group.get_member_count()
                    if user_group.group_name:
                        group_text = f"\n👥 Grupo: {user_group.group_name} ({member_count} usuarios)"
                    else:
                        group_text = f"\n👥 {member_count} usuarios incluidos"
            
            # Date range
            date_text = ""
            if query_params.get('date_from') and query_params.get('date_to'):
                date_from = query_params['date_from']
                date_to = query_params['date_to']
                date_text = f"\n📅 Período: {date_from} al {date_to}"
            elif query_params.get('date_from'):
                date_text = f"\n📅 Desde: {query_params['date_from']}"
            elif query_params.get('date_to'):
                date_text = f"\n📅 Hasta: {query_params['date_to']}"
            
            # Products filter
            products_text = ""
            if query_params.get('products'):
                products_list = ", ".join(query_params['products'])
                products_text = f"\n🛍️ Productos: {products_list}"
            
            message = f"📊 **Reporte de {transaction_type_text}**{group_text}{date_text}{products_text}\n\n"
            
            # Products summary
            if summary['products']:
                message += "**Resumen por Producto:**\n\n"
                
                for product_data in summary['products']:
                    product = product_data['product']
                    quantity = float(product_data['total_quantity'])
                    units = product_data['quantity_units']
                    cost = float(product_data['total_cost'])
                    count = product_data['transaction_count']
                    
                    message += f"• **{product.title()}**\n"
                    message += f"  Cantidad: {quantity} {units}\n"
                    message += f"  Costo total: {cost:.2f}\n"
                    message += f"  Transacciones: {count}\n\n"
                
                # Total
                total_cost = float(summary['total_cost'])
                total_transactions = summary['total_transactions']
                
                message += f"**Total General:**\n"
                message += f"💰 Costo total: {total_cost:.2f}\n"
                message += f"📝 Total transacciones: {total_transactions}"
            else:
                message += "No se encontraron transacciones con los criterios especificados."
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting summary: {str(e)}")
            return "Error al generar el reporte."
