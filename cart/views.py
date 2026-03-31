from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from catalog.models import Product
from .cart import Cart

MIN_ORDER_TOTAL = Decimal('10000')
IVA_RATE = Decimal('0.19')


def cart_detail(request):
    cart = Cart(request)
    cart_total = cart.get_total()
    iva_amount = (cart_total * IVA_RATE).quantize(Decimal('0.01'))
    total_with_tax = cart_total + iva_amount
    remaining_amount = max(MIN_ORDER_TOTAL - cart_total, Decimal('0'))
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'minimum_order': MIN_ORDER_TOTAL,
        'remaining_amount': remaining_amount,
        'iva_amount': iva_amount,
        'total_with_tax': total_with_tax,
    })


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    quantity = max(1, min(quantity, product.stock or 1))
    cart.add(product, quantity)
    messages.success(request, f'"{product.name}" agregado al carrito.')
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'"{product.name}" eliminado del carrito.')
    return redirect('cart:cart_detail')


def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    quantity = max(1, min(quantity, product.stock or 1))
    cart.update(product, quantity)
    return redirect('cart:cart_detail')
