from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from caja.models import Pago as PagoCaja, PerfilCaja
from menu.models import CategoriaMenu, ItemMenu

from .forms import MesaForm, OperatorSwitchForm
from .models import Comanda, ItemComanda, Mesa, PerfilGarzon

SESSION_OPERATOR_KEY = 'comandas_operador_id'


def _waiter_profile(user):
    if not user.is_authenticated:
        return None
    try:
        return user.perfil_garzon
    except PerfilGarzon.DoesNotExist:
        return None


def _cash_profile(user):
    if not user.is_authenticated:
        return None
    try:
        return user.perfil_caja
    except PerfilCaja.DoesNotExist:
        return None


def _is_active_waiter(user):
    profile = _waiter_profile(user)
    return bool(user.is_authenticated and (user.is_superuser or user.is_staff or (profile and profile.activo)))


def _can_review_orders(user):
    cash_profile = _cash_profile(user)
    return bool(user.is_authenticated and (user.is_superuser or user.is_staff or (cash_profile and cash_profile.activo)))


def _is_layout_admin(user):
    return bool(user.is_authenticated and user.is_superuser)


def _shared_terminal_user(request):
    return bool(request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff))


def _effective_operator_user(request):
    if not request.user.is_authenticated:
        return request.user
    if not _shared_terminal_user(request):
        return request.user

    operator_id = request.session.get(SESSION_OPERATOR_KEY)
    if not operator_id:
        return request.user

    try:
        return User.objects.get(pk=operator_id, perfil_garzon__activo=True)
    except User.DoesNotExist:
        request.session.pop(SESSION_OPERATOR_KEY, None)
        return request.user


def _effective_operator_profile(request):
    operator = _effective_operator_user(request)
    return _waiter_profile(operator)


def requiere_comandas(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_active_waiter(request.user):
            messages.error(request, 'Solo garzones activos o administracion pueden operar comandas.')
            return redirect('/')
        return view_func(request, *args, **kwargs)

    return wrapper


def requiere_revision_comandas(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _can_review_orders(request.user):
            messages.error(request, 'No tienes permisos para revisar comandas.')
            return redirect('/')
        return view_func(request, *args, **kwargs)

    return wrapper


def requiere_admin_layout(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_layout_admin(request.user):
            messages.error(request, 'Solo el administrador puede modificar zonas, mesas y asignaciones.')
            return redirect('comandas:panel_comandas')
        return view_func(request, *args, **kwargs)

    return wrapper


def _period_range(period):
    today = timezone.localdate()
    if period == 'weekly':
        return today - timedelta(days=6), today
    if period == 'monthly':
        return today - timedelta(days=29), today
    return today, today


def _comandas_periodo(period):
    start_date, end_date = _period_range(period)
    queryset = Comanda.objects.filter(
        fecha_operacion__gte=start_date,
        fecha_operacion__lte=end_date,
    ).select_related('mesa', 'garzon')
    return queryset, start_date, end_date


def _resolve_mesas_for_waiter(request):
    user = _effective_operator_user(request)
    mesas = Mesa.objects.filter(activa=True).select_related('garzon_asignado').order_by('zona', 'numero')
    if _shared_terminal_user(request) and user == request.user:
        return mesas

    assigned = mesas.filter(garzon_asignado=user)
    if assigned.exists():
        return assigned
    return mesas.filter(Q(garzon_asignado=user) | Q(garzon_asignado__isnull=True))


def _garzon_display(user):
    if not user:
        return 'Sin garzon'
    full_name = user.get_full_name().strip()
    return full_name or user.username


def _sales_total(queryset):
    return sum(comanda.get_total_with_tax() for comanda in queryset if comanda.estado == 'cerrada')


@requiere_comandas
def layout_mesas(request):
    mesas = _resolve_mesas_for_waiter(request)
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
        zonas.setdefault(zona, []).append(item)

    operator_user = _effective_operator_user(request)
    waiter_profile = _waiter_profile(operator_user)
    assigned_count = Mesa.objects.filter(activa=True, garzon_asignado=operator_user).count()
    return render(request, 'comandas/layout_mesas.html', {
        'zonas': zonas,
        'total_mesas': mesas.count(),
        'mesas_ocupadas': sum(1 for m in mesas_data if m['ocupada']),
        'assigned_count': assigned_count,
        'zona_asignada': getattr(waiter_profile, 'zona_asignada', ''),
        'can_view_dashboard': _can_review_orders(request.user),
        'operator_user': operator_user,
        'operator_profile': waiter_profile,
        'shared_terminal_mode': _shared_terminal_user(request),
        'operator_form': OperatorSwitchForm(),
    })


@requiere_comandas
def mesa_detalle(request, mesa_id):
    operator_user = _effective_operator_user(request)
    mesa = get_object_or_404(Mesa.objects.select_related('garzon_asignado'), pk=mesa_id, activa=True)
    if not _shared_terminal_user(request) and mesa.garzon_asignado and mesa.garzon_asignado != operator_user:
        messages.error(request, 'Esta mesa esta asignada a otro garzon.')
        return redirect('comandas:layout_mesas')

    comanda_activa = mesa.comanda_activa()
    ultimas_comandas = mesa.comandas.select_related('garzon').order_by('-creada_at')[:5]
    return render(request, 'comandas/mesa_detalle.html', {
        'mesa': mesa,
        'comanda': comanda_activa,
        'ultimas_comandas': ultimas_comandas,
    })


@requiere_comandas
def comanda_nueva(request, mesa_id):
    operator_user = _effective_operator_user(request)
    mesa = get_object_or_404(Mesa.objects.select_related('garzon_asignado'), pk=mesa_id, activa=True)
    if not _shared_terminal_user(request) and mesa.garzon_asignado and mesa.garzon_asignado != operator_user:
        messages.error(request, 'Esta mesa esta asignada a otro garzon.')
        return redirect('comandas:layout_mesas')
    if mesa.tiene_comanda_activa():
        messages.warning(request, f'La mesa {mesa.numero} ya tiene una comanda activa.')
        return redirect('comandas:comanda_detalle', comanda_id=mesa.comanda_activa().id)

    if request.method == 'POST':
        num_comensales = max(1, int(request.POST.get('num_comensales', 1)))
        notas = request.POST.get('notas', '').strip()
        comanda = Comanda.objects.create(
            mesa=mesa,
            garzon=operator_user,
            num_comensales=num_comensales,
            notas=notas,
        )
        messages.success(request, f'Comanda {comanda.folio} abierta en mesa {mesa.numero}.')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)

    return render(request, 'comandas/comanda_nueva.html', {'mesa': mesa})


def comanda_detalle(request, comanda_id):
    operator_user = _effective_operator_user(request)
    comanda = get_object_or_404(
        Comanda.objects.select_related('mesa', 'garzon', 'mesa__garzon_asignado').prefetch_related('items'),
        pk=comanda_id,
    )

    if not (_is_active_waiter(request.user) or _can_review_orders(request.user)):
        messages.error(request, 'No tienes acceso a esta comanda.')
        return redirect('/')

    if _is_active_waiter(request.user) and not _shared_terminal_user(request):
        if comanda.garzon_id != operator_user.id and comanda.mesa.garzon_asignado_id not in {None, operator_user.id}:
            messages.error(request, 'No tienes acceso operativo a esta comanda.')
            return redirect('comandas:layout_mesas')

    categorias = CategoriaMenu.objects.filter(activa=True).prefetch_related('items').order_by('tipo', 'orden', 'nombre')
    cats_menu = []
    for categoria in categorias:
        items = categoria.items.filter(disponible=True).order_by('orden', 'nombre')
        if items.exists():
            cats_menu.append({'categoria': categoria, 'items': items})

    pago = getattr(comanda, 'pago', None)
    garzon_profile = _waiter_profile(comanda.garzon) if comanda.garzon else None
    return render(request, 'comandas/comandas_detalle.html', {
        'comanda': comanda,
        'cats_menu': cats_menu,
        'suggested_tip': comanda.get_suggested_tip(),
        'pago': pago,
        'can_edit_order': _is_active_waiter(request.user),
        'can_review_order': _can_review_orders(request.user),
        'garzon_profile': garzon_profile,
        'operator_user': operator_user,
        'operator_profile': _effective_operator_profile(request),
        'shared_terminal_mode': _shared_terminal_user(request),
        'operator_form': OperatorSwitchForm(),
    })


@require_POST
@requiere_comandas
def comanda_agregar_item(request, comanda_id):
    operator_user = _effective_operator_user(request)
    comanda = get_object_or_404(Comanda.objects.select_related('mesa'), pk=comanda_id)
    pago = getattr(comanda, 'pago', None)
    if pago and pago.estado == 'aprobado':
        messages.error(request, 'No puedes agregar items a una comanda ya pagada.')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)
    if comanda.estado == 'cancelada':
        messages.error(request, 'No puedes agregar items a una comanda cancelada.')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)

    item_menu = get_object_or_404(ItemMenu, pk=request.POST.get('item_id'), disponible=True)
    cantidad = max(1, int(request.POST.get('cantidad', 1)))
    notas = request.POST.get('notas', '').strip()
    unit_price = item_menu.precio_oferta if item_menu.tiene_oferta and item_menu.precio_oferta else item_menu.precio

    ItemComanda.objects.create(
        comanda=comanda,
        item_menu=item_menu,
        agregado_por=operator_user,
        nombre_item=item_menu.nombre,
        precio_unitario=unit_price,
        cantidad=cantidad,
        notas=notas,
    )

    if comanda.estado in {'abierta', 'cerrada', 'lista'}:
        comanda.estado = 'en_proceso'
        comanda.cerrada_at = None
        comanda.save(update_fields=['estado', 'cerrada_at', 'actualizada_at'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'total': str(comanda.get_total_with_tax()), 'folio': comanda.folio})

    messages.success(request, f'"{item_menu.nombre}" agregado a la comanda {comanda.folio}.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda.id)


@require_POST
@requiere_comandas
def comanda_eliminar_item(request, comanda_id, item_id):
    item = get_object_or_404(ItemComanda, pk=item_id, comanda_id=comanda_id)
    nombre = item.nombre_item
    item.delete()
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'total': str(comanda.get_total_with_tax())})
    messages.success(request, f'"{nombre}" eliminado.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda_id)


@require_POST
@requiere_comandas
def comanda_cerrar(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    comanda.estado = 'cerrada'
    comanda.cerrada_at = timezone.now()
    comanda.save(update_fields=['estado', 'cerrada_at', 'actualizada_at'])
    messages.success(request, f'Comanda {comanda.folio} cerrada. Pasa a proceso de pago.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda.id)


@require_POST
@requiere_comandas
def comanda_reabrir(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    pago = getattr(comanda, 'pago', None)
    if pago and pago.estado == 'aprobado':
        messages.error(request, 'No puedes reabrir una comanda ya pagada.')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)
    comanda.estado = 'en_proceso'
    comanda.cerrada_at = None
    comanda.save(update_fields=['estado', 'cerrada_at', 'actualizada_at'])
    messages.success(request, f'Comanda {comanda.folio} reabierta para corregir o agregar consumo.')
    return redirect('comandas:comanda_detalle', comanda_id=comanda.id)


@require_POST
@requiere_comandas
def comanda_cancelar(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    pago = getattr(comanda, 'pago', None)
    if pago and pago.estado == 'aprobado':
        messages.error(request, 'No puedes cancelar una comanda ya pagada.')
        return redirect('comandas:comanda_detalle', comanda_id=comanda.id)
    comanda.estado = 'cancelada'
    comanda.save(update_fields=['estado', 'actualizada_at'])
    messages.warning(request, f'Comanda {comanda.folio} cancelada.')
    return redirect('comandas:layout_mesas')


@require_POST
def api_toggle_item(request, item_id):
    if not (_is_active_waiter(request.user) or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'ok': False}, status=403)
    item = get_object_or_404(ItemComanda.objects.select_related('comanda'), pk=item_id)
    item.advance_status()
    comanda = item.comanda
    item_states = list(comanda.items.values_list('estado', flat=True))
    if item_states and all(state in {'listo', 'entregado'} for state in item_states):
        comanda.estado = 'lista'
    elif any(state in {'preparando', 'listo', 'entregado'} for state in item_states):
        comanda.estado = 'en_proceso'
    comanda.save(update_fields=['estado', 'actualizada_at'])
    return JsonResponse({'ok': True, 'estado': item.estado, 'estado_display': item.get_estado_display()})


@require_POST
def api_estado_comanda(request, comanda_id):
    if not (_is_active_waiter(request.user) or _can_review_orders(request.user)):
        return JsonResponse({'ok': False}, status=403)
    comanda = get_object_or_404(Comanda, pk=comanda_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Comanda.ESTADO_CHOICES):
        comanda.estado = nuevo_estado
        if nuevo_estado == 'cerrada':
            comanda.cerrada_at = timezone.now()
        elif nuevo_estado != 'cerrada':
            comanda.cerrada_at = None
        comanda.save(update_fields=['estado', 'cerrada_at', 'actualizada_at'])
    return JsonResponse({'ok': True, 'estado': comanda.estado})


@requiere_revision_comandas
def kitchen_dashboard(request):
    comandas_activas = Comanda.objects.filter(
        estado__in=['abierta', 'en_proceso', 'lista', 'cerrada']
    ).select_related('mesa', 'garzon').prefetch_related('items').order_by('creada_at')
    items_kitchen = ItemComanda.objects.filter(
        comanda__estado__in=['abierta', 'en_proceso', 'lista'],
        estado__in=['pendiente', 'preparando', 'listo'],
    ).select_related('comanda__mesa', 'comanda__garzon').order_by('creado_at')
    return render(request, 'comandas/kitchen_dashboard.html', {
        'comandas_activas': comandas_activas,
        'items_kitchen': items_kitchen,
        'pending_items': items_kitchen.filter(estado='pendiente').count(),
        'preparing_items': items_kitchen.filter(estado='preparando').count(),
        'ready_items': items_kitchen.filter(estado='listo').count(),
    })


@requiere_revision_comandas
def panel_comandas(request):
    period = request.GET.get('period', 'daily')
    comandas_periodo, start_date, end_date = _comandas_periodo(period)
    comandas_abiertas = Comanda.objects.filter(
        estado__in=['abierta', 'en_proceso', 'lista', 'cerrada']
    ).select_related('mesa', 'garzon').order_by('-creada_at')

    desempeno_garzones = []
    agrupadas_garzones = comandas_periodo.values(
        'garzon__id', 'garzon__username', 'garzon__first_name', 'garzon__last_name'
    ).annotate(total=Count('id')).order_by('-total')
    for row in agrupadas_garzones:
        related = comandas_periodo.filter(garzon__id=row['garzon__id'])
        desempeno_garzones.append({
            'garzon': (
                f"{row['garzon__first_name']} {row['garzon__last_name']}".strip()
                or row['garzon__username']
                or 'Sin garzon'
            ),
            'comandas': row['total'],
            'ventas': _sales_total(related),
        })

    rendimiento_mesas = []
    agrupadas_mesas = comandas_periodo.values('mesa__id', 'mesa__numero', 'mesa__zona').annotate(total=Count('id')).order_by('-total')
    for row in agrupadas_mesas:
        related = comandas_periodo.filter(mesa__id=row['mesa__id'])
        rendimiento_mesas.append({
            'mesa': row['mesa__numero'],
            'zona': dict(Mesa.ZONA_CHOICES).get(row['mesa__zona'], row['mesa__zona']),
            'comandas': row['total'],
            'ventas': _sales_total(related),
        })

    return render(request, 'comandas/panel/dashboard.html', {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'comandas_abiertas': comandas_abiertas[:30],
        'comandas_periodo': comandas_periodo[:30],
        'comandas_hoy': Comanda.objects.filter(fecha_operacion=timezone.localdate()).count(),
        'total_hoy': _sales_total(Comanda.objects.filter(fecha_operacion=timezone.localdate())),
        'desempeno_garzones': desempeno_garzones,
        'rendimiento_mesas': rendimiento_mesas,
        'mesas_configuradas': Mesa.objects.filter(activa=True).count(),
        'mesas_sin_asignar': Mesa.objects.filter(activa=True, garzon_asignado__isnull=True).count(),
        'can_manage_layout': _is_layout_admin(request.user),
    })


@requiere_revision_comandas
def panel_mesas(request):
    mesas = Mesa.objects.select_related('garzon_asignado').all().order_by('zona', 'numero')
    zonas = {}
    for mesa in mesas:
        zonas.setdefault(mesa.get_zona_display(), []).append(mesa)
    return render(request, 'comandas/panel/mesas.html', {
        'mesas': mesas,
        'zonas': zonas,
        'can_manage_layout': _is_layout_admin(request.user),
    })


@requiere_admin_layout
def panel_mesa_crear(request):
    form = MesaForm(request.POST or None)
    if form.is_valid():
        mesa = form.save()
        messages.success(request, f'Mesa {mesa.numero} creada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/mesa_form.html', {'form': form, 'titulo': 'Nueva mesa'})


@requiere_admin_layout
def panel_mesa_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    form = MesaForm(request.POST or None, instance=mesa)
    if form.is_valid():
        form.save()
        messages.success(request, f'Mesa {mesa.numero} actualizada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/mesa_form.html', {'form': form, 'titulo': f'Editar mesa {mesa.numero}'})


@requiere_admin_layout
def panel_mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        numero = mesa.numero
        mesa.delete()
        messages.success(request, f'Mesa {numero} eliminada.')
        return redirect('comandas:panel_mesas')
    return render(request, 'comandas/panel/confirmar_eliminar.html', {'objeto': mesa, 'tipo': 'Mesa'})


@requiere_revision_comandas
def panel_garzones(request):
    period = request.GET.get('period', 'daily')
    comandas_periodo, start_date, end_date = _comandas_periodo(period)
    garzones = PerfilGarzon.objects.select_related('usuario').filter(activo=True).order_by('zona_asignada', 'usuario__username')
    garzon_rows = []

    for perfil in garzones:
        usuario = perfil.usuario
        mesas_asignadas = list(Mesa.objects.filter(activa=True, garzon_asignado=usuario).order_by('zona', 'numero'))
        comandas_usuario = comandas_periodo.filter(garzon=usuario)
        abiertas = Comanda.objects.filter(garzon=usuario, estado__in=['abierta', 'en_proceso', 'lista', 'cerrada']).count()
        garzon_rows.append({
            'perfil': perfil,
            'usuario': usuario,
            'nombre': _garzon_display(usuario),
            'zona': perfil.get_zona_asignada_display() if perfil.zona_asignada else 'Sin zona fija',
            'mesas_asignadas': mesas_asignadas,
            'mesas_count': len(mesas_asignadas),
            'comandas_periodo': comandas_usuario.count(),
            'ventas_periodo': _sales_total(comandas_usuario),
            'abiertas': abiertas,
            'sobrecupo': len(mesas_asignadas) > 5 and perfil.zona_asignada != 'barra',
        })

    bartender_rows = [row for row in garzon_rows if row['perfil'].zona_asignada == 'barra']
    return render(request, 'comandas/panel/garzones.html', {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'garzon_rows': garzon_rows,
        'bartender_rows': bartender_rows,
        'can_manage_layout': _is_layout_admin(request.user),
    })


@require_POST
@requiere_comandas
def seleccionar_operador(request):
    if not _shared_terminal_user(request):
        messages.info(request, 'Tu sesion ya identifica al operador actual.')
        return redirect(request.POST.get('next') or 'comandas:layout_mesas')

    form = OperatorSwitchForm(request.POST)
    if form.is_valid():
        perfil = form.cleaned_data['perfil']
        request.session[SESSION_OPERATOR_KEY] = perfil.usuario_id
        messages.success(
            request,
            f'Operador activo: {perfil.operador_label} · {perfil.usuario.get_full_name() or perfil.usuario.username}.',
        )
    else:
        messages.error(request, form.errors.as_text().replace('* ', '').strip())
    return redirect(request.POST.get('next') or 'comandas:layout_mesas')


@require_POST
@requiere_comandas
def liberar_operador(request):
    request.session.pop(SESSION_OPERATOR_KEY, None)
    messages.success(request, 'Operador de pedestal liberado. La terminal vuelve a modo administracion.')
    return redirect(request.POST.get('next') or 'comandas:layout_mesas')


@requiere_revision_comandas
def panel_historial(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()

    comandas = Comanda.objects.select_related('mesa', 'garzon').order_by('-creada_at')
    if query:
        lookup = (
            Q(garzon__username__icontains=query)
            | Q(garzon__first_name__icontains=query)
            | Q(garzon__last_name__icontains=query)
        )
        if query.isdigit():
            lookup |= Q(numero_dia=int(query)) | Q(mesa__numero=int(query))
        comandas = comandas.filter(lookup)
    if estado:
        comandas = comandas.filter(estado=estado)

    return render(request, 'comandas/panel/historial.html', {
        'comandas': comandas[:100],
        'query': query,
        'estado': estado,
        'estado_choices': Comanda.ESTADO_CHOICES,
    })
