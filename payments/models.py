from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models, transaction

from orders.models import Order


class PaymentSequence(models.Model):
    last_number = models.PositiveBigIntegerField(default=0)
    last_rejection_number = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = 'Secuencia de pagos'
        verbose_name_plural = 'Secuencias de pagos'

    @classmethod
    def next_number(cls):
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(pk=1)
            seq.last_number += 1
            seq.save(update_fields=['last_number'])
            return seq.last_number

    @classmethod
    def next_rejection_number(cls):
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(pk=1)
            seq.last_rejection_number += 1
            seq.save(update_fields=['last_rejection_number'])
            return seq.last_rejection_number


class TreasuryAuthorizationSettings(models.Model):
    approval_code_hash = models.CharField(max_length=255, blank=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='updated_treasury_codes'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Seguridad Tesoreria'
        verbose_name_plural = 'Seguridad Tesoreria'

    @classmethod
    def get_solo(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings

    @property
    def has_code(self):
        return bool(self.approval_code_hash)

    def set_code(self, raw_code, updated_by=None):
        self.approval_code_hash = make_password(raw_code)
        self.updated_by = updated_by
        self.save(update_fields=['approval_code_hash', 'updated_by', 'updated_at'])

    def verify_code(self, raw_code):
        if not self.approval_code_hash:
            return False
        return check_password(raw_code, self.approval_code_hash)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]

    PAYMENT_METHODS = [
        ('stripe', 'Tarjeta de credito/debito'),
        ('transfer', 'Transferencia bancaria'),
        ('cash', 'Efectivo'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_store_payments'
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='stripe')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=200, blank=True)
    treasury_number = models.PositiveBigIntegerField(unique=True, null=True, blank=True)
    rejection_number = models.PositiveBigIntegerField(unique=True, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_notified_at = models.DateTimeField(null=True, blank=True)
    dispatch_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago #{self.id} - Orden #{self.order.id} - {self.get_status_display()}'

    @property
    def treasury_number_display(self):
        if not self.treasury_number:
            return ''
        return f'{self.treasury_number:08d}'

    @property
    def rejection_code_display(self):
        if not self.rejection_number:
            return ''
        return f'RCHZ {self.rejection_number:07d}'

    @property
    def validation_reference_display(self):
        return self.treasury_number_display or self.rejection_code_display or ''


class PaymentValidationLog(models.Model):
    ACTION_CHOICES = [
        ('submitted', 'Transferencia informada'),
        ('approved', 'Pago aprobado'),
        ('rejected', 'Pago rechazado'),
        ('dispatch_notified', 'Despacho notificado'),
        ('customer_notified', 'Cliente notificado'),
        ('dispatch_updated', 'Despacho actualizado'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='validation_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='payment_validation_logs'
    )
    code = models.CharField(max_length=32, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historial validacion pago'
        verbose_name_plural = 'Historial validaciones pago'

    def __str__(self):
        return f'{self.payment_id} - {self.action}'
