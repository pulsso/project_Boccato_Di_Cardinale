# Generated manually for customer profile analytics.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone', models.CharField(blank=True, choices=[('norte', 'Santiago Norte'), ('sur', 'Santiago Sur'), ('oriente', 'Santiago Oriente'), ('poniente', 'Santiago Poniente'), ('centro', 'Santiago Centro')], max_length=20)),
                ('sector', models.CharField(blank=True, choices=[('las-condes', 'Las Condes'), ('providencia', 'Providencia'), ('nunoa', 'Nunoa'), ('vitacura', 'Vitacura'), ('la-reina', 'La Reina'), ('santiago-centro', 'Santiago Centro'), ('maipu', 'Maipu'), ('puente-alto', 'Puente Alto'), ('san-miguel', 'San Miguel'), ('la-florida', 'La Florida')], max_length=30)),
                ('default_address', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil cliente',
                'verbose_name_plural': 'Perfiles cliente',
            },
        ),
    ]
