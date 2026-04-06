from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_destination_coordinates'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_first_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_landline_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_last_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_mobile_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='ordernotification',
            name='recipient_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='ordernotification',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('closed', 'Cerrado')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='ordernotification',
            name='channel',
            field=models.CharField(choices=[('system', 'Sistema'), ('email', 'Email'), ('whatsapp', 'WhatsApp')], default='system', max_length=20),
        ),
        migrations.AlterField(
            model_name='ordernotification',
            name='recipient_type',
            field=models.CharField(choices=[('customer', 'Cliente'), ('dispatch', 'Despacho'), ('treasury', 'Tesoreria')], max_length=20),
        ),
    ]
