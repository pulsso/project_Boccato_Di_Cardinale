# Generated manually for Google Maps routing support.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_dispatch_and_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='destination_latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='destination_longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
