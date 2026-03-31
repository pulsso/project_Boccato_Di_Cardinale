from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image

from .forms import CategoriaMenuForm, ItemMenuForm
from .models import CategoriaMenu, ItemMenu


SECTION_META = {
    'desayuno': {'label': 'Desayuno', 'icon': '☕'},
    'brunch': {'label': 'Brunch & Once', 'icon': '🥐'},
    'almuerzo': {'label': 'Almuerzo', 'icon': '🍽️'},
    'cena': {'label': 'Cena', 'icon': '🌙'},
    'terraza': {'label': 'Terraza', 'icon': '🌿'},
    'vinos': {'label': 'Vinos', 'icon': '🍷'},
    'licores': {'label': 'Licores', 'icon': '🥃'},
    'cocteles': {'label': 'Cocteles', 'icon': '🍸'},
    'catering': {'label': 'Catering', 'icon': '🎉'},
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
                {
                    'nombre': 'Bowl de frutas y granola',
                    'descripcion': 'Yogurt natural, frutas frescas de temporada, miel y granola tostada.',
                    'precio': 6200,
                    'display_image_url': 'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=900&q=80',
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
                {
                    'nombre': 'Tabla Brunch Boccato',
                    'descripcion': 'Mini quiches, quesos suaves, charcuteria, frutas y pan de masa madre.',
                    'precio': 14900,
                    'display_image_url': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=900&q=80',
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
                {
                    'nombre': 'Salmon grillado',
                    'descripcion': 'Pure de coliflor, verduras al horno y salsa de limon.',
                    'precio': 17600,
                    'display_image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=900&q=80',
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
                {
                    'nombre': 'Ravioles de ricotta y espinaca',
                    'descripcion': 'Masa fresca, salsa pomodoro asada y albahaca.',
                    'precio': 14900,
                    'display_image_url': 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=900&q=80',
                },
                {
                    'nombre': 'Merluza austral confitada',
                    'descripcion': 'Cuscus de verduras y mantequilla blanca al cilantro.',
                    'precio': 16900,
                    'display_image_url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=900&q=80',
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
                {
                    'nombre': 'Bruschettas surtidas',
                    'descripcion': 'Tomate confitado, pesto, stracciatella y jamon serrano.',
                    'precio': 7900,
                    'display_image_url': 'https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?w=900&q=80',
                },
                {
                    'nombre': 'Empanaditas gourmet',
                    'descripcion': 'Mix de plateada al vino, queso azul con cebolla y pino suave.',
                    'precio': 7200,
                    'display_image_url': 'https://images.unsplash.com/photo-1529042410759-befb1204b468?w=900&q=80',
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
                {
                    'nombre': 'Sauvignon Blanc',
                    'descripcion': 'Notas citricas, mineralidad y final fresco.',
                    'precio': 14900,
                    'bodega': 'Casa Costa',
                    'cepa': 'Sauvignon Blanc',
                    'anno': '2023',
                    'origen': 'Casablanca',
                    'display_image_url': 'https://images.unsplash.com/photo-1562601579-599dec564e06?w=900&q=80',
                },
                {
                    'nombre': 'Rose Brut',
                    'descripcion': 'Espumante seco para aperitivo o brunch.',
                    'precio': 18900,
                    'bodega': 'Valle Espumante',
                    'cepa': 'Blend',
                    'anno': '2023',
                    'origen': 'Limari',
                    'display_image_url': 'https://images.unsplash.com/photo-1558008258-3256797b43f3?w=900&q=80',
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
                {
                    'nombre': 'Pisco reservado',
                    'descripcion': 'Servicio clasico para degustacion o sour premium.',
                    'precio': 6900,
                    'bodega': 'Mistral',
                    'graduacion': '35%',
                    'display_image_url': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=900&q=80',
                },
                {
                    'nombre': 'Gin botanico',
                    'descripcion': 'Perfume herbal y citrico, ideal para gin tonic.',
                    'precio': 7900,
                    'bodega': 'Botanic London',
                    'graduacion': '40%',
                    'display_image_url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=900&q=80',
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
                {
                    'nombre': 'Aperol Spritz',
                    'descripcion': 'Aperol, espumante, soda y rodaja de naranja.',
                    'precio': 7200,
                    'display_image_url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=900&q=80',
                },
                {
                    'nombre': 'Negroni Boccato',
                    'descripcion': 'Gin, vermut rosso, campari y piel de naranja.',
                    'precio': 7900,
                    'display_image_url': 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=900&q=80',
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
                {
                    'nombre': 'Brunch Corporativo',
                    'descripcion': 'Buffet frio, huevos, frutas, bolleria y espumante sin alcohol.',
                    'precio': 16900,
                    'precio_persona': 16900,
                    'min_personas': 12,
                    'display_image_url': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=900&q=80',
                },
                {
                    'nombre': 'Cocktail Premium',
                    'descripcion': 'Canapes, bocados calientes, barra y personal de servicio.',
                    'precio': 24900,
                    'precio_persona': 24900,
                    'min_personas': 20,
                    'display_image_url': 'https://images.unsplash.com/photo-1519167758481-83f29c2117e0?w=900&q=80',
                },
            ],
        },
    ],
}


def _normalize_item(item):
    is_dict = isinstance(item, dict)
    display_image_url = getattr(item, 'display_image_url', '') if not is_dict else item.get('display_image_url', '')
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
        'precio_oferta': item.get('precio_oferta', None) if is_dict else None,
        'tiene_oferta': item.get('tiene_oferta', False) if is_dict else False,
        'descuento_porcentaje': item.get('descuento_porcentaje', 0) if is_dict else 0,
        'precio_persona': item.get('precio_persona', None) if is_dict else None,
        'min_personas': item.get('min_personas', None) if is_dict else None,
    }
    if normalized['tiene_oferta'] and not normalized['precio_oferta']:
        normalized['precio_oferta'] = normalized['precio']
    return normalized


def _db_categories_for(tipo):
    try:
        categorias = CategoriaMenu.objects.filter(tipo=tipo, activa=True).prefetch_related('items')
        categories_with_items = []
        for categoria in categorias:
            normalized_items = [_normalize_item(item) for item in categoria.items.filter(disponible=True)]
            if normalized_items:
                categories_with_items.append({'categoria': categoria, 'items': normalized_items})
        return categories_with_items
    except Exception:
        return []


def _sample_categories_for(tipo):
    return SAMPLE_MENU.get(tipo, [])


def _categories_for_tipo(tipo):
    return _db_categories_for(tipo) or _sample_categories_for(tipo)


def _menu_sections():
    sections = []
    for tipo in SECTION_META:
        categorias = _categories_for_tipo(tipo)
        item_count = sum(len(categoria['items']) for categoria in categorias)
        sections.append({
            'tipo': tipo,
            'label': SECTION_META[tipo]['label'],
            'icon': SECTION_META[tipo]['icon'],
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
    template = f'menu/secciones/{tipo}.html'
    return render(request, template, {
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
        }
    return render(request, 'catalog/panel/dashboard.html', {'stats': stats})


@staff_member_required
def panel_items(request):
    tipo = request.GET.get('tipo', '')
    q = request.GET.get('q', '')
    items = ItemMenu.objects.select_related('categoria').all()
    if tipo:
        items = items.filter(categoria__tipo=tipo)
    if q:
        items = items.filter(nombre__icontains=q)
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
