import os
from urllib.parse import quote


SII_ELECTRONIC_INVOICE_URL = os.getenv(
    'SII_ELECTRONIC_INVOICE_URL',
    'https://www.sii.cl/destacados/factura_electronica/factura_etapas_2.html',
)
SII_ELECTRONIC_RECEIPT_URL = os.getenv(
    'SII_ELECTRONIC_RECEIPT_URL',
    'https://www.sii.cl/preguntas_frecuentes/bol_electr_vtas_serv/arbol_faqs_bol_electr_vtas_serv_2288.htm',
)
SII_FEE_RECEIPT_URL = os.getenv(
    'SII_FEE_RECEIPT_URL',
    'https://www.sii.cl/pagina/intermedia/bhe/pag_intermedia01.htm',
)

INVOICING_CONTACT_EMAIL = os.getenv('INVOICING_CONTACT_EMAIL', 'facturacion@boccato.cl')
INVOICING_CONTACT_WHATSAPP = os.getenv('INVOICING_CONTACT_WHATSAPP', '')
BUSINESS_LEGAL_NAME = os.getenv('BUSINESS_LEGAL_NAME', 'Boccato di Cardinale SpA')
BUSINESS_RUT = os.getenv('BUSINESS_RUT', '76.456.321-9')


def build_invoicing_mailto(order=None):
    subject = f'Solicitud de documento tributario - {BUSINESS_LEGAL_NAME}'
    lines = [
        'Hola equipo de facturacion,',
        '',
        'Necesito solicitar la emision de un documento tributario electronico.',
        '',
        'Tipo de documento:',
        '- [ ] Boleta electronica',
        '- [ ] Factura electronica',
        '- [ ] Boleta de honorarios',
        '',
        'Datos del solicitante:',
        '- Nombre o razon social:',
        '- RUT:',
        '- Giro:',
        '- Correo de contacto:',
        '',
    ]

    if order is not None:
        lines.extend([
            'Referencia del pedido:',
            f'- Orden: #{order.id}',
            f'- Folio interno: {order.folio}',
            f'- Cliente: {order.customer_full_name}',
            f'- Email: {order.customer_email or "No informado"}',
            f'- Total estimado: ${order.get_grand_total():,.0f}',
            '',
        ])

    lines.extend([
        'Adjunto respaldo si aplica.',
        '',
        'Gracias.',
    ])

    return f'mailto:{INVOICING_CONTACT_EMAIL}?subject={quote(subject)}&body={quote(chr(10).join(lines))}'
