from decimal import Decimal
from django.conf import settings

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomerProfile
from cart.cart import Cart
from config.commerce import (
    SECTOR_CHOICES,
    STORE_ORIGIN_ADDRESS,
    STORE_ORIGIN_LAT,
    STORE_ORIGIN_LNG,
    ZONE_CHOICES,
    get_sector_distance_km,
)
from config.security import sanitize_untrusted_text
from payments.models import PaymentValidationLog

from .models import DispatchTask, Order, OrderItem
from .ticket import generate_ticket

MIN_ORDER_TOTAL = Decimal('10000')


def _get_order_payment(order):
    try:
        return order.payment
    except Exception:
        return None


def _can_manage_dispatch(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__iexact='despacho').exists()


def require_dispatch(view_func):
    def wrapper(request, *args, **kwargs):
        if not _can_manage_dispatch(request.user):
            messages.error(request, 'No tienes acceso al panel de despacho.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _checkout_context(cart, items, profile=None, form_data=None, fresh_checkout=False):
    zone = ''
    sector = ''
    shipping_address = ''
    notes = ''
    delivery_method = 'internal'
    delivery_distance_km = ''
    destination_latitude = ''
    destination_longitude = ''
    if profile and form_data:
        zone = profile.zone
        sector = profile.sector
        shipping_address = profile.default_address
    if form_data:
        zone = form_data.get('zone', zone)
        sector = form_data.get('sector', sector)
        shipping_address = form_data.get('shipping_address', shipping_address)
        notes = form_data.get('notes', '')
        delivery_method = form_data.get('delivery_method', delivery_method)
        delivery_distance_km = form_data.get('delivery_distance_km', delivery_distance_km)
        destination_latitude = form_data.get('destination_latitude', '')
        destination_longitude = form_data.get('destination_longitude', '')

    preview = Order(
        zone=zone,
        sector=sector,
        delivery_method=delivery_method,
        delivery_distance_km=Decimal(str(delivery_distance_km or '0')),
    )
    for item in items:
        preview.items_cache = True
    preview.get_total = lambda: cart.get_total()
    preview.get_net_total = lambda: cart.get_total()
    preview.get_tax_amount = lambda: (cart.get_total() * Decimal('0.19')).quantize(Decimal('0.01'))
    preview.get_delivery_fee = preview.calculate_delivery_fee
    preview.get_total_with_tax = lambda: preview.get_net_total() + preview.get_tax_amount()
    preview.get_grand_total = lambda: preview.get_total_with_tax() + preview.get_delivery_fee()
    approximate_distance = Decimal(str(delivery_distance_km or '0'))
    if not approximate_distance and sector:
        approximate_distance = get_sector_distance_km(sector)

    return {
        'cart': cart,
        'items': items,
        'minimum_order': MIN_ORDER_TOTAL,
        'zone_choices': ZONE_CHOICES,
        'sector_choices': SECTOR_CHOICES,
        'zone': zone,
        'sector': sector,
        'shipping_address': shipping_address,
        'notes': notes,
        'delivery_method': delivery_method,
        'delivery_distance_km': delivery_distance_km,
        'destination_latitude': destination_latitude,
        'destination_longitude': destination_longitude,
        'preview': preview,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'store_origin_address': STORE_ORIGIN_ADDRESS,
        'store_origin_lat': STORE_ORIGIN_LAT,
        'store_origin_lng': STORE_ORIGIN_LNG,
        'fresh_checkout': fresh_checkout,
        'approximate_distance_km': approximate_distance,
    }


@login_required
def order_create(request):
    cart = Cart(request)
    items = cart.get_items()
    if not items:
        messages.warning(request, 'Tu carrito esta vacio.')
        return redirect('cart:cart_detail')

    cart_total = cart.get_total()
    remaining_amount = max(MIN_ORDER_TOTAL - cart_total, Decimal('0'))
    if cart_total < MIN_ORDER_TOTAL:
        messages.warning(
            request,
            f'El pedido minimo para despacho es de ${MIN_ORDER_TOTAL:.0f}. '
            f'Te faltan ${remaining_amount:.0f}.'
        )
        return redirect('cart:cart_detail')

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return render(
            request,
            'orders/order_checkout.html',
            _checkout_context(cart, items, profile=profile, fresh_checkout=True),
        )

    shipping_address = sanitize_untrusted_text(request.POST.get('shipping_address', ''), max_length=500)
    notes = sanitize_untrusted_text(request.POST.get('notes', ''), max_length=500)
    zone = request.POST.get('zone', '').strip()
    sector = request.POST.get('sector', '').strip()
    delivery_method = request.POST.get('delivery_method', 'internal').strip()
    distance_raw = request.POST.get('delivery_distance_km', '0').strip()
    destination_latitude_raw = request.POST.get('destination_latitude', '').strip()
    destination_longitude_raw = request.POST.get('destination_longitude', '').strip()

    try:
        delivery_distance_km = Decimal(distance_raw or '0')
    except Exception:
        delivery_distance_km = Decimal('0')
    try:
        destination_latitude = Decimal(destination_latitude_raw) if destination_latitude_raw else None
    except Exception:
        destination_latitude = None
    try:
        destination_longitude = Decimal(destination_longitude_raw) if destination_longitude_raw else None
    except Exception:
        destination_longitude = None

    form_data = {
        'zone': zone,
        'sector': sector,
        'shipping_address': shipping_address,
        'notes': notes,
        'delivery_method': delivery_method,
        'delivery_distance_km': str(delivery_distance_km),
        'destination_latitude': destination_latitude_raw,
        'destination_longitude': destination_longitude_raw,
    }

    if not shipping_address:
        messages.error(request, 'Debes ingresar una direccion de entrega.')
        return render(request, 'orders/order_checkout.html', _checkout_context(cart, items, profile=profile, form_data=form_data))

    if zone not in dict(ZONE_CHOICES) or sector not in dict(SECTOR_CHOICES):
        messages.error(request, 'Debes seleccionar zona y sector para el analisis de pedidos.')
        return render(request, 'orders/order_checkout.html', _checkout_context(cart, items, profile=profile, form_data=form_data))

    if delivery_method not in dict(Order.DELIVERY_METHOD_CHOICES):
        messages.error(request, 'Debes seleccionar el tipo de despacho.')
        return render(request, 'orders/order_checkout.html', _checkout_context(cart, items, profile=profile, form_data=form_data))

    if delivery_distance_km <= 0 and sector:
        delivery_distance_km = get_sector_distance_km(sector)
        form_data['delivery_distance_km'] = str(delivery_distance_km)

    insufficient_stock = []
    for item in items:
        if item['product'].stock < item['quantity']:
            insufficient_stock.append(
                f'{item["product"].name} (stock disponible: {item["product"].stock})'
            )

    if insufficient_stock:
        messages.error(request, 'No hay stock suficiente para: ' + ', '.join(insufficient_stock))
        return redirect('cart:cart_detail')

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            notes=notes,
            zone=zone,
            sector=sector,
            delivery_method=delivery_method,
            delivery_distance_km=delivery_distance_km,
            destination_latitude=destination_latitude,
            destination_longitude=destination_longitude,
            estimated_delivery_minutes=30,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price,
            )
        order.delivery_fee = order.calculate_delivery_fee()
        order.save(update_fields=['delivery_fee', 'updated_at'])

        profile.zone = zone
        profile.sector = sector
        profile.default_address = shipping_address
        profile.save()

    cart.clear()
    messages.success(request, f'Orden #{order.id} creada. Confirma ahora la transferencia.')
    return redirect('payments:payment_process', order_id=order.id)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    payment = _get_order_payment(order)
    logs = payment.validation_logs.all()[:8] if payment else []
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'payment': payment,
        'notifications': order.notifications.all()[:6],
        'validation_logs': logs,
        'dispatch_task': getattr(order, 'dispatch_task', None),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'store_origin_address': STORE_ORIGIN_ADDRESS,
        'store_origin_lat': STORE_ORIGIN_LAT,
        'store_origin_lng': STORE_ORIGIN_LNG,
    })


@login_required
def order_list(request):
    orders = []
    for order in Order.objects.filter(user=request.user):
        orders.append({
            'instance': order,
            'payment': _get_order_payment(order),
        })
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_ticket(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return generate_ticket(order)


@require_dispatch
def dispatch_dashboard(request):
    tasks = DispatchTask.objects.select_related('order__user', 'assigned_to', 'order__payment').order_by('-created_at')
    return render(request, 'orders/dispatch_dashboard.html', {'tasks': tasks})


@require_dispatch
def dispatch_order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    payment = _get_order_payment(order)
    dispatch_task, _ = DispatchTask.objects.get_or_create(order=order)

    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method', '')
        estimated_minutes = request.POST.get('estimated_delivery_minutes', '30')
        dispatch_notes = sanitize_untrusted_text(request.POST.get('dispatch_notes', ''), max_length=400)
        if delivery_method not in {'internal', 'external'}:
            messages.error(request, 'Debes seleccionar el tipo de entrega.')
        else:
            try:
                estimated_minutes = int(estimated_minutes)
            except ValueError:
                estimated_minutes = 30
            estimated_minutes = max(15, min(30, estimated_minutes))

            dispatch_task.assigned_to = request.user
            dispatch_task.delivery_method = delivery_method
            dispatch_task.estimated_delivery_minutes = estimated_minutes
            dispatch_task.notes = dispatch_notes
            dispatch_task.status = 'out_for_delivery'
            dispatch_task.save()

            order.delivery_method = delivery_method
            order.estimated_delivery_minutes = estimated_minutes
            order.dispatch_notes = dispatch_notes
            order.delivery_fee = order.calculate_delivery_fee()
            order.status = 'shipped'
            order.save(update_fields=[
                'delivery_method', 'estimated_delivery_minutes', 'dispatch_notes', 'delivery_fee', 'status', 'updated_at'
            ])

            if payment:
                PaymentValidationLog.objects.create(
                    payment=payment,
                    action='dispatch_updated',
                    actor=request.user,
                    detail=(
                        f'Despacho actualizado. Metodo: {order.get_delivery_method_display()}. '
                        f'ETA: {estimated_minutes} min. {dispatch_notes}'.strip()
                    ),
                )

            messages.success(request, 'Orden enviada a entrega.')
            return redirect('orders:dispatch_dashboard')

    return render(request, 'orders/dispatch_detail.html', {
        'order': order,
        'payment': payment,
        'dispatch_task': dispatch_task,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'store_origin_address': STORE_ORIGIN_ADDRESS,
        'store_origin_lat': STORE_ORIGIN_LAT,
        'store_origin_lng': STORE_ORIGIN_LNG,
    })
