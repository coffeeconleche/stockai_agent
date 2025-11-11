#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for Excel generation without full service dependencies
"""
import boto3
import pandas as pd
import io
from datetime import datetime
from decimal import Decimal

# AWS Configuration
AWS_PROFILE = 'diego_macbook_pro_kiro'
AWS_REGION = 'us-east-1'
S3_BUCKET = 'whatsapp-ai-agent-images'
S3_PREFIX = 'transaction-images/'

def test_excel_generation():
    """Test Excel report generation"""
    print("🧪 Testing Excel generation...")
    
    # Create test data
    test_data = []
    products = ['mani', 'azucar', 'cafe', 'arroz', 'frijol', 'papa', 
                'cebolla', 'tomate', 'zanahoria', 'lechuga', 'limon', 'naranja']
    
    for i, product in enumerate(products):
        test_data.append({
            'Producto': product.title(),
            'Cantidad Total': float(100 + i * 10),
            'Unidades': 'kg',
            'Costo Total (PEN)': float(200 + i * 50),
            'Número de Transacciones': 3 + i,
            'Costo Promedio': float((200 + i * 50) / (3 + i)),
        })
    
    # Create Excel in memory
    excel_buffer = io.BytesIO()
    
    # Get Lima timezone
    from pytz import timezone
    lima_tz = timezone('America/Lima')
    lima_time = datetime.now(lima_tz)
    generation_time = lima_time.strftime('%Y-%m-%d %H:%M:%S')
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([
            ['Tipo de Reporte', 'Ventas'],
            ['Período', '2025-01-01 al 2025-11-11'],
            ['', ''],
            ['TOTALES', ''],
            ['Costo Total', '5030.00 PEN'],
            ['Total Transacciones', '61'],
            ['Total Productos', str(len(products))],
            ['Fecha Generación', f"{generation_time} (Lima, UTC-5)"]
        ], columns=['Campo', 'Valor'])
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Detailed sheet
        detailed_df = pd.DataFrame(test_data)
        detailed_df = detailed_df.sort_values('Costo Total (PEN)', ascending=False)
        detailed_df.to_excel(writer, sheet_name='Detalle por Producto', index=False)
        
        # Top 10 sheet
        top10_df = detailed_df.head(10)
        top10_df.to_excel(writer, sheet_name='Top 10 Productos', index=False)
    
    excel_buffer.seek(0)
    
    print(f"✅ Excel file created in memory ({len(excel_buffer.getvalue())} bytes)")
    
    # Upload to S3
    try:
        session = boto3.Session(profile_name=AWS_PROFILE)
        s3_client = session.client('s3', region_name=AWS_REGION)
        
        # Use Lima timezone for filename
        timestamp = lima_time.strftime('%Y%m%d_%H%M')
        s3_key = f"{S3_PREFIX}reporte_transacciones_{timestamp}_stockai.xlsx"
        
        print(f"📤 Uploading to S3: s3://{S3_BUCKET}/{s3_key}")
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=excel_buffer.getvalue(),
            ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ContentDisposition='attachment; filename="reporte_transacciones.xlsx"'
        )
        
        print(f"✅ Upload successful!")
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=24 * 3600
        )
        
        print(f"\n📊 Excel Report Generated Successfully!")
        print(f"📄 Filename: {s3_key.split('/')[-1]}")
        print(f"📥 Download URL (valid for 24 hours):")
        print(f"{presigned_url}")
        print(f"\n💡 In WhatsApp, this will be sent as a document attachment")
        print(f"💡 Users can download it directly without seeing the long URL")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    try:
        success = test_excel_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
