from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Mesa, Comanda, ItemComanda, PerfilGarzon
from menu.models import CategoriaMenu, ItemMenu
from .forms import MesaForm


# ── LAYOUT MESAS (pantalla táctil garzón) ──────────────────

@login_required
def layout_mesas(request):
    mesas = Mesa.objects.filter(activa=True).order_by('zona', 'numero')
    mesas_data = []
    for mesa in mesas:
        comanda = mesa.comanda_activa()
        mesas_data.append({
            'mesa': mesa,
            'comanda': comanda,
            'ocupada': comanda is not None,
        })
    zonas = {}
    for item in mesas_data:
        zona = item['mesa'].get_zona_display()
        if zona not in zonas:
            zonas[zona] = []
        zonas[zona].append(item)
    return render(request, 'comandas/layout_mesas.html', {
        'zonas': zonas,
        'total_mesas': mesas.count(),
        'mesas_ocupadas': sum(1 for m in mesas_data if m['ocupada']),
    })


@login_required
def mesa_detalle(request, mesa_id):
    mesa = get_object_or_404(Mesa, pk=mesa_id, activa=True)
    comanda_activa = mesa.comanda_activa()
    return render(request, 'comandas/mesa_detalle.html', {
        'mesa': mesa,
        'comanda': comanda_activa,
    })


@login_required
def comanda_nueva(request, mesa_id):
    mesa = get_object_or_404(Mesa, pk=mesa_id, activa=True)
    if mesa.tiene_comanda_activa():
        messages.warning(request, f'La Mesa {mesa.numero} ya tiene una comanda activa.')
        return redirect('comandas:comanda_detalle', comanda_id=mesa.comanda_activa().id)
    if request.method == 'POST':
        num_comensales = int(request.POST.get('num_comensales', 1))
        notas = request.POST.get('notas', '')
        comanda = Comanda.objects.create(
            mesa=mesa,
            garzon=request.user,
            num_comensales=num_comensales,
            notas=notas,
        )
        messages.success(request, f'Comanda abierta — Mesa {mesa.numero}')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)
    return render(request, 'comandas/comanda_nueva.html', {'mesa': mesa})


@login_required
def comanda_detalle(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    categorias = CategoriaMenu.objects.filter(activa=True).prefetch_related('items')
    cats_menu = []
    for cat in categorias:
        items = cat.items.filter(disponible=True)
        if items.exists():
            cats_menu.append({'categoria': cat, 'items': items})
    return render(request, 'comandas/comanda_detalle.html', {
        'comanda': comanda,
        'cats_menu': cats_menu,
        'estado_choices': Comanda.ESTADO_CHOICES,
    })


@login_required
@require_POST
def comanda_agregar_item(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    item_id = request.POST.get('item_id')
    cantidad = int(request.POST.get('cantidad', 1))
    notas = request.POST.get('notas', '')
    item_menu = get_object_or_404(ItemMenu, pk=item_id)
    ItemComanda.objects.create(
        comanda=comanda,
        item_menu=item_menu,
        nombre_item=item_menu.nombre,
        precio_unitario=item_menu.precio,
        cantidad=cantidad,
        notas=notas,
    )
    if comanda.estado == 'abierta':
        comanda.estado = 'en_proceso'
        comanda.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'total': str(comanda.get_total()),
            'total_items': comanda.get_total_items(),
        })
    messages.success(request, f'"{item_menu.nombre}" agregado.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda_id)


@login_required
@require_POST
def comanda_eliminar_item(request, comanda_id, item_id):
    item = get_object_or_404(ItemComanda, pk=item_id, comanda_id=comanda_id)
    nombre = item.nombre_item
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        comanda = get_object_or_404(Comanda, pk=comanda_id)
        return JsonResponse({'ok': True, 'total': str(comanda.get_total())})
    messages.success(request, f'"{nombre}" eliminado.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda_id)


@login_required
@require_POST
def comanda_cerrar(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    comanda.estado = 'cerrada'
    comanda.cerrada_at = timezone.now()
    comanda.save()
    messages.success(request, f'Comanda #{comanda.id} cerrada. Total: ${comanda.get_total()}')
    return redirect('comandas:layout_mesas')


@login_required
@require_POST
def comanda_cancelar(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    comanda.estado = 'cancelada'
    comanda.save()
    messages.warning(request, f'Comanda #{comanda.id} cancelada.')
    return redirect('comandas:layout_mesas')


# ── API TÁCTIL ──────────────────────────────────────────────

@login_required
@require_POST
def api_toggle_item(request, item_id):
    item = get_object_or_404(ItemComanda, pk=item_id)
    estados = ['pendiente', 'preparando', 'listo', 'entregado']
    idx = estados.index(item.estado)
    item.estado = estados[(idx + 1) % len(estados)]
    item.save()
    return JsonResponse({'ok': True, 'estado': item.estado, 'estado_display': item.get_estado_display()})


@login_required
@require_POST
def api_estado_comanda(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Comanda.ESTADO_CHOICES):
        comanda.estado = nuevo_estado
        if nuevo_estado == 'cerrada':
            comanda.cerrada_at = timezone.now()
        comanda.save()
    return JsonResponse({'ok': True, 'estado': comanda.estado})


# ── PANEL ADMIN COMANDAS ────────────────────────────────────

@staff_member_required
def panel_comandas(request):
    comandas_abiertas = Comanda.objects.filter(estado__in=['abierta', 'en_proceso']).select_related('mesa', 'garzon')
    comandas_hoy = Comanda.objects.filter(creada_at__date=timezone.now().date()).count()
    total_hoy = sum(c.get_total() for c in Comanda.objects.filter(
        creada_at__date=timezone.now().date(), estado='cerrada'))
    return render(request, 'comandas/panel/dashboard.html', {
        'comandas_abiertas': comandas_abiertas,
        'comandas_hoy': comandas_hoy,
        'total_hoy': total_hoy,
    })


@staff_member_required
def panel_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'comandas/panel/mesas.html', {'mesas': mesas})


@staff_member_required
def panel_mesa_crear(request):
    form = MesaForm(request.POST or None)
    if form.is_valid():
        mesa = form.save()
        messages.success(request, f'Mesa {mesa.numero} creada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/mesa_form.html', {'form': form, 'titulo': 'Nueva Mesa'})


@staff_member_required
def panel_mesa_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    form = MesaForm(request.POST or None, instance=mesa)
    if form.is_valid():
        form.save()
        messages.success(request, f'Mesa {mesa.numero} actualizada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/mesa_form.html', {
        'form': form, 'titulo': f'Editar Mesa {mesa.numero}'
    })


@staff_member_required
def panel_mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        numero = mesa.numero
        mesa.delete()
        messages.success(request, f'Mesa {numero} eliminada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/confirmar_eliminar.html', {'objeto': mesa, 'tipo': 'Mesa'})


@staff_member_required
def panel_garzones(request):
    from django.contrib.auth.models import User
    garzones = User.objects.filter(perfil_garzon__activo=True).select_related('perfil_garzon')
    return render(request, 'comandas/panel/garzones.html', {'garzones': garzones})


@staff_member_required
def panel_historial(request):
    garzon_id = request.GET.get('garzon', '')
    fecha = request.GET.get('fecha', '')
    from django.contrib.auth.models import User
    comandas = Comanda.objects.select_related('mesa', 'garzon').all()
    if garzon_id:
        comandas = comandas.filter(garzon_id=garzon_id)
    if fecha:
        comandas = comandas.filter(creada_at__date=fecha)
    garzones = User.objects.filter(comandas__isnull=False).distinct()
    return render(request, 'comandas/panel/historial.html', {
        'comandas': comandas,
        'garzones': garzones,
        'garzon_sel': garzon_id,
        'fecha_sel': fecha,
    })