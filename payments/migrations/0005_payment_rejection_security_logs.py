# Generated manually for treasury approval security and validation logs.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_dispatch_and_notifications'),
        ('payments', '0004_alter_payment_method'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentsequence',
            name='last_rejection_number',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='payment',
            name='customer_notified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='dispatch_notified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='rejection_number',
            field=models.PositiveBigIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='TreasuryAuthorizationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_code_hash', models.CharField(blank=True, max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_treasury_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Seguridad Tesoreria',
                'verbose_name_plural': 'Seguridad Tesoreria',
            },
        ),
        migrations.CreateModel(
            name='PaymentValidationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('submitted', 'Transferencia informada'), ('approved', 'Pago aprobado'), ('rejected', 'Pago rechazado'), ('dispatch_notified', 'Despacho notificado'), ('customer_notified', 'Cliente notificado'), ('dispatch_updated', 'Despacho actualizado')], max_length=30)),
                ('code', models.CharField(blank=True, max_length=32)),
                ('detail', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_validation_logs', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='validation_logs', to='payments.payment')),
            ],
            options={
                'verbose_name': 'Historial validacion pago',
                'verbose_name_plural': 'Historial validaciones pago',
                'ordering': ['-created_at'],
            },
        ),
    ]
