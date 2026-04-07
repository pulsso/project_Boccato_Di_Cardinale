from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import PerfilCaja, AperturaCaja, CierreCaja, Pago, Anulacion, TransaccionCaja
from comandas.models import Comanda
from .forms import AperturaCajaForm, CierreCajaForm, PagoForm, AnulacionForm


# ── DECORADORES ─────────────────────────────────────────────

def requiere_perfil_caja(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        try:
            perfil = request.user.perfil_caja
            if not perfil.activo:
                messages.error(request, 'Tu perfil de caja esta desactivado.')
                return redirect('/')
        except PerfilCaja.DoesNotExist:
            if not request.user.is_staff:
                messages.error(request, 'No tienes acceso al modulo de caja.')
                return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def requiere_tesorero(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        try:
            perfil = request.user.perfil_caja
            if perfil.rol != 'tesorero' and not request.user.is_superuser:
                messages.error(request, 'Solo el Tesorero puede realizar esta accion.')
                return redirect('caja:dashboard')
        except PerfilCaja.DoesNotExist:
            if not request.user.is_superuser:
                messages.error(request, 'Acceso denegado.')
                return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def _get_apertura_activa():
    return (
        AperturaCaja.objects.filter(
            estado='autorizada',
            cierre__isnull=True,
        )
        .select_related('cajero', 'autorizador')
        .order_by('-autorizada_at', '-solicitada_at')
        .first()
    )


# ── DASHBOARD CAJERO ────────────────────────────────────────

@requiere_perfil_caja
def dashboard(request):
    hoy = timezone.now().date()
    apertura_activa = _get_apertura_activa()
    apertura_activa_es_propia = bool(
        apertura_activa and apertura_activa.cajero_id == request.user.id
    )

    comandas_por_cobrar = Comanda.objects.filter(
        estado='cerrada'
    ).exclude(pago__estado='aprobado').select_related('mesa', 'garzon')

    pagos_hoy = Pago.objects.filter(creado_at__date=hoy, estado='aprobado')
    total_hoy = pagos_hoy.aggregate(t=Sum('monto_total'))['t'] or 0
    propinas_hoy = pagos_hoy.aggregate(p=Sum('propina'))['p'] or 0

    resumen_metodos = {}
    for metodo, label in Pago.METODO_CHOICES:
        total = pagos_hoy.filter(metodo=metodo).aggregate(t=Sum('monto_total'))['t'] or 0
        resumen_metodos[metodo] = {'label': label, 'total': total}

    apertura_pendiente = (
        AperturaCaja.objects.filter(cajero=request.user, estado='pendiente')
        .select_related('autorizador')
        .order_by('-solicitada_at')
        .first()
    )

    return render(request, 'caja/dashboard.html', {
        'apertura_activa': apertura_activa,
        'apertura_activa_es_propia': apertura_activa_es_propia,
        'apertura_pendiente': apertura_pendiente,
        'comandas_por_cobrar': comandas_por_cobrar,
        'total_hoy': total_hoy,
        'propinas_hoy': propinas_hoy,
        'resumen_metodos': resumen_metodos,
        'pagos_hoy': pagos_hoy.count(),
        'hoy': hoy,
    })


# ── APERTURA ────────────────────────────────────────────────

@requiere_perfil_caja
def solicitar_apertura(request):
    apertura_activa = _get_apertura_activa()
    if apertura_activa:
        responsable = apertura_activa.cajero.get_full_name() or apertura_activa.cajero.username
        if apertura_activa.cajero_id == request.user.id:
            messages.warning(request, 'Tu caja ya se encuentra abierta y autorizada.')
        else:
            messages.warning(request, f'La caja ya esta abierta para {responsable}. Debe cerrarse antes de solicitar una nueva apertura.')
        return redirect('caja:dashboard')

    apertura_existente = (
        AperturaCaja.objects.filter(cajero=request.user, estado='pendiente')
        .order_by('-solicitada_at')
        .first()
    )

    if apertura_existente:
        messages.warning(request, 'Ya existe una solicitud de apertura pendiente para tu usuario.')
        return redirect('caja:dashboard')

    form = AperturaCajaForm(request.POST or None)
    if form.is_valid():
        apertura = form.save(commit=False)
        apertura.cajero = request.user
        apertura.save()
        messages.success(request, 'Solicitud de apertura enviada. Esperando autorizacion del Tesorero.')
        return redirect('caja:dashboard')
    return render(request, 'caja/apertura_form.html', {'form': form})


@requiere_tesorero
def autorizar_apertura(request, pk):
    apertura = get_object_or_404(AperturaCaja, pk=pk, estado='pendiente')
    if request.method == 'POST':
        accion = request.POST.get('accion')
        motivo = request.POST.get('motivo', '')
        if accion == 'autorizar':
            apertura.autorizar(autorizador=request.user)
            messages.success(request, f'Apertura autorizada para {apertura.cajero.get_full_name() or apertura.cajero.username}.')
        elif accion == 'rechazar':
            apertura.rechazar(autorizador=request.user, motivo=motivo)
            messages.warning(request, 'Apertura rechazada.')
        return redirect('caja:tesorero_dashboard')
    return render(request, 'caja/autorizar_apertura.html', {'apertura': apertura})


# ── CIERRE ───────────────────────────────────────────────────

@requiere_perfil_caja
def solicitar_cierre(request, apertura_id):
    apertura = get_object_or_404(AperturaCaja, pk=apertura_id, estado='autorizada')

    if hasattr(apertura, 'cierre'):
        messages.warning(request, 'Esta apertura ya tiene un cierre registrado.')
        return redirect('caja:dashboard')

    pagos_apertura = Pago.objects.filter(apertura_caja=apertura, estado='aprobado')
    totales = {
        'monto_efectivo':        pagos_apertura.filter(metodo='efectivo').aggregate(t=Sum('monto_total'))['t'] or 0,
        'monto_tarjeta_credito': pagos_apertura.filter(metodo='tarjeta_credito').aggregate(t=Sum('monto_total'))['t'] or 0,
        'monto_tarjeta_debito':  pagos_apertura.filter(metodo='tarjeta_debito').aggregate(t=Sum('monto_total'))['t'] or 0,
        'monto_transferencia':   pagos_apertura.filter(metodo='transferencia').aggregate(t=Sum('monto_total'))['t'] or 0,
        'monto_propinas':        pagos_apertura.aggregate(p=Sum('propina'))['p'] or 0,
    }
    total_esperado = sum(v for k, v in totales.items() if k != 'monto_propinas')

    if request.method == 'POST':
        form = CierreCajaForm(request.POST)
        if form.is_valid():
            cierre = form.save(commit=False)
            cierre.apertura = apertura
            cierre.cajero = request.user
            cierre.save()
            messages.success(request, 'Solicitud de cierre enviada. Esperando autorizacion del Tesorero.')
            return redirect('caja:dashboard')
    else:
        form = CierreCajaForm(initial=totales)

    return render(request, 'caja/cierre_form.html', {
        'form': form,
        'apertura': apertura,
        'totales': totales,
        'total_esperado': total_esperado,
        'pagos_apertura': pagos_apertura,
    })


@requiere_tesorero
def autorizar_cierre(request, pk):
    cierre = get_object_or_404(CierreCaja, pk=pk, estado='pendiente')
    if request.method == 'POST':
        accion = request.POST.get('accion')
        motivo = request.POST.get('motivo', '')
        if accion == 'autorizar':
            cierre.autorizar(autorizador=request.user)
            messages.success(request, f'Cierre autorizado. Total: ${cierre.get_total():,.0f}')
        elif accion == 'rechazar':
            cierre.estado = 'rechazado'
            cierre.autorizador = request.user
            cierre.notas_rechazo = motivo
            cierre.save()
            TransaccionCaja.registrar(
                tipo='rechazo_apertura',
                usuario=cierre.cajero,
                autorizador=request.user,
                monto=0,
                descripcion=f'Cierre rechazado. Motivo: {motivo or "Sin motivo"}',
                referencia_id=cierre.id,
                referencia_modelo='CierreCaja',
            )
            messages.warning(request, 'Cierre rechazado.')
        return redirect('caja:tesorero_dashboard')
    return render(request, 'caja/autorizar_cierre.html', {'cierre': cierre})


# ── PAGO ─────────────────────────────────────────────────────

@requiere_perfil_caja
def registrar_pago(request, comanda_id):
    comanda = get_object_or_404(Comanda, pk=comanda_id, estado='cerrada')

    if hasattr(comanda, 'pago') and comanda.pago.estado == 'aprobado':
        messages.warning(request, 'Esta comanda ya fue pagada.')
        return redirect('caja:dashboard')

    apertura_activa = _get_apertura_activa()
    if not apertura_activa:
        messages.error(request, 'No hay caja abierta. Solicita apertura primero.')
        return redirect('caja:dashboard')

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                pago = form.save(commit=False)
                pago.comanda = comanda
                pago.apertura_caja = apertura_activa
                pago.cajero = request.user
                pago.monto_total = comanda.get_total_with_tax()

                if pago.metodo == 'transferencia':
                    pago.estado = 'pendiente'
                    pago.save()
                    TransaccionCaja.registrar(
                        tipo='transferencia',
                        usuario=request.user,
                        monto=pago.monto_total,
                        descripcion=f'Transferencia pendiente — Mesa {comanda.mesa.numero} — Ref: {pago.referencia}',
                        referencia_id=pago.id,
                        referencia_modelo='Pago',
                        apertura=apertura_activa,
                        ip_address=_get_ip(request),
                    )
                    messages.info(request, 'Transferencia registrada. Pendiente autorizacion del Tesorero.')
                else:
                    pago.save()
                    pago.aprobar(autorizador=None)
                    messages.success(request, f'Pago registrado. Total: ${pago.get_total_con_propina():,.0f}')

            return redirect('caja:recibo', pago_id=pago.id)
    else:
        form = PagoForm(initial={'propina': comanda.get_suggested_tip()})

    return render(request, 'caja/registrar_pago.html', {
        'form': form,
        'comanda': comanda,
        'total': comanda.get_total_with_tax(),
        'subtotal_neto': comanda.get_net_total(),
        'iva_amount': comanda.get_tax_amount(),
        'suggested_tip': comanda.get_suggested_tip(),
    })


@requiere_tesorero
def autorizar_transferencia(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id, metodo='transferencia', estado='pendiente')
    if request.method == 'POST':
        accion = request.POST.get('accion')
        motivo = request.POST.get('motivo', '')
        if accion == 'autorizar':
            pago.aprobar(autorizador=request.user)
            messages.success(request, f'Transferencia autorizada. Mesa {pago.comanda.mesa.numero}.')
        elif accion == 'rechazar':
            pago.estado = 'rechazado'
            pago.save()
            TransaccionCaja.registrar(
                tipo='rechazo_transferencia',
                usuario=pago.cajero,
                autorizador=request.user,
                monto=pago.monto_total,
                descripcion=f'Transferencia RECHAZADA — Mesa {pago.comanda.mesa.numero} — Motivo: {motivo}',
                referencia_id=pago.id,
                referencia_modelo='Pago',
                apertura=pago.apertura_caja,
            )
            messages.warning(request, 'Transferencia rechazada.')
        return redirect('caja:tesorero_dashboard')
    return render(request, 'caja/autorizar_transferencia.html', {'pago': pago})


# ── ANULACION ────────────────────────────────────────────────

@requiere_tesorero
def anular_pago(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id, estado='aprobado')
    form = AnulacionForm(request.POST or None)
    if form.is_valid():
        motivo = form.cleaned_data['motivo']
        pago.anular(usuario=request.user, autorizador=request.user, motivo=motivo)
        messages.success(request, f'Pago #{pago.id} anulado. Transaccion registrada.')
        return redirect('caja:tesorero_dashboard')
    return render(request, 'caja/anular_pago.html', {'form': form, 'pago': pago})


# ── RECIBO ───────────────────────────────────────────────────

@requiere_perfil_caja
def recibo(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id)
    txn = TransaccionCaja.objects.filter(
        referencia_modelo='Pago',
        referencia_id=pago.id,
        tipo='pago'
    ).first()
    return render(request, 'caja/recibo.html', {'pago': pago, 'txn': txn})


# ── HISTORIAL ────────────────────────────────────────────────

@requiere_perfil_caja
def historial_pagos(request):
    fecha = request.GET.get('fecha', '')
    metodo = request.GET.get('metodo', '')
    cajero_id = request.GET.get('cajero', '')

    pagos = Pago.objects.select_related('comanda__mesa', 'cajero', 'autorizador').all()

    try:
        perfil = request.user.perfil_caja
        if perfil.rol == 'cajero':
            pagos = pagos.filter(cajero=request.user)
    except PerfilCaja.DoesNotExist:
        pass

    if fecha:
        pagos = pagos.filter(creado_at__date=fecha)
    if metodo:
        pagos = pagos.filter(metodo=metodo)
    if cajero_id:
        pagos = pagos.filter(cajero_id=cajero_id)

    from django.contrib.auth.models import User
    cajeros = User.objects.filter(pagos_registrados__isnull=False).distinct()
    total_filtrado = pagos.filter(estado='aprobado').aggregate(t=Sum('monto_total'))['t'] or 0

    return render(request, 'caja/historial.html', {
        'pagos': pagos,
        'cajeros': cajeros,
        'metodo_choices': Pago.METODO_CHOICES,
        'fecha_sel': fecha,
        'metodo_sel': metodo,
        'cajero_sel': cajero_id,
        'total_filtrado': total_filtrado,
    })


# ── DASHBOARD TESORERO ───────────────────────────────────────

@requiere_tesorero
def tesorero_dashboard(request):
    hoy = timezone.now().date()
    from payments.models import Payment as StorePayment
    from orders.models import OrderNotification

    aperturas_pendientes = AperturaCaja.objects.filter(estado='pendiente').select_related('cajero')
    cierres_pendientes = CierreCaja.objects.filter(estado='pendiente').select_related('cajero', 'apertura')
    transferencias_pendientes = Pago.objects.filter(
        metodo='transferencia', estado='pendiente'
    ).select_related('comanda__mesa', 'cajero')
    ecommerce_transferencias_pendientes = StorePayment.objects.filter(
        method='transfer', status='pending'
    ).select_related('order', 'user')
    ecommerce_validaciones_recientes = StorePayment.objects.exclude(
        status='pending'
    ).select_related('order', 'user', 'approved_by')
    ecommerce_notificaciones_recientes = OrderNotification.objects.filter(
        order__payment__method='transfer'
    ).select_related('order', 'recipient_user').order_by('-created_at')[:12]

    pagos_hoy = Pago.objects.filter(creado_at__date=hoy, estado='aprobado')
    total_hoy = pagos_hoy.aggregate(t=Sum('monto_total'))['t'] or 0
    propinas_hoy = pagos_hoy.aggregate(p=Sum('propina'))['p'] or 0

    resumen = {}
    for metodo, label in Pago.METODO_CHOICES:
        total = pagos_hoy.filter(metodo=metodo).aggregate(t=Sum('monto_total'))['t'] or 0
        cantidad = pagos_hoy.filter(metodo=metodo).count()
        resumen[metodo] = {'label': label, 'total': total, 'cantidad': cantidad}

    historial_cierres = CierreCaja.objects.filter(
        estado='autorizado'
    ).select_related('cajero', 'autorizador').order_by('-autorizado_at')[:10]

    anulaciones_recientes = Anulacion.objects.select_related(
        'pago__comanda__mesa', 'solicitado_por', 'autorizado_por'
    ).order_by('-creada_at')[:5]

    return render(request, 'caja/tesorero_dashboard.html', {
        'aperturas_pendientes': aperturas_pendientes,
        'cierres_pendientes': cierres_pendientes,
        'transferencias_pendientes': transferencias_pendientes,
        'ecommerce_transferencias_pendientes': ecommerce_transferencias_pendientes,
        'ecommerce_validaciones_recientes': ecommerce_validaciones_recientes[:10],
        'ecommerce_notificaciones_recientes': ecommerce_notificaciones_recientes,
        'total_hoy': total_hoy,
        'propinas_hoy': propinas_hoy,
        'resumen': resumen,
        'historial_cierres': historial_cierres,
        'anulaciones_recientes': anulaciones_recientes,
        'hoy': hoy,
    })


# ── AUDITORIA ────────────────────────────────────────────────

@requiere_tesorero
def auditoria(request):
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    tipo = request.GET.get('tipo', '')
    usuario_id = request.GET.get('usuario', '')

    txns = TransaccionCaja.objects.select_related('usuario', 'autorizador', 'apertura').all()

    if fecha_desde:
        txns = txns.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        txns = txns.filter(fecha__date__lte=fecha_hasta)
    if tipo:
        txns = txns.filter(tipo=tipo)
    if usuario_id:
        txns = txns.filter(usuario_id=usuario_id)

    total_txns = txns.count()
    total_monto = txns.filter(tipo='pago').aggregate(t=Sum('monto'))['t'] or 0
    total_anulaciones = txns.filter(tipo='anulacion').aggregate(t=Sum('monto'))['t'] or 0

    from django.contrib.auth.models import User
    usuarios = User.objects.filter(transacciones_caja__isnull=False).distinct()

    return render(request, 'caja/auditoria.html', {
        'txns': txns[:200],
        'total_txns': total_txns,
        'total_monto': total_monto,
        'total_anulaciones': total_anulaciones,
        'tipo_choices': TransaccionCaja.TIPO_CHOICES,
        'usuarios': usuarios,
        'desde_sel': fecha_desde,
        'hasta_sel': fecha_hasta,
        'tipo_sel': tipo,
        'usuario_sel': usuario_id,
    })
