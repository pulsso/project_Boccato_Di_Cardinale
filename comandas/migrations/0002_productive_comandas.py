from django.db import migrations, models
from django.utils import timezone


def populate_daily_numbers(apps, schema_editor):
    Comanda = apps.get_model('comandas', 'Comanda')
    ComandaSequence = apps.get_model('comandas', 'ComandaSequence')

    grouped = {}
    for comanda in Comanda.objects.all().order_by('creada_at', 'id'):
        fecha = timezone.localtime(comanda.creada_at).date() if comanda.creada_at else timezone.localdate()
        grouped.setdefault(fecha, 0)
        grouped[fecha] += 1
        comanda.fecha_operacion = fecha
        comanda.numero_dia = grouped[fecha]
        comanda.save(update_fields=['fecha_operacion', 'numero_dia'])

    for fecha, ultimo_numero in grouped.items():
        ComandaSequence.objects.update_or_create(
            fecha=fecha,
            defaults={'ultimo_numero': ultimo_numero},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('comandas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComandaSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(unique=True)),
                ('ultimo_numero', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Secuencia diaria de comanda',
                'verbose_name_plural': 'Secuencias diarias de comanda',
            },
        ),
        migrations.AddField(
            model_name='comanda',
            name='fecha_operacion',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='comanda',
            name='numero_dia',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='itemcomanda',
            name='entregado_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itemcomanda',
            name='listo_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itemcomanda',
            name='preparando_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(populate_daily_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='comanda',
            name='fecha_operacion',
            field=models.DateField(db_index=True, default=timezone.localdate),
        ),
        migrations.AddConstraint(
            model_name='comanda',
            constraint=models.UniqueConstraint(fields=('fecha_operacion', 'numero_dia'), name='unique_comanda_numero_por_dia'),
        ),
    ]
