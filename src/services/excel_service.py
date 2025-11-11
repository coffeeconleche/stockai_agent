# -*- coding: utf-8 -*-
"""
Excel generation service for transaction reports
"""
import boto3
import pandas as pd
import io
import logging
from typing import Dict, Any, List
from datetime import datetime
from src.config import Config

logger = logging.getLogger(__name__)

class ExcelService:
    """Service for generating Excel reports"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
        self.bucket_name = Config.S3_BUCKET_NAME
    
    def generate_report_excel(self, summary: Dict[str, Any], query_params: Dict[str, Any], phone_number: str = None) -> tuple:
        """Generate Excel report and upload to S3"""
        try:
            products = summary.get('products', [])
            if not products:
                return None
            
            # Create Excel workbook with multiple sheets
            excel_buffer = io.BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Sheet 1: Summary Report
                self._create_summary_sheet(writer, summary, query_params, phone_number)
                
                # Sheet 2: Detailed Data
                self._create_detailed_sheet(writer, products)
                
                # Sheet 3: Charts Data (for manual chart creation)
                self._create_charts_data_sheet(writer, products)
            
            excel_buffer.seek(0)
            
            # Upload to S3 with Lima timezone in filename
            from pytz import timezone
            lima_tz = timezone('America/Lima')
            lima_time = datetime.now(lima_tz)
            timestamp = lima_time.strftime('%Y%m%d_%H%M')
            s3_key = f"{Config.S3_IMAGES_PREFIX}reporte_transacciones_{timestamp}_stockai.xlsx"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=excel_buffer.getvalue(),
                ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                ContentDisposition='attachment; filename="reporte_transacciones.xlsx"'
            )
            
            # Generate presigned URL (valid for 24 hours)
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=24 * 3600
            )
            
            # Extract filename from s3_key
            filename = s3_key.split('/')[-1]
            
            logger.info(f"Generated Excel report: {presigned_url}")
            return presigned_url, filename
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}")
            return None, None
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, summary: Dict[str, Any], query_params: Dict[str, Any], phone_number: str = None):
        """Create summary sheet with report information"""
        try:
            # Prepare summary data
            summary_data = []
            
            # Header information
            transaction_type_text = ""
            if query_params.get('transaction_type') == 1:
                transaction_type_text = "Ventas"
            elif query_params.get('transaction_type') == 0:
                transaction_type_text = "Compras"
            else:
                transaction_type_text = "Transacciones"
            
            summary_data.append(['Tipo de Reporte', transaction_type_text])
            
            # Group information
            if phone_number and Config.ENABLE_USER_GROUPS:
                from src.models import UserGroupRepository
                user_group_repo = UserGroupRepository()
                user_group = user_group_repo.get_user_group(phone_number)
                
                if user_group and user_group.is_active and user_group.grouped_phone_numbers:
                    member_count = user_group.get_member_count()
                    if user_group.group_name:
                        summary_data.append(['Grupo', f"{user_group.group_name} ({member_count} usuarios)"])
                    else:
                        summary_data.append(['Grupo', f"{member_count} usuarios incluidos"])
            
            # Date range
            if query_params.get('date_from') and query_params.get('date_to'):
                summary_data.append(['Período', f"{query_params['date_from']} al {query_params['date_to']}"])
            elif query_params.get('date_from'):
                summary_data.append(['Desde', query_params['date_from']])
            elif query_params.get('date_to'):
                summary_data.append(['Hasta', query_params['date_to']])
            
            # Products filter
            if query_params.get('products'):
                products_list = ", ".join(query_params['products'])
                summary_data.append(['Productos Filtrados', products_list])
            
            # Totals
            total_cost = float(summary['total_cost'])
            total_transactions = summary['total_transactions']
            total_products = len(summary['products'])
            
            # Get Lima timezone for generation timestamp
            from pytz import timezone
            lima_tz = timezone('America/Lima')
            lima_time = datetime.now(lima_tz)
            generation_time = lima_time.strftime('%Y-%m-%d %H:%M:%S')
            
            summary_data.extend([
                ['', ''],  # Empty row
                ['TOTALES', ''],
                ['Costo Total', f"{total_cost:.2f} PEN"],
                ['Total Transacciones', total_transactions],
                ['Total Productos', total_products],
                ['Fecha Generación', f"{generation_time} (Lima, UTC-5)"]
            ])
            
            # Create DataFrame and write to Excel
            summary_df = pd.DataFrame(summary_data, columns=['Campo', 'Valor'])
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Format the summary sheet
            workbook = writer.book
            worksheet = writer.sheets['Resumen']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
        except Exception as e:
            logger.error(f"Error creating summary sheet: {str(e)}")
    
    def _create_detailed_sheet(self, writer: pd.ExcelWriter, products: List[Dict[str, Any]]):
        """Create detailed products sheet"""
        try:
            # Prepare detailed data
            detailed_data = []
            
            for product_data in products:
                detailed_data.append({
                    'Producto': product_data['product'].title(),
                    'Cantidad Total': float(product_data['total_quantity']),
                    'Unidades': product_data['quantity_units'],
                    'Costo Total (PEN)': float(product_data['total_cost']),
                    'Número de Transacciones': product_data['transaction_count'],
                    'Costo Promedio por Transacción': float(product_data['total_cost']) / product_data['transaction_count'],
                    'Cantidad Promedio por Transacción': float(product_data['total_quantity']) / product_data['transaction_count']
                })
            
            # Create DataFrame
            detailed_df = pd.DataFrame(detailed_data)
            
            # Sort by total cost (descending)
            detailed_df = detailed_df.sort_values('Costo Total (PEN)', ascending=False)
            
            # Write to Excel
            detailed_df.to_excel(writer, sheet_name='Detalle por Producto', index=False)
            
            # Format the detailed sheet
            worksheet = writer.sheets['Detalle por Producto']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format currency columns
            from openpyxl.styles import NamedStyle
            currency_style = NamedStyle(name='currency', number_format='#,##0.00')
            
            for row in range(2, len(detailed_data) + 2):  # Skip header
                worksheet[f'D{row}'].style = currency_style  # Costo Total
                worksheet[f'F{row}'].style = currency_style  # Costo Promedio
            
        except Exception as e:
            logger.error(f"Error creating detailed sheet: {str(e)}")
    
    def _create_charts_data_sheet(self, writer: pd.ExcelWriter, products: List[Dict[str, Any]]):
        """Create charts data sheet for visualization"""
        try:
            # Top 10 products by cost
            top_products = sorted(products, key=lambda x: float(x['total_cost']), reverse=True)[:10]
            
            chart_data = []
            for product_data in top_products:
                chart_data.append({
                    'Producto': product_data['product'].title(),
                    'Costo Total': float(product_data['total_cost']),
                    'Cantidad Total': float(product_data['total_quantity']),
                    'Transacciones': product_data['transaction_count']
                })
            
            # Create DataFrame
            chart_df = pd.DataFrame(chart_data)
            
            # Write to Excel
            chart_df.to_excel(writer, sheet_name='Top 10 Productos', index=False)
            
            # Format the charts sheet
            worksheet = writer.sheets['Top 10 Productos']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 25)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
        except Exception as e:
            logger.error(f"Error creating charts data sheet: {str(e)}")
