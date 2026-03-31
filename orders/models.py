from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from catalog.models import Product
from config.commerce import (
    EXTERNAL_DELIVERY_PERCENTAGE,
    INTERNAL_DELIVERY_FEE_ABOVE_10KM,
    SECTOR_CHOICES,
    ZONE_CHOICES,
)

IVA_RATE = Decimal('0.19')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'En proceso'),
        ('shipped', 'En despacho'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('internal', 'Sistema propio'),
        ('external', 'Delivery externo'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    stripe_payment_id = models.CharField(max_length=200, blank=True)
    paid = models.BooleanField(default=False)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True)
    sector = models.CharField(max_length=30, choices=SECTOR_CHOICES, blank=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, blank=True)
    delivery_distance_km = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    estimated_delivery_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    dispatch_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'

    def __str__(self):
        return f'Orden #{self.id} - {self.user.username}'

    @property
    def folio(self):
        return self.created_at.strftime('BOC-%Y%m%d-%H%M%S')

    def get_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def get_net_total(self):
        return self.get_total()

    def get_tax_amount(self):
        return (self.get_net_total() * IVA_RATE).quantize(Decimal('0.01'))

    def calculate_delivery_fee(self):
        distance = self.delivery_distance_km or Decimal('0')
        if self.delivery_method == 'internal' and distance > Decimal('10'):
            extra_km = max(distance - Decimal('10'), Decimal('0'))
            return INTERNAL_DELIVERY_FEE_ABOVE_10KM + (extra_km * Decimal('1200')).quantize(Decimal('1'))
        if self.delivery_method == 'external':
            return (self.get_net_total() * EXTERNAL_DELIVERY_PERCENTAGE).quantize(Decimal('1'))
        return Decimal('0')

    def get_delivery_fee(self):
        if self.delivery_fee:
            return Decimal(self.delivery_fee)
        return self.calculate_delivery_fee()

    def get_total_with_tax(self):
        return self.get_net_total() + self.get_tax_amount()

    def get_grand_total(self):
        return self.get_total_with_tax() + self.get_delivery_fee()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def subtotal_with_tax(self):
        return self.subtotal() * Decimal('1.19')

    def __str__(self):
        return f'{self.quantity} x {self.product}'


class DispatchTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente despacho'),
        ('assigned', 'Asignado'),
        ('out_for_delivery', 'En entrega'),
        ('delivered', 'Entregado'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='dispatch_task')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dispatch_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=20, choices=Order.DELIVERY_METHOD_CHOICES, blank=True)
    estimated_delivery_minutes = models.PositiveSmallIntegerField(default=30)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tarea de despacho'
        verbose_name_plural = 'Tareas de despacho'

    def __str__(self):
        return f'Despacho orden #{self.order_id}'


class OrderNotification(models.Model):
    RECIPIENT_CHOICES = [
        ('customer', 'Cliente'),
        ('dispatch', 'Despacho'),
    ]

    CHANNEL_CHOICES = [
        ('system', 'Sistema'),
        ('email', 'Email'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='system')
    recipient_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_notifications'
    )
    recipient_email = models.EmailField(blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificacion de orden'
        verbose_name_plural = 'Notificaciones de orden'

    def __str__(self):
        return f'{self.order_id} - {self.subject}'
