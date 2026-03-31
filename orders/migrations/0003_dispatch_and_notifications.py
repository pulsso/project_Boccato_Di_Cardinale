# Generated manually for dispatch workflow and notifications.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(blank=True, choices=[('internal', 'Sistema propio'), ('external', 'Delivery externo')], max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_distance_km',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='dispatch_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_minutes',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='sector',
            field=models.CharField(blank=True, choices=[('las-condes', 'Las Condes'), ('providencia', 'Providencia'), ('nunoa', 'Nunoa'), ('vitacura', 'Vitacura'), ('la-reina', 'La Reina'), ('santiago-centro', 'Santiago Centro'), ('maipu', 'Maipu'), ('puente-alto', 'Puente Alto'), ('san-miguel', 'San Miguel'), ('la-florida', 'La Florida')], max_length=30),
        ),
        migrations.AddField(
            model_name='order',
            name='zone',
            field=models.CharField(blank=True, choices=[('norte', 'Santiago Norte'), ('sur', 'Santiago Sur'), ('oriente', 'Santiago Oriente'), ('poniente', 'Santiago Poniente'), ('centro', 'Santiago Centro')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('processing', 'En proceso'), ('shipped', 'En despacho'), ('delivered', 'Entregado'), ('cancelled', 'Cancelado')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='DispatchTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pendiente despacho'), ('assigned', 'Asignado'), ('out_for_delivery', 'En entrega'), ('delivered', 'Entregado')], default='pending', max_length=20)),
                ('delivery_method', models.CharField(blank=True, choices=[('internal', 'Sistema propio'), ('external', 'Delivery externo')], max_length=20)),
                ('estimated_delivery_minutes', models.PositiveSmallIntegerField(default=30)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispatch_tasks', to=settings.AUTH_USER_MODEL)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dispatch_task', to='orders.order')),
            ],
            options={
                'verbose_name': 'Tarea de despacho',
                'verbose_name_plural': 'Tareas de despacho',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_type', models.CharField(choices=[('customer', 'Cliente'), ('dispatch', 'Despacho')], max_length=20)),
                ('channel', models.CharField(choices=[('system', 'Sistema'), ('email', 'Email')], default='system', max_length=20)),
                ('recipient_email', models.EmailField(blank=True, max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='orders.order')),
                ('recipient_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificacion de orden',
                'verbose_name_plural': 'Notificaciones de orden',
                'ordering': ['-created_at'],
            },
        ),
    ]
