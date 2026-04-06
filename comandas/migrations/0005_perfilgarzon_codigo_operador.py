from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comandas', '0004_seed_operational_layout'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilgarzon',
            name='codigo_operador',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='Numero operativo del garzon o bartender para equipos compartidos.',
                null=True,
                unique=True,
            ),
        ),
    ]
