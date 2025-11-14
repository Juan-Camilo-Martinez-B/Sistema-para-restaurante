from django.http import HttpResponse
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from decimal import Decimal
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import pandas as pd
from .models import Pedido, ItemPedido


def generar_reporte_pdf_pedidos(request, fecha_inicio=None, fecha_fin=None):
    """Genera un reporte PDF de pedidos"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Pedidos", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Filtros de fecha
    if fecha_inicio and fecha_fin:
        pedidos = Pedido.objects.filter(
            fecha_creacion__date__gte=fecha_inicio,
            fecha_creacion__date__lte=fecha_fin
        ).exclude(estado='pendiente')
    else:
        pedidos = Pedido.objects.exclude(estado='pendiente')
    
    # Resumen
    total_pedidos = pedidos.count()
    total_ventas = pedidos.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    summary_data = [
        ['Total de Pedidos', str(total_pedidos)],
        ['Total de Ventas', f"${total_ventas}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de pedidos
    data = [['#', 'Cliente', 'Fecha', 'Estado', 'Total']]
    for pedido in pedidos[:50]:  # Limitar a 50 pedidos
        data.append([
            str(pedido.id),
            pedido.cliente.username,
            pedido.fecha_creacion.strftime('%d/%m/%Y'),
            pedido.get_estado_display(),
            f"${pedido.total}"
        ])
    
    table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_pedidos_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response


def generar_reporte_excel_pedidos(request, fecha_inicio=None, fecha_fin=None):
    """Genera un reporte Excel de pedidos"""
    # Filtros de fecha
    if fecha_inicio and fecha_fin:
        pedidos = Pedido.objects.filter(
            fecha_creacion__date__gte=fecha_inicio,
            fecha_creacion__date__lte=fecha_fin
        ).exclude(estado='pendiente')
    else:
        pedidos = Pedido.objects.exclude(estado='pendiente')
    
    # Preparar datos
    data = []
    for pedido in pedidos:
        data.append({
            'ID': pedido.id,
            'Cliente': pedido.cliente.username,
            'Fecha': pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'Estado': pedido.get_estado_display(),
            'Método de Pago': pedido.get_metodo_pago_display() or '-',
            'Subtotal': float(pedido.subtotal),
            'IVA': float(pedido.impuesto),
            'Total': float(pedido.total),
        })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Pedidos', index=False)
        
        # Agregar hoja de resumen
        resumen_data = {
            'Métrica': ['Total Pedidos', 'Total Ventas'],
            'Valor': [
                len(df),
                df['Total'].sum()
            ]
        }
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
    
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_pedidos_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response

