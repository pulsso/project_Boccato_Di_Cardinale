# Generated manually for storefront improvements.

from django.db import migrations, models


def create_sample_products(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Product = apps.get_model('catalog', 'Product')

    cafe_cat, _ = Category.objects.get_or_create(
        slug='cafes-gourmet',
        defaults={
            'name': 'Cafes Gourmet',
            'description': 'Seleccion de cafes de origen y especialidad.',
            'active': True,
        },
    )
    dulce_cat, _ = Category.objects.get_or_create(
        slug='dulces-de-autor',
        defaults={
            'name': 'Dulces de Autor',
            'description': 'Pasteleria y chocolates seleccionados.',
            'active': True,
        },
    )

    Product.objects.get_or_create(
        slug='cafe-de-origen-boccato',
        defaults={
            'category': cafe_cat,
            'name': 'Cafe de Origen Boccato 500g',
            'description': 'Blend de granos seleccionados, tostado medio, ideal para espresso o prensa francesa.',
            'price': 12990,
            'stock': 18,
            'external_image_url': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=1200&q=80',
            'available': True,
            'featured': True,
        },
    )

    Product.objects.get_or_create(
        slug='caja-chocolates-boutique',
        defaults={
            'category': dulce_cat,
            'name': 'Caja Chocolates Boutique x12',
            'description': 'Seleccion de bombones artesanales y chocolates de autor para regalo o sobremesa.',
            'price': 14990,
            'stock': 10,
            'external_image_url': 'https://images.unsplash.com/photo-1481391319762-47dff72954d9?w=1200&q=80',
            'available': True,
            'featured': True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_galeriafoto_product_featured_campana_historialcambio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='external_image_url',
            field=models.URLField(blank=True, verbose_name='Imagen externa (URL)'),
        ),
        migrations.RunPython(create_sample_products, migrations.RunPython.noop),
    ]
