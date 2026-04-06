from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from caja.models import PerfilCaja
from config.invoicing import (
    BUSINESS_LEGAL_NAME,
    BUSINESS_RUT,
    INVOICING_CONTACT_EMAIL,
    INVOICING_CONTACT_WHATSAPP,
    SII_ELECTRONIC_INVOICE_URL,
    SII_ELECTRONIC_RECEIPT_URL,
    SII_FEE_RECEIPT_URL,
    build_invoicing_mailto,
)
from orders.models import Order

from .forms import ContactForm


def _can_manage_billing(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.perfil_caja.rol == 'tesorero' and user.perfil_caja.activo
    except PerfilCaja.DoesNotExist:
        return False


def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mensaje enviado. Te responderemos pronto.')
        return redirect('contact:contact')
    return render(request, 'contact/contact.html', {'form': form})


def billing_hub(request):
    if not _can_manage_billing(request.user):
        messages.error(request, 'Acceso restringido a administracion y tesoreria.')
        return redirect('/')

    order = None
    order_id = request.GET.get('order')
    if order_id:
        order = get_object_or_404(Order, pk=order_id)

    return render(request, 'contact/billing_hub.html', {
        'billing_mailto_url': build_invoicing_mailto(order),
        'billing_order': order,
        'business_legal_name': BUSINESS_LEGAL_NAME,
        'business_rut': BUSINESS_RUT,
        'invoicing_contact_email': INVOICING_CONTACT_EMAIL,
        'invoicing_contact_whatsapp': INVOICING_CONTACT_WHATSAPP,
        'sii_electronic_invoice_url': SII_ELECTRONIC_INVOICE_URL,
        'sii_electronic_receipt_url': SII_ELECTRONIC_RECEIPT_URL,
        'sii_fee_receipt_url': SII_FEE_RECEIPT_URL,
    })
