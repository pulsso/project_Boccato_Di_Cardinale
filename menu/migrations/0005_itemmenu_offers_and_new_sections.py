from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_merge_20260330_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoriamenu',
            name='tipo',
            field=models.CharField(choices=[
                ('desayuno', 'Menu Desayuno'),
                ('brunch', 'Brunch y Once'),
                ('almuerzo', 'Menu Almuerzo'),
                ('postres', 'Postres'),
                ('infantil', 'Menu Infantil Dia'),
                ('cena', 'Menu Cena'),
                ('terraza', 'Menu Terraza'),
                ('vinos', 'Carta de Vinos'),
                ('licores', 'Licores y Whiskies'),
                ('cocteles', 'Cocteles'),
                ('catering', 'Catering y Eventos'),
            ], max_length=20),
        ),
        migrations.AddField(
            model_name='itemmenu',
            name='precio_oferta',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='itemmenu',
            name='tiene_oferta',
            field=models.BooleanField(default=False),
        ),
    ]
