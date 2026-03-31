from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from caja.models import AperturaCaja, PerfilCaja, TransaccionCaja
from config.security import sanitize_untrusted_text
from inventory.models import StockMovement
from orders.models import DispatchTask, Order, OrderNotification

from .models import (
    Payment,
    PaymentSequence,
    PaymentValidationLog,
    TreasuryAuthorizationSettings,
)

BANK_DETAILS = {
    'bank': 'Banco de Chile',
    'account_type': 'Cuenta Corriente',
    'account_number': '001-98765432',
    'holder': 'Boccato di Cardinale SpA',
    'rut': '76.456.321-9',
    'email': 'pagos@boccato.cl',
}


def require_treasurer(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        try:
            perfil = request.user.perfil_caja
            if perfil.rol != 'tesorero' and not request.user.is_superuser:
                messages.error(request, 'Solo el tesorero puede validar transferencias de tienda.')
                return redirect('caja:dashboard')
        except PerfilCaja.DoesNotExist:
            if not request.user.is_superuser:
                messages.error(request, 'Acceso denegado.')
                return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_active_cash_opening():
    return AperturaCaja.objects.filter(
        estado='autorizada',
        cierre__isnull=True,
    ).order_by('-autorizada_at').first()


def _get_payment_or_none(order):
    try:
        return order.payment
    except Payment.DoesNotExist:
        return None


def _get_dispatch_user():
    dispatch_group = Group.objects.filter(name__iexact='despacho').first()
    if dispatch_group:
        user = dispatch_group.user_set.filter(is_active=True).order_by('id').first()
        if user:
            return user
    return User.objects.filter(is_staff=True, is_active=True).exclude(is_superuser=True).order_by('id').first()


def _log_validation(payment, action, actor=None, code='', detail=''):
    PaymentValidationLog.objects.create(
        payment=payment,
        action=action,
        actor=actor,
        code=code,
        detail=detail,
    )


def _notify_order(order, recipient_type, subject, message_text, recipient_user=None, recipient_email=''):
    notification = OrderNotification.objects.create(
        order=order,
        recipient_type=recipient_type,
        channel='system',
        recipient_user=recipient_user,
        recipient_email=recipient_email,
        subject=subject,
        message=message_text,
        sent_at=timezone.now(),
    )
    email_target = recipient_email or getattr(recipient_user, 'email', '')
    if email_target:
        send_mail(
            subject,
            message_text,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@boccato.cl'),
            [email_target],
            fail_silently=True,
        )
        OrderNotification.objects.create(
            order=order,
            recipient_type=recipient_type,
            channel='email',
            recipient_user=recipient_user,
            recipient_email=email_target,
            subject=subject,
            message=message_text,
            sent_at=timezone.now(),
        )
    return notification


def _register_order_movements(order, payment):
    for item in order.items.select_related('product'):
        if item.product:
            StockMovement.objects.create(
                product=item.product,
                movement_type='out',
                quantity=item.quantity,
                reason=f'Venta ecommerce orden #{order.id} autorizada por tesoreria.',
                authorized_by=payment.approved_by,
            )

    TransaccionCaja.registrar(
        tipo='transferencia',
        usuario=payment.user,
        autorizador=payment.approved_by,
        monto=payment.amount,
        descripcion=(
            f'Transferencia tienda autorizada. Orden #{order.id}. '
            f'Boleta {payment.treasury_number_display or "sin numero"} '
            f'| Ref: {payment.reference or "sin referencia"}'
        ),
        referencia_id=payment.id,
        referencia_modelo='Payment',
        apertura=_get_active_cash_opening(),
    )


def _create_dispatch_task(order, payment):
    dispatch_user = _get_dispatch_user()
    task, _ = DispatchTask.objects.get_or_create(order=order)
    task.assigned_to = dispatch_user
    task.status = 'assigned'
    task.delivery_method = order.delivery_method or 'internal'
    task.estimated_delivery_minutes = order.estimated_delivery_minutes or 30
    task.notes = (
        f'Pedido aprobado por tesoreria. Boleta {payment.treasury_number_display}. '
        f'Folio {order.folio}. Preparar despacho y confirmar entrega.'
    )
    task.save()
    return task


@login_required
def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    existing_payment = _get_payment_or_none(order)

    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, f'La orden #{order.id} ya fue aprobada por tesoreria.')
        return redirect('payments:payment_success', order_id=order.id)

    if request.method == 'POST':
        reference = sanitize_untrusted_text(request.POST.get('reference', ''), max_length=120)
        if not reference:
            messages.error(request, 'Debes ingresar el numero o comprobante de transferencia.')
            return render(request, 'payments/payment_process.html', {
                'order': order,
                'bank_details': BANK_DETAILS,
                'payment': existing_payment,
            })

        with transaction.atomic():
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'method': 'transfer',
                    'status': 'pending',
                    'amount': order.get_grand_total(),
                }
            )
            payment.user = request.user
            payment.method = 'transfer'
            payment.status = 'pending'
            payment.amount = order.get_grand_total()
            payment.reference = reference
            payment.rejection_number = None
            payment.approved_by = None
            payment.review_notes = ''
            payment.confirmed_at = None
            payment.submitted_at = timezone.now()
            payment.save()
            _log_validation(
                payment,
                'submitted',
                actor=request.user,
                detail=f'Transferencia informada para orden #{order.id}. Ref: {reference}',
            )

        messages.success(
            request,
            f'Transferencia informada para la orden #{order.id}. Queda pendiente de validacion del tesorero.'
        )
        return redirect('orders:order_detail', pk=order.id)

    return render(request, 'payments/payment_process.html', {
        'order': order,
        'bank_details': BANK_DETAILS,
        'payment': existing_payment,
    })


@require_treasurer
def treasury_security(request):
    security_settings = TreasuryAuthorizationSettings.get_solo()
    if request.method == 'POST':
        new_code = sanitize_untrusted_text(request.POST.get('new_code', ''), max_length=32)
        confirm_code = sanitize_untrusted_text(request.POST.get('confirm_code', ''), max_length=32)
        if len(new_code) < 6:
            messages.error(request, 'La clave de aprobacion debe tener al menos 6 caracteres.')
        elif new_code != confirm_code:
            messages.error(request, 'La confirmacion de la clave no coincide.')
        else:
            security_settings.set_code(new_code, updated_by=request.user)
            messages.success(request, 'La clave de aprobacion tesoreria fue actualizada.')
            return redirect('payments:treasury_security')

    return render(request, 'payments/treasury_security.html', {
        'security_settings': security_settings,
    })


@require_treasurer
def payment_authorize(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related('order', 'user'),
        pk=payment_id,
        method='transfer',
        status='pending',
    )
    security_settings = TreasuryAuthorizationSettings.get_solo()

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = sanitize_untrusted_text(request.POST.get('review_notes', ''), max_length=400)
        approval_code = sanitize_untrusted_text(request.POST.get('approval_code', ''), max_length=32)

        if not security_settings.has_code:
            messages.error(request, 'Debes configurar primero la clave de aprobacion de tesoreria.')
            return redirect('payments:treasury_security')
        if not security_settings.verify_code(approval_code):
            messages.error(request, 'Clave de aprobacion incorrecta.')
            return render(request, 'payments/payment_authorize.html', {
                'payment': payment,
                'order': payment.order,
                'security_settings': security_settings,
            })

        with transaction.atomic():
            if action == 'approve':
                if not payment.treasury_number:
                    payment.treasury_number = PaymentSequence.next_number()
                payment.status = 'completed'
                payment.approved_by = request.user
                payment.review_notes = notes
                payment.confirmed_at = timezone.now()
                payment.amount = payment.order.get_grand_total()
                payment.save()

                payment.order.paid = True
                payment.order.status = 'processing'
                payment.order.delivery_method = payment.order.delivery_method or 'internal'
                payment.order.estimated_delivery_minutes = payment.order.estimated_delivery_minutes or 30
                payment.order.save(
                    update_fields=['paid', 'status', 'delivery_method', 'estimated_delivery_minutes', 'updated_at']
                )

                _register_order_movements(payment.order, payment)
                dispatch_task = _create_dispatch_task(payment.order, payment)

                dispatch_message = (
                    f'Orden #{payment.order.id} aprobada por tesoreria. '
                    f'Boleta {payment.treasury_number_display}. '
                    f'Folio {payment.order.folio}. '
                    f'Ingresar al detalle del pedido y procesar despacho.'
                )
                customer_message = (
                    f'Pago aprobado para tu orden #{payment.order.id}. '
                    f'Boleta {payment.treasury_number_display}. '
                    f'Proxima entrega estimada entre 15 y 30 minutos.'
                )
                _notify_order(
                    payment.order,
                    'dispatch',
                    f'Nueva orden lista para despacho #{payment.order.id}',
                    dispatch_message,
                    recipient_user=dispatch_task.assigned_to,
                )
                _notify_order(
                    payment.order,
                    'customer',
                    f'Pago aprobado orden #{payment.order.id}',
                    customer_message,
                    recipient_user=payment.user,
                    recipient_email=payment.user.email,
                )
                payment.dispatch_notified_at = timezone.now()
                payment.customer_notified_at = timezone.now()
                payment.save(update_fields=['dispatch_notified_at', 'customer_notified_at'])

                _log_validation(
                    payment,
                    'approved',
                    actor=request.user,
                    code=payment.treasury_number_display,
                    detail=notes or 'Pago aprobado y boleta emitida.',
                )
                _log_validation(
                    payment,
                    'dispatch_notified',
                    actor=request.user,
                    code=payment.treasury_number_display,
                    detail=dispatch_message,
                )
                _log_validation(
                    payment,
                    'customer_notified',
                    actor=request.user,
                    code=payment.treasury_number_display,
                    detail=customer_message,
                )
                messages.success(
                    request,
                    f'Transferencia autorizada con boleta {payment.treasury_number_display}.'
                )
            elif action == 'reject':
                if not payment.rejection_number:
                    payment.rejection_number = PaymentSequence.next_rejection_number()
                payment.status = 'failed'
                payment.approved_by = request.user
                payment.review_notes = notes
                payment.confirmed_at = timezone.now()
                payment.save()

                rejection_message = (
                    f'Tu pago por la orden #{payment.order.id} fue rechazado. '
                    f'Codigo {payment.rejection_code_display}. '
                    f'Por favor revisa el comprobante y vuelve a informar la transferencia.'
                )
                _notify_order(
                    payment.order,
                    'customer',
                    f'Pago rechazado orden #{payment.order.id}',
                    rejection_message,
                    recipient_user=payment.user,
                    recipient_email=payment.user.email,
                )
                payment.customer_notified_at = timezone.now()
                payment.save(update_fields=['customer_notified_at'])

                _log_validation(
                    payment,
                    'rejected',
                    actor=request.user,
                    code=payment.rejection_code_display,
                    detail=notes or 'Pago rechazado por tesoreria.',
                )
                _log_validation(
                    payment,
                    'customer_notified',
                    actor=request.user,
                    code=payment.rejection_code_display,
                    detail=rejection_message,
                )
                messages.warning(
                    request,
                    f'Transferencia rechazada con codigo {payment.rejection_code_display}.'
                )

        return redirect('caja:tesorero_dashboard')

    return render(request, 'payments/payment_authorize.html', {
        'payment': payment,
        'order': payment.order,
        'security_settings': security_settings,
    })


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/payment_success.html', {
        'order': order,
        'payment': _get_payment_or_none(order),
    })


@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.warning(request, 'Pago cancelado.')
    return redirect('orders:order_detail', pk=order.id)
