# -*- coding: utf-8 -*-
"""
Image generation service for transaction responses
"""
import boto3
from PIL import Image, ImageDraw, ImageFont
import io
import logging
from typing import Dict, Any, List
from datetime import datetime
from src.config import Config

# Ensure proper UTF-8 encoding for Spanish characters
import sys
if sys.version_info[0] >= 3:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logger = logging.getLogger(__name__)

class ImageService:
    """Service for generating transaction table images"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
        self.bucket_name = Config.S3_BUCKET_NAME
        
        # Image dimensions (3:4 ratio for mobile)
        self.width = 900
        self.height = 1200
        
        # Colors for transaction tables (Blue theme)
        self.bg_color = (255, 255, 255)  # White
        self.header_color = (41, 128, 185)  # Blue
        self.text_color = (44, 62, 80)  # Dark gray
        self.border_color = (189, 195, 199)  # Light gray
        self.alt_row_color = (236, 240, 241)  # Very light gray
        
        # Colors for report tables (Green theme)
        self.report_header_color = (39, 174, 96)  # Green
        self.report_alt_row_color = (232, 246, 236)  # Very light green
    
    def generate_transaction_image(self, transactions: List[Dict[str, Any]]) -> str:
        """Generate a table image for transactions and upload to S3"""
        try:
            # Create image
            img = Image.new('RGB', (self.width, self.height), self.bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font with proper Unicode support, fallback to default
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
                cell_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                cell_font = ImageFont.load_default()
            
            # Draw title
            title = "✅ Transacciones Registradas"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((self.width - title_width) // 2, 40), title, fill=self.header_color, font=title_font)
            
            # Table starting position
            table_y = 120
            margin = 30
            table_width = self.width - (2 * margin)
            
            # Column widths (proportional) - more compact
            col_widths = [140, 220, 140, 140, 140]  # Tipo, Producto, Cantidad, Costo, Perecedero
            
            # Draw header row
            header_height = 55
            draw.rectangle(
                [(margin, table_y), (margin + table_width, table_y + header_height)],
                fill=self.header_color
            )
            
            headers = ["Tipo", "Producto", "Cantidad", "Costo", "Perecedero"]
            x_pos = margin
            for i, header in enumerate(headers):
                # Center text in cell
                text_bbox = draw.textbbox((0, 0), header, font=header_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x_pos + (col_widths[i] - text_width) // 2
                draw.text((text_x, table_y + 12), header, fill=(255, 255, 255), font=header_font)
                
                # Draw vertical line
                if i < len(headers) - 1:
                    draw.line([(x_pos + col_widths[i], table_y), 
                              (x_pos + col_widths[i], table_y + header_height)], 
                             fill=(255, 255, 255), width=2)
                
                x_pos += col_widths[i]
            
            # Draw data rows
            row_height = 70
            current_y = table_y + header_height
            
            for idx, transaction in enumerate(transactions):
                # Alternate row colors
                row_color = self.alt_row_color if idx % 2 == 0 else self.bg_color
                
                draw.rectangle(
                    [(margin, current_y), (margin + table_width, current_y + row_height)],
                    fill=row_color,
                    outline=self.border_color,
                    width=1
                )
                
                # Prepare data with proper UTF-8 encoding
                tipo = "Venta" if transaction.get('transaction_type') == 1 else "Compra"
                producto = str(transaction.get('product', ''))
                if transaction.get('product_variation'):
                    producto += f"\n({str(transaction.get('product_variation'))})"
                
                cantidad = f"{transaction.get('quantity', 0)} {str(transaction.get('quantity_units', ''))}"
                costo = f"{transaction.get('cost', 0)} {str(transaction.get('currency', 'PEN'))}"
                # Use Unicode character for "Sí" to ensure proper rendering
                perecedero = "Sí" if transaction.get('is_perishable') == 1 else "No"
                
                row_data = [tipo, producto, cantidad, costo, perecedero]
                
                # Draw cells
                x_pos = margin
                for i, data in enumerate(row_data):
                    # Wrap text if too long
                    lines = self._wrap_text(data, col_widths[i] - 15, cell_font, draw)
                    
                    # Draw text (centered horizontally, top-aligned vertically)
                    y_offset = current_y + 10
                    for line in lines:
                        text_bbox = draw.textbbox((0, 0), line, font=cell_font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_x = x_pos + (col_widths[i] - text_width) // 2
                        draw.text((text_x, y_offset), line, fill=self.text_color, font=cell_font)
                        y_offset += 30
                    
                    # Draw vertical line
                    if i < len(row_data) - 1:
                        draw.line([(x_pos + col_widths[i], current_y), 
                                  (x_pos + col_widths[i], current_y + row_height)], 
                                 fill=self.border_color, width=1)
                    
                    x_pos += col_widths[i]
                
                current_y += row_height
            
            # Draw footer
            footer_y = current_y + 30
            footer_text = f"📊 Total: {len(transactions)} transacción{'es' if len(transactions) > 1 else ''}"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=cell_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            draw.text(((self.width - footer_width) // 2, footer_y), footer_text, fill=self.text_color, font=cell_font)
            
            # Save to bytes with proper encoding
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG', optimize=True, quality=95)
            img_byte_arr.seek(0)
            
            # Upload to S3
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
            s3_key = f"{Config.S3_IMAGES_PREFIX}{timestamp}.png"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=img_byte_arr.getvalue(),
                ContentType='image/png',
                #ACL='public-read'
            )

            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=24 * 3600  # seconds
            )
            
            # # Generate public URL
            # image_url = f"https://{self.bucket_name}.s3.{Config.AWS_REGION}.amazonaws.com/{s3_key}"
            
            # logger.info(f"Generated transaction image: {image_url}")
            # return image_url

            logger.info(f"Generated transaction image (presigned): {presigned_url}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating transaction image: {str(e)}")
            return None
    
    def generate_report_image(self, summary: Dict[str, Any], query_params: Dict[str, Any]) -> str:
        """Generate a report table image and upload to S3"""
        try:
            products = summary.get('products', [])
            if not products:
                return None
            
            # Create image
            img = Image.new('RGB', (self.width, self.height), self.bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font with proper Unicode support
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
                cell_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                cell_font = ImageFont.load_default()
                footer_font = ImageFont.load_default()
            
            # Draw title
            transaction_type_text = ""
            if query_params.get('transaction_type') == 1:
                transaction_type_text = "Ventas"
            elif query_params.get('transaction_type') == 0:
                transaction_type_text = "Compras"
            else:
                transaction_type_text = "Transacciones"
            
            title = f"📊 Reporte de {transaction_type_text}"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((self.width - title_width) // 2, 40), title, fill=self.report_header_color, font=title_font)
            
            # Draw date range if specified
            current_y = 110
            if query_params.get('date_from') or query_params.get('date_to'):
                date_text = ""
                if query_params.get('date_from') and query_params.get('date_to'):
                    date_text = f"📅 {query_params['date_from']} al {query_params['date_to']}"
                elif query_params.get('date_from'):
                    date_text = f"📅 Desde: {query_params['date_from']}"
                elif query_params.get('date_to'):
                    date_text = f"📅 Hasta: {query_params['date_to']}"
                
                date_bbox = draw.textbbox((0, 0), date_text, font=cell_font)
                date_width = date_bbox[2] - date_bbox[0]
                draw.text(((self.width - date_width) // 2, current_y), date_text, fill=self.text_color, font=cell_font)
                current_y += 50
            
            # Table starting position
            table_y = current_y + 10
            margin = 30
            table_width = self.width - (2 * margin)
            
            # Column widths for report: Producto, Cantidad, Costo Total, # Trans
            col_widths = [280, 200, 200, 160]
            
            # Draw header row
            header_height = 55
            draw.rectangle(
                [(margin, table_y), (margin + table_width, table_y + header_height)],
                fill=self.report_header_color
            )
            
            headers = ["Producto", "Cantidad", "Costo Total", "# Trans"]
            x_pos = margin
            for i, header in enumerate(headers):
                text_bbox = draw.textbbox((0, 0), header, font=header_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x_pos + (col_widths[i] - text_width) // 2
                draw.text((text_x, table_y + 12), header, fill=(255, 255, 255), font=header_font)
                
                if i < len(headers) - 1:
                    draw.line([(x_pos + col_widths[i], table_y), 
                              (x_pos + col_widths[i], table_y + header_height)], 
                             fill=(255, 255, 255), width=2)
                
                x_pos += col_widths[i]
            
            # Draw data rows
            row_height = 70
            current_y = table_y + header_height
            
            for idx, product_data in enumerate(products):
                row_color = self.report_alt_row_color if idx % 2 == 0 else self.bg_color
                
                draw.rectangle(
                    [(margin, current_y), (margin + table_width, current_y + row_height)],
                    fill=row_color,
                    outline=self.border_color,
                    width=1
                )
                
                # Prepare data
                producto = str(product_data['product']).title()
                quantity = float(product_data['total_quantity'])
                units = str(product_data['quantity_units'])
                cantidad = f"{quantity} {units}"
                cost = float(product_data['total_cost'])
                costo = f"{cost:.2f} PEN"
                trans_count = str(product_data['transaction_count'])
                
                row_data = [producto, cantidad, costo, trans_count]
                
                # Draw cells
                x_pos = margin
                for i, data in enumerate(row_data):
                    lines = self._wrap_text(data, col_widths[i] - 15, cell_font, draw)
                    
                    y_offset = current_y + 10
                    for line in lines:
                        text_bbox = draw.textbbox((0, 0), line, font=cell_font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_x = x_pos + (col_widths[i] - text_width) // 2
                        draw.text((text_x, y_offset), line, fill=self.text_color, font=cell_font)
                        y_offset += 30
                    
                    if i < len(row_data) - 1:
                        draw.line([(x_pos + col_widths[i], current_y), 
                                  (x_pos + col_widths[i], current_y + row_height)], 
                                 fill=self.border_color, width=1)
                    
                    x_pos += col_widths[i]
                
                current_y += row_height
            
            # Draw footer with totals
            footer_y = current_y + 30
            total_cost = float(summary['total_cost'])
            total_transactions = summary['total_transactions']
            
            footer_text = f"💰 Total: {total_cost:.2f} PEN  |  📝 {total_transactions} transacción{'es' if total_transactions != 1 else ''}"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            draw.text(((self.width - footer_width) // 2, footer_y), footer_text, fill=self.report_header_color, font=footer_font)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG', optimize=True, quality=95)
            img_byte_arr.seek(0)
            
            # Upload to S3
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
            s3_key = f"{Config.S3_IMAGES_PREFIX}report_{timestamp}.png"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=img_byte_arr.getvalue(),
                ContentType='image/png'
            )
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=24 * 3600
            )
            
            logger.info(f"Generated report image (presigned): {presigned_url}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating report image: {str(e)}")
            return None
    
    def _wrap_text(self, text: str, max_width: int, font, draw) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
