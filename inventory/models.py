from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('loss', 'Merma'),
        ('replacement', 'Reemplazo autorizado'),
        ('adjustment', 'Ajuste de inventario'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True)
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'

    def __str__(self):
        return f'{self.get_movement_type_display()} — {self.product.name} ({self.quantity})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        product = self.product
        if self.movement_type == 'in' or self.movement_type == 'replacement':
            product.stock += self.quantity
        elif self.movement_type in ['out', 'loss']:
            product.stock -= self.quantity
        elif self.movement_type == 'adjustment':
            product.stock = self.quantity
        product.save()