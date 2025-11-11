import io
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_invoice_pdf_buffer(factura_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Factura N°: {factura_data['id']}", styles['h1']))
    story.append(Spacer(1, 0.2*inch))

    header_data = [
        [Paragraph("<b>Fecha:</b>", styles['Normal']), Paragraph(factura_data['fecha'].strftime('%d/%m/%Y %H:%M'), styles['Normal'])],
        [Paragraph("<b>Generado por:</b>", styles['Normal']), Paragraph(factura_data['creador']['username'], styles['Normal'])],
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
    header_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Datos del Cliente", styles['h2']))
    cliente_info = f"""
    <b>Nombre:</b> {factura_data['cliente']['nombre']} {factura_data['cliente']['apellido']}<br/>
    <b>DNI:</b> {factura_data['cliente']['dni']}<br/>
    <b>Dirección:</b> {factura_data['cliente']['direccion'] or 'N/A'}<br/>
    <b>Teléfono:</b> {factura_data['cliente']['telefono'] or 'N/A'}
    """
    story.append(Paragraph(cliente_info, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Detalle de la Compra", styles['h2']))
    table_data = [
        ["Producto", "Cantidad", "Precio Unit.", "Importe"]
    ]
    total_factura = Decimal('0.0')

    for item in factura_data['detalle']:
        precio_unit = Decimal(item['precio'])
        cantidad = item['cantidad']
        importe = precio_unit * cantidad
        total_factura += importe
        table_data.append([
            item['nombre'],
            str(cantidad),
            f"${precio_unit:,.2f}",
            f"${importe:,.2f}"
        ])

    table_data.append(["", "", Paragraph("<b>TOTAL</b>", styles['h4']), Paragraph(f"<b>${total_factura:,.2f}</b>", styles['h4'])])
    
    detalle_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.2*inch])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-2), colors.beige),
        ('GRID', (0,0), (-1,-2), 1, colors.black),
        ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ])
    detalle_table.setStyle(style)
    story.append(detalle_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer