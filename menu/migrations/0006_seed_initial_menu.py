from django.db import migrations


INITIAL_MENU = {
    'desayuno': {
        'categoria': 'Menu Desayuno',
        'items': [
            ('Croissant Boccato', 'Croissant de mantequilla, mermelada de frutos rojos y cafe de especialidad.', 6900, True, 5900, True),
            ('Tostadas con palta y huevos', 'Pan artesanal, palta hass, huevos pochados y aceite de oliva.', 7900, False, None, True),
        ],
    },
    'brunch': {
        'categoria': 'Brunch y Once',
        'items': [
            ('Huevos Benedictinos', 'Muffin ingles, jamon serrano, salsa holandesa y brotes frescos.', 8900, True, None, True),
            ('French Toast Brioche', 'Pan brioche, frutas del bosque, crema chantilly y syrup de maple.', 8400, False, None, True),
        ],
    },
    'almuerzo': {
        'categoria': 'Menu Almuerzo',
        'items': [
            ('Crema de zapallo asado', 'Con aceite de oliva, semillas tostadas y queso de cabra.', 5900, False, None, True),
            ('Risotto de champinones', 'Arroz arborio, parmesano, hongos salteados y toque de trufa.', 11900, True, 10900, True),
        ],
    },
    'postres': {
        'categoria': 'Postres',
        'items': [
            ('Tiramisu Boccato', 'Crema de mascarpone, bizcocho de cafe y cacao amargo.', 6200, True, None, True),
            ('Cheesecake de frutos rojos', 'Base crocante, queso crema y salsa de berries.', 5900, False, None, True),
        ],
    },
    'infantil': {
        'categoria': 'Menu Infantil Dia',
        'items': [
            ('Mini pasta pomodoro', 'Pasta corta con salsa de tomate suave y queso rallado.', 5900, False, None, True),
            ('Pollo crispy con papas', 'Tiras de pollo apanado, papas rusticas y jugo pequeno.', 6900, True, None, True),
        ],
    },
    'cena': {
        'categoria': 'Menu Cena',
        'items': [
            ('Lomo vetado al romero', 'Papas rusticas, reduccion de vino tinto y mantequilla de hierbas.', 18900, True, None, True),
        ],
    },
    'terraza': {
        'categoria': 'Menu Terraza',
        'items': [
            ('Tabla Boccato', 'Quesos seleccionados, charcuteria, frutos secos y panes tostados.', 15900, True, None, True),
        ],
    },
    'vinos': {
        'categoria': 'Carta de Vinos',
        'items': [
            ('Cabernet Sauvignon Reserva', 'Vino tinto elegante de taninos suaves.', 16900, False, None, True),
        ],
    },
    'licores': {
        'categoria': 'Licores y Whiskies',
        'items': [
            ('Whisky 12 anos', 'Notas a vainilla, caramelo y roble tostado.', 8900, False, None, True),
        ],
    },
    'cocteles': {
        'categoria': 'Cocteles',
        'items': [
            ('Pisco Sour Premium', 'Pisco reservado, limon sutil, syrup y angostura.', 6900, True, None, True),
        ],
    },
    'catering': {
        'categoria': 'Catering y Eventos',
        'items': [
            ('Coffee Break Ejecutivo', 'Cafe premium, mini pasteleria, jugos y sandwiches.', 12900, False, None, True),
        ],
    },
}


def seed_menu(apps, schema_editor):
    CategoriaMenu = apps.get_model('menu', 'CategoriaMenu')
    ItemMenu = apps.get_model('menu', 'ItemMenu')

    if ItemMenu.objects.exists():
        return

    for order, (tipo, payload) in enumerate(INITIAL_MENU.items(), start=1):
        categoria, _ = CategoriaMenu.objects.get_or_create(
            tipo=tipo,
            nombre=payload['categoria'],
            defaults={'orden': order, 'activa': True},
        )
        for item_order, (nombre, descripcion, precio, destacado, precio_oferta, disponible) in enumerate(payload['items'], start=1):
            ItemMenu.objects.get_or_create(
                categoria=categoria,
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'precio': precio,
                    'destacado': destacado,
                    'precio_oferta': precio_oferta,
                    'tiene_oferta': bool(precio_oferta),
                    'disponible': disponible,
                    'orden': item_order,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ('menu', '0005_itemmenu_offers_and_new_sections'),
    ]

    operations = [
        migrations.RunPython(seed_menu, migrations.RunPython.noop),
    ]
