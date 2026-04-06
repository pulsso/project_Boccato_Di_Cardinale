from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from django.http import HttpResponse


def build_ticket_pdf(order):
    try:
        payment = order.payment
    except Exception:
        payment = None
    is_approved = bool(payment and payment.status == 'completed')
    is_rejected = bool(payment and payment.status == 'failed')
    tax_multiplier = Decimal('1.19')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    title = 'Nota de Venta' if is_approved else 'Pedido Pendiente'
    if is_approved:
        payment_state = 'Aprobado por tesorero'
    elif is_rejected:
        payment_state = 'Transferencia rechazada'
    else:
        payment_state = 'Pendiente de validacion'

    elements.append(Paragraph('Boccato di Cardinale', styles['Title']))
    elements.append(Paragraph(title, styles['Heading2']))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph(f'Folio pedido: {order.folio}', styles['Normal']))
    elements.append(Paragraph(f'Fecha: {order.created_at.strftime("%d/%m/%Y")}', styles['Normal']))
    elements.append(Paragraph(f'Hora: {order.created_at.strftime("%H:%M")}', styles['Normal']))
    elements.append(Paragraph(f'Cliente: {order.customer_full_name}', styles['Normal']))
    if order.customer_email:
        elements.append(Paragraph(f'Email: {order.customer_email}', styles['Normal']))
    if order.customer_mobile_phone:
        elements.append(Paragraph(f'Celular: {order.customer_mobile_phone}', styles['Normal']))
    if order.customer_landline_phone:
        elements.append(Paragraph(f'Telefono fijo: {order.customer_landline_phone}', styles['Normal']))
    elements.append(Paragraph(f'Direccion: {order.shipping_address or "No especificada"}', styles['Normal']))
    elements.append(Paragraph(f'Pago: {payment_state}', styles['Normal']))
    if payment and payment.treasury_number_display:
        elements.append(Paragraph(f'Boleta: {payment.treasury_number_display}', styles['Normal']))
    if payment and payment.rejection_code_display:
        elements.append(Paragraph(f'Codigo rechazo: {payment.rejection_code_display}', styles['Normal']))
    if payment and payment.reference:
        elements.append(Paragraph(f'Referencia transferencia: {payment.reference}', styles['Normal']))
    if order.delivery_method:
        elements.append(Paragraph(f'Despacho: {order.get_delivery_method_display()}', styles['Normal']))
    if order.estimated_delivery_minutes:
        elements.append(Paragraph(f'Tiempo estimado: {order.estimated_delivery_minutes} min', styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    header_price = 'Valor + IVA' if is_approved else 'Valor neto'
    data = [['Producto', 'Cantidad', header_price, 'Subtotal']]
    for item in order.items.all():
        unit_price = item.price * tax_multiplier if is_approved else item.price
        subtotal = item.subtotal() * tax_multiplier if is_approved else item.subtotal()
        product_name = item.product.name if item.product else 'Producto eliminado'
        data.append([
            product_name,
            str(item.quantity),
            f'${unit_price:,.0f}',
            f'${subtotal:,.0f}',
        ])

    data.append(['', '', 'NETO', f'${order.get_net_total():,.0f}'])
    data.append(['', '', 'IVA 19%', f'${order.get_tax_amount():,.0f}'])
    data.append(['', '', 'DESPACHO', f'${order.get_delivery_fee():,.0f}'])
    if is_approved:
        data.append(['', '', 'TOTAL', f'${order.get_grand_total():,.0f}'])
    else:
        data.append(['', '', 'TOTAL EST.', f'${order.get_grand_total():,.0f}'])

    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E1E2E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F0F0F0')]),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f'Impreso Boccato di Cardinale - {order.created_at.strftime("%d/%m/%Y %H:%M")}', styles['Normal']))

    doc.build(elements)
    return buffer.getvalue()


def generate_ticket(order):
    pdf_bytes = build_ticket_pdf(order)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="pedido_boccato_{order.id}.pdf"'
    response.write(pdf_bytes)
    return response
