from django.db import migrations


ADDITIONAL_MENU = {
    'te_cafe': {
        'categoria': 'Te - Cafe e Infusiones',
        'items': [
            ('Espresso Boccato', 'Cafe de especialidad de tueste medio servido corto.', 2800, True, None, True),
            ('Cappuccino de la casa', 'Leche texturizada, espresso doble y cacao suave.', 3900, False, None, True),
            ('Te premium en tetera', 'Seleccion Earl Grey, chai, jazmin o frutos rojos.', 3600, False, None, True),
            ('Infusion de hierbas del huerto', 'Menta, cedron, manzanilla y jengibre segun disponibilidad.', 3400, False, None, True),
        ],
    },
    'bebidas': {
        'categoria': 'Bebidas y Cervezas',
        'items': [
            ('Jugo natural del dia', 'Preparado al momento con fruta fresca de temporada.', 4200, False, None, True),
            ('Soda Boccato citrus', 'Receta propia con limon, romero, miel y agua gasificada.', 4300, True, None, True),
            ('Shop lager artesanal', 'Formato shop bien frio con espuma cremosa.', 4900, False, None, True),
            ('Cerveza artesanal botella', 'IPA, amber ale o stout de productores locales.', 5400, False, None, True),
            ('Bebida de fantasia', 'Linea clasica, zero o ginger ale.', 2600, False, None, True),
        ],
    },
    'llevar': {
        'categoria': 'Para Llevar y Boutique',
        'items': [
            ('Caja termica premium', 'Caja rigida para despacho o picnic gourmet.', 14900, False, None, True),
            ('Set cubiertos biodegradables', 'Tenedor, cuchara, cuchillo de corte y servilleta.', 1800, False, None, True),
            ('Chimichurri Boccato', 'Receta propia en frasco para carnes y vegetales.', 5200, False, None, True),
            ('Sal de mar Boccato gourmet', 'Blend de sales con hierbas y citricos.', 4600, False, None, True),
            ('Tabla de corte Boccato', 'Tabla de madera para servicio, asado o regalo.', 18900, False, None, True),
            ('Tarjeta VIP Terraza y Show', 'Beneficio de 20% de descuento en terraza y show en vivo.', 25000, True, None, True),
        ],
    },
}


def seed_additional_sections(apps, schema_editor):
    CategoriaMenu = apps.get_model('menu', 'CategoriaMenu')
    ItemMenu = apps.get_model('menu', 'ItemMenu')

    base_order = CategoriaMenu.objects.count() + 1
    for offset, (tipo, payload) in enumerate(ADDITIONAL_MENU.items(), start=0):
        categoria, _ = CategoriaMenu.objects.get_or_create(
            tipo=tipo,
            nombre=payload['categoria'],
            defaults={'orden': base_order + offset, 'activa': True},
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
        ('menu', '0006_seed_initial_menu'),
    ]

    operations = [
        migrations.RunPython(seed_additional_sections, migrations.RunPython.noop),
    ]
