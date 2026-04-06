from django.db import migrations


def seed_operational_layout(apps, schema_editor):
    Mesa = apps.get_model('comandas', 'Mesa')

    defaults = []

    for index in range(15):
        defaults.append({
            'numero': index + 1,
            'zona': 'salon',
            'capacidad': 4,
            'activa': True,
            'pos_x': index % 5,
            'pos_y': index // 5,
        })

    for index in range(10):
        defaults.append({
            'numero': 101 + index,
            'zona': 'barra',
            'capacidad': 1,
            'activa': True,
            'pos_x': index,
            'pos_y': 0,
        })

    for index in range(25):
        defaults.append({
            'numero': 201 + index,
            'zona': 'terraza',
            'capacidad': 4,
            'activa': True,
            'pos_x': index % 5,
            'pos_y': index // 5,
        })

    for mesa_data in defaults:
        Mesa.objects.get_or_create(numero=mesa_data['numero'], defaults=mesa_data)


class Migration(migrations.Migration):

    dependencies = [
        ('comandas', '0003_alter_itemcomanda_options_alter_perfilgarzon_options_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_operational_layout, migrations.RunPython.noop),
    ]
