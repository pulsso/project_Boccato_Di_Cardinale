from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image

from .forms import CategoriaMenuForm, ItemMenuForm
from .models import CategoriaMenu, ItemMenu


def _local_menu_fallback(tipo):
    file_by_tipo = {
        'desayuno': 'desayuno.jpg',
        'brunch': 'brunch.jpg',
        'almuerzo': 'almuerzo.jpg',
        'postres': 'postres.jpg',
        'infantil': 'infantil.jpg',
        'te_cafe': 'te_cafe.jpg',
        'bebidas': 'bebidas.jpg',
        'llevar': 'llevar.jpg',
        'cena': 'cena.jpg',
        'terraza': 'terraza.jpg',
        'vinos': 'vinos.jpg',
        'licores': 'licores.jpg',
        'cocteles': 'cocteles.jpg',
        'catering': 'catering.jpg',
    }
    return f"/static/menu/photos/{file_by_tipo.get(tipo, 'almuerzo.jpg')}"


SECTION_META = {
    'desayuno': {'label': 'Desayuno', 'icon': 'D'},
    'brunch': {'label': 'Brunch & Once', 'icon': 'B'},
    'almuerzo': {'label': 'Almuerzo', 'icon': 'A'},
    'postres': {'label': 'Postres', 'icon': 'P'},
    'infantil': {'label': 'Infantil Dia', 'icon': 'I'},
    'te_cafe': {'label': 'Te - Cafe', 'icon': 'TC'},
    'bebidas': {'label': 'Bebidas y Cervezas', 'icon': 'BB'},
    'llevar': {'label': 'Para Llevar', 'icon': 'PL'},
    'cena': {'label': 'Cena', 'icon': 'C'},
    'terraza': {'label': 'Terraza', 'icon': 'T'},
    'vinos': {'label': 'Vinos', 'icon': 'V'},
    'licores': {'label': 'Licores', 'icon': 'L'},
    'cocteles': {'label': 'Cocteles', 'icon': 'Co'},
    'catering': {'label': 'Catering', 'icon': 'E'},
}

SECTION_IMAGE_FALLBACKS = {
    'desayuno': _local_menu_fallback('desayuno'),
    'brunch': _local_menu_fallback('brunch'),
    'almuerzo': _local_menu_fallback('almuerzo'),
    'postres': _local_menu_fallback('postres'),
    'infantil': _local_menu_fallback('infantil'),
    'te_cafe': _local_menu_fallback('te_cafe'),
    'bebidas': _local_menu_fallback('bebidas'),
    'llevar': _local_menu_fallback('llevar'),
    'cena': _local_menu_fallback('cena'),
    'terraza': _local_menu_fallback('terraza'),
    'vinos': _local_menu_fallback('vinos'),
    'licores': _local_menu_fallback('licores'),
    'cocteles': _local_menu_fallback('cocteles'),
    'catering': _local_menu_fallback('catering'),
}


SAMPLE_MENU = {
    'desayuno': [
        {
            'categoria': {'nombre': 'Especialidades de la Manana', 'descripcion': 'Desde las 08:00 hrs'},
            'items': [
                {
                    'nombre': 'Croissant Boccato',
                    'descripcion': 'Croissant de mantequilla, mermelada de frutos rojos y cafe de especialidad.',
                    'precio': 6900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=900&q=80',
                    'precio_oferta': 5900,
                    'tiene_oferta': True,
                    'descuento_porcentaje': 14,
                },
                {
                    'nombre': 'Tostadas con palta y huevos',
                    'descripcion': 'Pan artesanal, palta hass, huevos pochados y aceite de oliva.',
                    'precio': 7900,
                    'display_image_url': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=900&q=80',
                },
            ],
        },
    ],
    'brunch': [
        {
            'categoria': {'nombre': 'Brunch de Fin de Semana', 'descripcion': 'Sabados, domingos y festivos'},
            'items': [
                {
                    'nombre': 'Huevos Benedictinos',
                    'descripcion': 'Muffin ingles, jamon serrano, salsa holandesa y brotes frescos.',
                    'precio': 8900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=900&q=80',
                },
                {
                    'nombre': 'French Toast Brioche',
                    'descripcion': 'Pan brioche, frutas del bosque, crema chantilly y syrup de maple.',
                    'precio': 8400,
                    'display_image_url': 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=900&q=80',
                },
            ],
        },
    ],
    'almuerzo': [
        {
            'categoria': {'nombre': 'Entradas y Fondos', 'descripcion': 'Cocina de mercado y temporada'},
            'items': [
                {
                    'nombre': 'Crema de zapallo asado',
                    'descripcion': 'Con aceite de oliva, semillas tostadas y queso de cabra.',
                    'precio': 5900,
                    'display_image_url': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=900&q=80',
                },
                {
                    'nombre': 'Risotto de champinones',
                    'descripcion': 'Arroz arborio, parmesano, hongos salteados y toque de trufa.',
                    'precio': 11900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=900&q=80',
                    'precio_oferta': 10900,
                    'tiene_oferta': True,
                    'descuento_porcentaje': 8,
                },
            ],
        },
    ],
    'postres': [
        {
            'categoria': {'nombre': 'Postres de la Casa', 'descripcion': 'Dulces artesanales y vitrina diaria'},
            'items': [
                {
                    'nombre': 'Tiramisu Boccato',
                    'descripcion': 'Crema de mascarpone, bizcocho de cafe y cacao amargo.',
                    'precio': 6200,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=900&q=80',
                },
                {
                    'nombre': 'Cheesecake de frutos rojos',
                    'descripcion': 'Base crocante, queso crema y salsa de berries.',
                    'precio': 5900,
                    'display_image_url': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=900&q=80',
                },
            ],
        },
    ],
    'infantil': [
        {
            'categoria': {'nombre': 'Menu Infantil de Dia', 'descripcion': 'Disponible hasta las 18:00 hrs'},
            'items': [
                {
                    'nombre': 'Mini pasta pomodoro',
                    'descripcion': 'Pasta corta con salsa de tomate suave y queso rallado.',
                    'precio': 5900,
                    'display_image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=900&q=80',
                },
                {
                    'nombre': 'Pollo crispy con papas',
                    'descripcion': 'Tiras de pollo apanado, papas rusticas y jugo pequeno.',
                    'precio': 6900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1513639776629-7b61b0ac49cb?w=900&q=80',
                },
            ],
        },
    ],
    'te_cafe': [
        {
            'categoria': {'nombre': 'Cafe, Te e Infusiones', 'descripcion': 'Servicio de cafeteria, hierbas y teteras'},
            'items': [
                {
                    'nombre': 'Espresso Boccato',
                    'descripcion': 'Cafe de especialidad de tueste medio servido corto.',
                    'precio': 2800,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=900&q=80',
                },
                {
                    'nombre': 'Cappuccino de la casa',
                    'descripcion': 'Leche texturizada, espresso doble y cacao suave.',
                    'precio': 3900,
                    'display_image_url': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=900&q=80',
                },
                {
                    'nombre': 'Te premium en tetera',
                    'descripcion': 'Seleccion Earl Grey, chai, jazmin o frutos rojos.',
                    'precio': 3600,
                    'display_image_url': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=900&q=80',
                },
                {
                    'nombre': 'Infusion de hierbas del huerto',
                    'descripcion': 'Menta, cedron, manzanilla y jengibre segun disponibilidad.',
                    'precio': 3400,
                    'display_image_url': 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=900&q=80',
                },
            ],
        },
    ],
    'bebidas': [
        {
            'categoria': {'nombre': 'Jugos, Sodas y Cervezas', 'descripcion': 'Bebidas frias, cervezas y especialidades sin alcohol'},
            'items': [
                {
                    'nombre': 'Jugo natural del dia',
                    'descripcion': 'Preparado al momento con fruta fresca de temporada.',
                    'precio': 4200,
                    'display_image_url': 'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=900&q=80',
                },
                {
                    'nombre': 'Soda Boccato citrus',
                    'descripcion': 'Receta propia con limon, romero, miel y agua gasificada.',
                    'precio': 4300,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=900&q=80',
                },
                {
                    'nombre': 'Shop lager artesanal',
                    'descripcion': 'Formato shop bien frio con espuma cremosa.',
                    'precio': 4900,
                    'display_image_url': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=900&q=80',
                },
                {
                    'nombre': 'Cerveza artesanal botella',
                    'descripcion': 'IPA, amber ale o stout de productores locales.',
                    'precio': 5400,
                    'display_image_url': 'https://images.unsplash.com/photo-1436076863939-06870fe779c2?w=900&q=80',
                },
                {
                    'nombre': 'Bebida de fantasia',
                    'descripcion': 'Linea clasica, zero o ginger ale.',
                    'precio': 2600,
                    'display_image_url': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=900&q=80',
                },
            ],
        },
    ],
    'llevar': [
        {
            'categoria': {'nombre': 'Accesorios y Gourmet Boccato', 'descripcion': 'Productos para llevar, regalos y linea propia'},
            'items': [
                {
                    'nombre': 'Caja termica premium',
                    'descripcion': 'Caja rigida para despacho o picnic gourmet.',
                    'precio': 14900,
                    'display_image_url': '',
                },
                {
                    'nombre': 'Set cubiertos biodegradables',
                    'descripcion': 'Tenedor, cuchara, cuchillo de corte y servilleta.',
                    'precio': 1800,
                    'display_image_url': '',
                },
                {
                    'nombre': 'Chimichurri Boccato',
                    'descripcion': 'Receta propia en frasco para carnes y vegetales.',
                    'precio': 5200,
                    'display_image_url': '',
                },
                {
                    'nombre': 'Sal de mar Boccato gourmet',
                    'descripcion': 'Blend de sales con hierbas y citricos.',
                    'precio': 4600,
                    'display_image_url': '',
                },
                {
                    'nombre': 'Tabla de corte Boccato',
                    'descripcion': 'Tabla de madera para servicio, asado o regalo.',
                    'precio': 18900,
                    'display_image_url': '',
                },
                {
                    'nombre': 'Tarjeta VIP Terraza y Show',
                    'descripcion': 'Beneficio de 20% de descuento en terraza y show en vivo.',
                    'precio': 25000,
                    'destacado': True,
                    'display_image_url': '',
                },
            ],
        },
    ],
    'cena': [
        {
            'categoria': {'nombre': 'Cena de Autor', 'descripcion': 'Servicio nocturno y maridaje sugerido'},
            'items': [
                {
                    'nombre': 'Lomo vetado al romero',
                    'descripcion': 'Papas rusticas, reduccion de vino tinto y mantequilla de hierbas.',
                    'precio': 18900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=900&q=80',
                },
            ],
        },
    ],
    'terraza': [
        {
            'categoria': {'nombre': 'Tablas y Bocadillos', 'descripcion': 'Disponibles todo el dia en terraza'},
            'items': [
                {
                    'nombre': 'Tabla Boccato',
                    'descripcion': 'Quesos seleccionados, charcuteria, frutos secos y panes tostados.',
                    'precio': 15900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=900&q=80',
                },
            ],
        },
    ],
    'vinos': [
        {
            'categoria': {'nombre': 'Seleccion de la Casa', 'descripcion': 'Copas y botellas'},
            'items': [
                {
                    'nombre': 'Cabernet Sauvignon Reserva',
                    'descripcion': 'Vino tinto elegante de taninos suaves.',
                    'precio': 16900,
                    'bodega': 'Maipo Cellars',
                    'cepa': 'Cabernet Sauvignon',
                    'anno': '2022',
                    'origen': 'Valle del Maipo',
                    'display_image_url': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=900&q=80',
                },
            ],
        },
    ],
    'licores': [
        {
            'categoria': {'nombre': 'Destilados Premium', 'descripcion': 'Copa y servicio en barra'},
            'items': [
                {
                    'nombre': 'Whisky 12 anos',
                    'descripcion': 'Notas a vainilla, caramelo y roble tostado.',
                    'precio': 8900,
                    'bodega': 'Highland Reserve',
                    'graduacion': '40%',
                    'display_image_url': 'https://images.unsplash.com/photo-1527281400683-1aae777175f8?w=900&q=80',
                },
            ],
        },
    ],
    'cocteles': [
        {
            'categoria': {'nombre': 'Cocteleria de Autor', 'descripcion': 'Preparaciones de barra y aperitivos'},
            'items': [
                {
                    'nombre': 'Pisco Sour Premium',
                    'descripcion': 'Pisco reservado, limon sutil, syrup y angostura.',
                    'precio': 6900,
                    'destacado': True,
                    'display_image_url': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=900&q=80',
                },
            ],
        },
    ],
    'catering': [
        {
            'categoria': {'nombre': 'Eventos y Celebraciones', 'descripcion': 'Servicio a pedido'},
            'items': [
                {
                    'nombre': 'Coffee Break Ejecutivo',
                    'descripcion': 'Cafe premium, mini pasteleria, jugos y sandwiches.',
                    'precio': 12900,
                    'precio_persona': 12900,
                    'min_personas': 10,
                    'display_image_url': 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=900&q=80',
                },
            ],
        },
    ],
}


def _resolve_item_image(item, fallback_tipo=''):
    is_dict = isinstance(item, dict)
    if is_dict:
        return SECTION_IMAGE_FALLBACKS.get(fallback_tipo, '') or item.get('display_image_url') or item.get('external_image_url', '')

    image_url = getattr(item, 'display_image_url', '') or getattr(item, 'external_image_url', '')
    if image_url:
        return image_url

    categoria = getattr(item, 'categoria', None)
    tipo = fallback_tipo or getattr(categoria, 'tipo', '')
    return SECTION_IMAGE_FALLBACKS.get(tipo, '')


def _normalize_item(item, fallback_tipo=''):
    is_dict = isinstance(item, dict)
    display_image_url = _resolve_item_image(item, fallback_tipo=fallback_tipo)
    normalized = {
        'nombre': getattr(item, 'nombre', '') if not is_dict else item.get('nombre', ''),
        'descripcion': getattr(item, 'descripcion', '') if not is_dict else item.get('descripcion', ''),
        'precio': getattr(item, 'precio', 0) if not is_dict else item.get('precio', 0),
        'destacado': getattr(item, 'destacado', False) if not is_dict else item.get('destacado', False),
        'bodega': getattr(item, 'bodega', '') if not is_dict else item.get('bodega', ''),
        'cepa': getattr(item, 'cepa', '') if not is_dict else item.get('cepa', ''),
        'anno': getattr(item, 'anno', '') if not is_dict else item.get('anno', ''),
        'origen': getattr(item, 'origen', '') if not is_dict else item.get('origen', ''),
        'graduacion': getattr(item, 'graduacion', '') if not is_dict else item.get('graduacion', ''),
        'display_image_url': display_image_url,
        'precio_oferta': item.get('precio_oferta', None) if is_dict else getattr(item, 'precio_oferta', None),
        'tiene_oferta': item.get('tiene_oferta', False) if is_dict else getattr(item, 'tiene_oferta', False),
        'descuento_porcentaje': item.get('descuento_porcentaje', 0) if is_dict else getattr(item, 'descuento_porcentaje', 0),
        'precio_persona': item.get('precio_persona', None) if is_dict else None,
        'min_personas': item.get('min_personas', None) if is_dict else None,
    }
    if normalized['tiene_oferta'] and not normalized['precio_oferta']:
        normalized['precio_oferta'] = normalized['precio']
    return normalized


def _db_categories_for(tipo):
    categorias = CategoriaMenu.objects.filter(tipo=tipo, activa=True).prefetch_related('items')
    categories_with_items = []
    for categoria in categorias:
        normalized_items = [_normalize_item(item, fallback_tipo=tipo) for item in categoria.items.filter(disponible=True)]
        if normalized_items:
            categories_with_items.append({'categoria': categoria, 'items': normalized_items})
    return categories_with_items


def _has_real_menu_data():
    return CategoriaMenu.objects.filter(activa=True, items__isnull=False).exists()


def _categories_for_tipo(tipo):
    db_categories = _db_categories_for(tipo)
    if db_categories:
        return db_categories
    if _has_real_menu_data():
        return []
    return SAMPLE_MENU.get(tipo, [])


def _menu_sections():
    sections = []
    for tipo, meta in SECTION_META.items():
        categorias = _categories_for_tipo(tipo)
        item_count = sum(len(categoria['items']) for categoria in categorias)
        sections.append({
            'tipo': tipo,
            'label': meta['label'],
            'icon': meta['icon'],
            'count': item_count,
        })
    return sections


def _destacados_por_tipo():
    destacados = {}
    for tipo in SECTION_META:
        items = []
        for categoria in _categories_for_tipo(tipo):
            items.extend(categoria['items'])
        featured = [item for item in items if item.get('destacado')]
        destacados[tipo] = (featured or items)[:3]
    return destacados


def _ofertas_para_home():
    offers = []
    for tipo in SECTION_META:
        for categoria in _categories_for_tipo(tipo):
            for item in categoria['items']:
                if item.get('tiene_oferta') or item.get('destacado'):
                    offers.append({
                        **item,
                        'categoria': {
                            'tipo': tipo,
                            'get_tipo_display': SECTION_META[tipo]['label'],
                        },
                    })
    if not offers:
        return [], [], []
    return offers[:3], offers[3:6], offers[:6]


def carta_home(request):
    secciones = _menu_sections()
    ofertas_izq, ofertas_der, ofertas_carrusel = _ofertas_para_home()
    return render(request, 'menu/carta_home.html', {
        'secciones': secciones,
        'destacados': _destacados_por_tipo(),
        'ofertas_izq': ofertas_izq,
        'ofertas_der': ofertas_der,
        'ofertas_carrusel': ofertas_carrusel,
        'total_almuerzo': next((s['count'] for s in secciones if s['tipo'] == 'almuerzo'), 0),
        'total_cena': next((s['count'] for s in secciones if s['tipo'] == 'cena'), 0),
        'total_terraza': next((s['count'] for s in secciones if s['tipo'] == 'terraza'), 0),
        'total_vinos': next((s['count'] for s in secciones if s['tipo'] == 'vinos'), 0),
        'total_licores': next((s['count'] for s in secciones if s['tipo'] == 'licores'), 0),
    })


def carta_completa(request):
    secciones_menu = []
    for tipo, meta in SECTION_META.items():
        categorias = _categories_for_tipo(tipo)
        if categorias:
            secciones_menu.append({
                'tipo': tipo,
                'label': meta['label'],
                'categorias': categorias,
            })
    return render(request, 'menu/carta_completa.html', {'secciones_menu': secciones_menu})


def _carta_tipo(request, tipo):
    categorias = _categories_for_tipo(tipo)
    return render(request, f'menu/secciones/{tipo}.html', {
        'categorias': categorias,
        'tipo': tipo,
        'tipo_label': SECTION_META[tipo]['label'],
    })


def carta_desayuno(request):
    return _carta_tipo(request, 'desayuno')


def carta_brunch(request):
    return _carta_tipo(request, 'brunch')


def carta_almuerzo(request):
    return _carta_tipo(request, 'almuerzo')


def carta_postres(request):
    return _carta_tipo(request, 'postres')


def carta_infantil(request):
    return _carta_tipo(request, 'infantil')


def carta_te_cafe(request):
    return _carta_tipo(request, 'te_cafe')


def carta_bebidas(request):
    return _carta_tipo(request, 'bebidas')


def carta_llevar(request):
    return _carta_tipo(request, 'llevar')


def carta_cena(request):
    return _carta_tipo(request, 'cena')


def carta_terraza(request):
    return _carta_tipo(request, 'terraza')


def carta_vinos(request):
    return _carta_tipo(request, 'vinos')


def carta_licores(request):
    return _carta_tipo(request, 'licores')


def carta_cocteles(request):
    return _carta_tipo(request, 'cocteles')


def carta_catering(request):
    return _carta_tipo(request, 'catering')


@staff_member_required
def panel_menu(request):
    stats = {}
    for tipo, label in CategoriaMenu.TIPO_CHOICES:
        stats[tipo] = {
            'label': label,
            'categorias': CategoriaMenu.objects.filter(tipo=tipo).count(),
            'items': ItemMenu.objects.filter(categoria__tipo=tipo).count(),
            'disponibles': ItemMenu.objects.filter(categoria__tipo=tipo, disponible=True).count(),
            'ofertas': ItemMenu.objects.filter(categoria__tipo=tipo, tiene_oferta=True).count(),
        }
    return render(request, 'menu/panel/dashboard.html', {'stats': stats})


@staff_member_required
def panel_items(request):
    tipo = request.GET.get('tipo', '')
    q = request.GET.get('q', '')
    items = ItemMenu.objects.select_related('categoria').all().order_by('categoria__tipo', 'categoria__nombre', 'nombre')
    if tipo:
        items = items.filter(categoria__tipo=tipo)
    if q:
        items = items.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(categoria__nombre__icontains=q) |
            Q(categoria__tipo__icontains=q)
        )
    return render(request, 'menu/panel/items.html', {
        'items': items,
        'tipo_sel': tipo,
        'q': q,
        'tipo_choices': CategoriaMenu.TIPO_CHOICES,
    })


@staff_member_required
def panel_item_crear(request):
    form = ItemMenuForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save()
        if item.imagen:
            _optimizar_imagen(item.imagen.path)
        messages.success(request, f'"{item.nombre}" creado.')
        return redirect('menu:panel_items')
    return render(request, 'menu/panel/item_form.html', {'form': form, 'titulo': 'Nuevo Item'})


@staff_member_required
def panel_item_editar(request, pk):
    item = get_object_or_404(ItemMenu, pk=pk)
    form = ItemMenuForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        item = form.save()
        if item.imagen:
            _optimizar_imagen(item.imagen.path)
        messages.success(request, f'"{item.nombre}" actualizado.')
        return redirect('menu:panel_items')
    return render(request, 'menu/panel/item_form.html', {
        'form': form,
        'titulo': f'Editar: {item.nombre}',
        'item': item,
    })


@staff_member_required
def panel_item_eliminar(request, pk):
    item = get_object_or_404(ItemMenu, pk=pk)
    if request.method == 'POST':
        nombre = item.nombre
        item.delete()
        messages.success(request, f'"{nombre}" eliminado.')
        return redirect('menu:panel_items')
    return render(request, 'menu/panel/confirmar_eliminar.html', {'objeto': item, 'tipo': 'Item'})


@staff_member_required
def panel_categorias(request):
    categorias = CategoriaMenu.objects.all()
    return render(request, 'menu/panel/categorias.html', {'categorias': categorias})


@staff_member_required
def panel_categoria_crear(request):
    form = CategoriaMenuForm(request.POST or None)
    if form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoria "{categoria.nombre}" creada.')
        return redirect('menu:panel_categorias')
    return render(request, 'menu/panel/categoria_form.html', {'form': form, 'titulo': 'Nueva Categoria'})


@staff_member_required
def panel_categoria_editar(request, pk):
    categoria = get_object_or_404(CategoriaMenu, pk=pk)
    form = CategoriaMenuForm(request.POST or None, instance=categoria)
    if form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoria "{categoria.nombre}" actualizada.')
        return redirect('menu:panel_categorias')
    return render(request, 'menu/panel/categoria_form.html', {
        'form': form,
        'titulo': f'Editar Categoria: {categoria.nombre}',
        'categoria': categoria,
    })


@staff_member_required
def panel_categoria_eliminar(request, pk):
    categoria = get_object_or_404(CategoriaMenu, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoria "{nombre}" eliminada.')
        return redirect('menu:panel_categorias')
    return render(request, 'menu/panel/confirmar_eliminar.html', {'objeto': categoria, 'tipo': 'Categoria'})


def _optimizar_imagen(path):
    try:
        img = Image.open(path)
        img = img.convert('RGB')
        img.thumbnail((800, 800))
        img.save(path, 'JPEG', quality=85, optimize=True)
    except Exception:
        pass
