from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from catalog.models import Product
from .models import StockMovement
from .forms import StockMovementForm


@staff_member_required
def inventory_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'inventory/inventory_list.html', {'products': products})


@staff_member_required
def stock_movement(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    movements = StockMovement.objects.filter(product=product)
    form = StockMovementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        movement = form.save(commit=False)
        movement.product = product
        movement.authorized_by = request.user
        movement.save()
        messages.success(request, 'Movimiento de stock registrado.')
        return redirect('inventory:inventory_list')
    return render(request, 'inventory/stock_movement.html', {
        'product': product,
        'movements': movements,
        'form': form,
    })