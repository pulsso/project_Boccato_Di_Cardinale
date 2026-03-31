from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from PIL import Image
import json
from .models import Category, Product, GaleriaFoto, Oferta, Campana, HistorialCambio
from .forms import ProductForm, OfertaForm, CampanaForm, GaleriaFotoForm
from orders.models import Order, OrderItem
from config.commerce import get_sector_coordinates, get_sector_label, get_zone_label
import datetime


SAMPLE_GALLERY = [
    {
        'titulo': 'Terraza Panoramica',
        'descripcion': 'Vista abierta, cocteleria y servicio de terraza durante toda la jornada.',
        'section_label': 'Terraza Principal',
        'display_image_url': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=1200&q=80',
    },
    {
        'titulo': 'Galeria de Arte',
        'descripcion': 'Ambiente cultural para tardes de cafe y noches de vino.',
        'section_label': 'Galeria de Arte',
        'display_image_url': 'https://images.unsplash.com/photo-1541532713592-79a0317b6b77?w=1200&q=80',
    },
    {
        'titulo': 'La Barra',
        'descripcion': 'Barra central con cocteleria clasica y tragos de autor.',
        'section_label': 'La Barra',
        'display_image_url': 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=1200&q=80',
    },
    {
        'titulo': 'Salon Privado VIP',
        'descripcion': 'Espacio reservado para experiencias exclusivas y celebraciones.',
        'section_label': 'Salon VIP',
        'display_image_url': 'https://images.unsplash.com/photo-1578474846511-04ba529f0b88?w=1200&q=80',
    },
    {
        'titulo': 'Sala de Reuniones',
        'descripcion': 'Reuniones ejecutivas con servicio de cafe y catering.',
        'section_label': 'Sala de Reuniones',
        'display_image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80',
    },
    {
        'titulo': 'Noches en Vivo',
        'descripcion': 'Escenario y ambientacion para sesiones musicales de terraza.',
        'section_label': 'Musica en Vivo',
        'display_image_url': 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1200&q=80',
    },
]


def _gallery_cards():
    try:
        fotos = GaleriaFoto.objects.filter(activa=True)
        if fotos.exists():
            cards = []
            for foto in fotos:
                image_url = foto.display_image_url
                if not image_url:
                    continue
                cards.append({
                    'titulo': foto.titulo,
                    'descripcion': foto.descripcion,
                    'section_label': foto.get_seccion_display(),
                    'display_image_url': image_url,
                    'activa': foto.activa,
                    'pk': foto.pk,
                })
            if cards:
                return cards
    except Exception:
        pass
    return SAMPLE_GALLERY


# ── TIENDA PÚBLICA ──────────────────────────────────────────

def product_list(request):
    categories = Category.objects.filter(active=True)
    category_slug = request.GET.get('category')
    products = Product.objects.filter(available=True)
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    campanas = Campana.objects.filter(activa=True, tipo='banner',
                                       fecha_inicio__lte=timezone.now().date(),
                                       fecha_fin__gte=timezone.now().date())
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'campanas': campanas,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    oferta = product.ofertas.filter(activa=True).first()
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'oferta': oferta,
    })


def terraza(request):
    fotos = _gallery_cards()
    fotos_por_seccion = {}
    for foto in fotos:
        seccion = foto['section_label']
        if seccion not in fotos_por_seccion:
            fotos_por_seccion[seccion] = []
        fotos_por_seccion[seccion].append(foto)
    return render(request, 'catalog/terraza.html', {
        'fotos': fotos,
        'fotos_por_seccion': fotos_por_seccion,
        'fotos_total': len(fotos),
    })


# ── CRUD PRODUCTOS ──────────────────────────────────────────

@staff_member_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save()
        if product.image:
            optimize_image(product.image.path)
        _registrar_historial(request.user, 'crear', 'Producto', product.id, product.name,
                             f'Precio: ${product.price} | Stock: {product.stock}')
        messages.success(request, 'Producto creado correctamente.')
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_form.html', {'form': form, 'title': 'Nuevo Producto'})


@staff_member_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    precio_anterior = product.price
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        product = form.save()
        if product.image:
            optimize_image(product.image.path)
        detalle = f'Precio anterior: ${precio_anterior} → nuevo: ${product.price}'
        accion = 'precio' if precio_anterior != product.price else 'editar'
        _registrar_historial(request.user, accion, 'Producto', product.id, product.name, detalle)
        messages.success(request, 'Producto actualizado.')
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_form.html', {'form': form, 'title': 'Editar Producto'})


@staff_member_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        nombre = product.name
        product.delete()
        _registrar_historial(request.user, 'eliminar', 'Producto', None, nombre, '')
        messages.success(request, 'Producto eliminado.')
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_confirm_delete.html', {'product': product})


# ── PANEL ADMIN PERSONALIZADO ───────────────────────────────

@staff_member_required
def panel_dashboard(request):
    hoy = timezone.now().date()
    total_productos = Product.objects.count()
    total_categorias = Category.objects.count()
    total_ordenes = Order.objects.count()
    ordenes_pendientes = Order.objects.filter(status='pending').count()
    ofertas_activas = Oferta.objects.filter(activa=True, fecha_fin__gte=hoy).count()
    campanas_activas = Campana.objects.filter(activa=True, fecha_fin__gte=hoy).count()
    ventas_totales = Order.objects.filter(paid=True).aggregate(
        total=Sum('items__price'))['total'] or 0
    ultimas_ordenes = Order.objects.select_related('user').order_by('-created_at')[:5]
    ultimos_cambios = HistorialCambio.objects.select_related('usuario').order_by('-fecha')[:8]
    productos_sin_stock = Product.objects.filter(stock=0, available=True).count()
    ordenes_zona = Order.objects.exclude(zone='').values('zone').annotate(total=Count('id')).order_by('-total')
    ordenes_sector = Order.objects.exclude(sector='').values('sector').annotate(total=Count('id')).order_by('-total')[:8]
    sales_map_points = []
    for order in Order.objects.exclude(sector='').select_related('user').order_by('-created_at')[:80]:
        coords = get_sector_coordinates(order.sector)
        sales_map_points.append({
            'id': order.id,
            'sector': get_sector_label(order.sector),
            'zone': get_zone_label(order.zone),
            'lat': coords['lat'],
            'lng': coords['lng'],
            'total': float(order.get_grand_total()),
            'status': order.get_status_display(),
            'customer': order.user.get_full_name() or order.user.username,
        })

    return render(request, 'catalog/panel/dashboard.html', {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_ordenes': total_ordenes,
        'ordenes_pendientes': ordenes_pendientes,
        'ofertas_activas': ofertas_activas,
        'campanas_activas': campanas_activas,
        'ventas_totales': ventas_totales,
        'ultimas_ordenes': ultimas_ordenes,
        'ultimos_cambios': ultimos_cambios,
        'productos_sin_stock': productos_sin_stock,
        'ordenes_zona': [
            {'label': get_zone_label(item['zone']), 'total': item['total']}
            for item in ordenes_zona
        ],
        'ordenes_sector': [
            {'label': get_sector_label(item['sector']), 'total': item['total']}
            for item in ordenes_sector
        ],
        'sales_map_points_json': json.dumps(sales_map_points),
    })


@staff_member_required
def panel_productos(request):
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    productos = Product.objects.select_related('category').all()
    if q:
        productos = productos.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if categoria:
        productos = productos.filter(category__slug=categoria)
    categorias = Category.objects.filter(active=True)
    return render(request, 'catalog/panel/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'q': q,
        'categoria_sel': categoria,
    })


@staff_member_required
def panel_producto_crear(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save()
        if product.image:
            optimize_image(product.image.path)
        _registrar_historial(request.user, 'crear', 'Producto', product.id, product.name,
                             f'Precio: ${product.price} | Stock: {product.stock}')
        messages.success(request, f'Producto "{product.name}" creado.')
        return redirect('catalog:panel_productos')
    return render(request, 'catalog/panel/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@staff_member_required
def panel_producto_editar(request, pk):
    product = get_object_or_404(Product, pk=pk)
    precio_anterior = product.price
    stock_anterior = product.stock
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        product = form.save()
        if product.image:
            optimize_image(product.image.path)
        cambios = []
        if precio_anterior != product.price:
            cambios.append(f'Precio: ${precio_anterior} → ${product.price}')
        if stock_anterior != product.stock:
            cambios.append(f'Stock: {stock_anterior} → {product.stock}')
        accion = 'precio' if precio_anterior != product.price else 'editar'
        _registrar_historial(request.user, accion, 'Producto', product.id, product.name,
                             ' | '.join(cambios) if cambios else 'Editado')
        messages.success(request, f'Producto "{product.name}" actualizado.')
        return redirect('catalog:panel_productos')
    return render(request, 'catalog/panel/producto_form.html', {
        'form': form, 'titulo': f'Editar: {product.name}', 'producto': product
    })


@staff_member_required
def panel_producto_eliminar(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        nombre = product.name
        product.delete()
        _registrar_historial(request.user, 'eliminar', 'Producto', None, nombre, '')
        messages.success(request, f'Producto "{nombre}" eliminado.')
        return redirect('catalog:panel_productos')
    return render(request, 'catalog/panel/confirmar_eliminar.html', {'objeto': product, 'tipo': 'Producto'})


@staff_member_required
def panel_categorias(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            from django.utils.text import slugify
            slug = slugify(nombre)
            cat, created = Category.objects.get_or_create(slug=slug, defaults={'name': nombre})
            if created:
                _registrar_historial(request.user, 'crear', 'Categoría', cat.id, cat.name, '')
                messages.success(request, f'Categoría "{nombre}" creada.')
            else:
                messages.warning(request, 'Esa categoría ya existe.')
        return redirect('catalog:panel_categorias')
    categorias = Category.objects.annotate(total_productos=Count('products'))
    return render(request, 'catalog/panel/categorias.html', {'categorias': categorias})


@staff_member_required
def panel_ofertas(request):
    hoy = timezone.now().date()
    ofertas = Oferta.objects.select_related('producto', 'creada_por').all()
    return render(request, 'catalog/panel/ofertas.html', {'ofertas': ofertas, 'hoy': hoy})


@staff_member_required
def panel_oferta_crear(request):
    form = OfertaForm(request.POST or None)
    if form.is_valid():
        oferta = form.save(commit=False)
        oferta.creada_por = request.user
        oferta.save()
        _registrar_historial(request.user, 'oferta', 'Oferta', oferta.id,
                             str(oferta), f'{oferta.descuento_porcentaje}% hasta {oferta.fecha_fin}')
        messages.success(request, 'Oferta creada.')
        return redirect('catalog:panel_ofertas')
    return render(request, 'catalog/panel/oferta_form.html', {'form': form, 'titulo': 'Nueva Oferta'})


@staff_member_required
def panel_oferta_eliminar(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)
    if request.method == 'POST':
        nombre = str(oferta)
        oferta.delete()
        _registrar_historial(request.user, 'eliminar', 'Oferta', None, nombre, '')
        messages.success(request, 'Oferta eliminada.')
    return redirect('catalog:panel_ofertas')


@staff_member_required
def panel_campanas(request):
    hoy = timezone.now().date()
    campanas = Campana.objects.select_related('creada_por').all()
    return render(request, 'catalog/panel/campanas.html', {'campanas': campanas, 'hoy': hoy})


@staff_member_required
def panel_campana_crear(request):
    form = CampanaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        campana = form.save(commit=False)
        campana.creada_por = request.user
        campana.save()
        _registrar_historial(request.user, 'campana', 'Campaña', campana.id,
                             campana.titulo, f'Tipo: {campana.tipo}')
        messages.success(request, 'Campaña creada.')
        return redirect('catalog:panel_campanas')
    return render(request, 'catalog/panel/campana_form.html', {'form': form, 'titulo': 'Nueva Campaña'})


@staff_member_required
def panel_campana_eliminar(request, pk):
    campana = get_object_or_404(Campana, pk=pk)
    if request.method == 'POST':
        nombre = campana.titulo
        campana.delete()
        _registrar_historial(request.user, 'eliminar', 'Campaña', None, nombre, '')
        messages.success(request, 'Campaña eliminada.')
    return redirect('catalog:panel_campanas')


@staff_member_required
def panel_ordenes(request):
    status = request.GET.get('status', '')
    ordenes = Order.objects.select_related('user').prefetch_related('items__product')
    if status:
        ordenes = ordenes.filter(status=status)
    return render(request, 'catalog/panel/ordenes.html', {
        'ordenes': ordenes,
        'status_sel': status,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required
def panel_orden_detalle(request, pk):
    orden = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        nuevo_status = request.POST.get('status')
        if nuevo_status:
            status_anterior = orden.status
            orden.status = nuevo_status
            orden.save()
            _registrar_historial(request.user, 'editar', 'Orden', orden.id,
                                 f'Orden #{orden.id}',
                                 f'Estado: {status_anterior} → {nuevo_status}')
            messages.success(request, 'Estado de orden actualizado.')
        return redirect('catalog:panel_orden_detalle', pk=pk)
    return render(request, 'catalog/panel/orden_detalle.html', {
        'orden': orden,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required
def panel_galeria(request):
    fotos = GaleriaFoto.objects.all()
    return render(request, 'catalog/panel/galeria.html', {'fotos': fotos})


@staff_member_required
def panel_galeria_crear(request):
    form = GaleriaFotoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        foto = form.save()
        _registrar_historial(request.user, 'crear', 'GaleriaFoto', foto.id,
                             foto.titulo, f'Sección: {foto.get_seccion_display()}')
        messages.success(request, 'Foto agregada a la galería.')
        return redirect('catalog:panel_galeria')
    return render(request, 'catalog/panel/galeria_form.html', {'form': form, 'titulo': 'Nueva Foto'})


@staff_member_required
def panel_galeria_eliminar(request, pk):
    foto = get_object_or_404(GaleriaFoto, pk=pk)
    if request.method == 'POST':
        titulo = foto.titulo
        foto.delete()
        _registrar_historial(request.user, 'eliminar', 'GaleriaFoto', None, titulo, '')
        messages.success(request, 'Foto eliminada.')
    return redirect('catalog:panel_galeria')


@staff_member_required
def panel_historial(request):
    usuario = request.GET.get('usuario', '')
    accion = request.GET.get('accion', '')
    historial = HistorialCambio.objects.select_related('usuario').all()
    if usuario:
        historial = historial.filter(usuario__username__icontains=usuario)
    if accion:
        historial = historial.filter(accion=accion)
    return render(request, 'catalog/panel/historial.html', {
        'historial': historial,
        'accion_choices': HistorialCambio.ACCION_CHOICES,
        'usuario_q': usuario,
        'accion_sel': accion,
    })


@staff_member_required
def panel_reportes(request):
    hoy = timezone.now().date()
    mes_actual = hoy.replace(day=1)

    ventas_mes = Order.objects.filter(
        paid=True, created_at__date__gte=mes_actual
    ).aggregate(total=Sum('items__price'))['total'] or 0

    ventas_total = Order.objects.filter(paid=True).aggregate(
        total=Sum('items__price'))['total'] or 0

    ordenes_mes = Order.objects.filter(created_at__date__gte=mes_actual).count()
    ordenes_total = Order.objects.count()

    top_productos = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_vendido=Sum('quantity')
    ).order_by('-total_vendido')[:10]

    ordenes_por_status = Order.objects.values('status').annotate(
        total=Count('id')
    ).order_by('-total')

    productos_sin_stock = Product.objects.filter(stock=0, available=True)

    return render(request, 'catalog/panel/reportes.html', {
        'ventas_mes': ventas_mes,
        'ventas_total': ventas_total,
        'ordenes_mes': ordenes_mes,
        'ordenes_total': ordenes_total,
        'top_productos': top_productos,
        'ordenes_por_status': ordenes_por_status,
        'productos_sin_stock': productos_sin_stock,
        'mes_actual': mes_actual,
    })


# ── HELPERS ─────────────────────────────────────────────────

def _registrar_historial(usuario, accion, modelo, objeto_id, objeto_nombre, detalle):
    HistorialCambio.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        objeto_nombre=objeto_nombre,
        detalle=detalle,
    )


def optimize_image(path):
    img = Image.open(path)
    img = img.convert('RGB')
    img.thumbnail((800, 800))
    img.save(path, 'JPEG', quality=85, optimize=True)
