from django.db import models
from django.contrib.auth.models import User
from menu.models import ItemMenu


class Mesa(models.Model):
    ZONA_CHOICES = [
        ('salon', 'Salón Principal'),
        ('terraza', 'Terraza'),
        ('vip', 'Salón VIP'),
        ('barra', 'Barra'),
    ]
    numero = models.PositiveIntegerField(unique=True)
    zona = models.CharField(max_length=20, choices=ZONA_CHOICES, default='salon')
    capacidad = models.PositiveIntegerField(default=4)
    activa = models.BooleanField(default=True)
    # Posición en el layout visual
    pos_x = models.PositiveIntegerField(default=0, help_text='Posición X en el layout')
    pos_y = models.PositiveIntegerField(default=0, help_text='Posición Y en el layout')

    class Meta:
        ordering = ['zona', 'numero']
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'

    def __str__(self):
        return f'Mesa {self.numero} — {self.get_zona_display()}'

    def tiene_comanda_activa(self):
        return self.comandas.filter(estado__in=['abierta', 'en_proceso']).exists()

    def comanda_activa(self):
        return self.comandas.filter(estado__in=['abierta', 'en_proceso']).first()


class Comanda(models.Model):
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('en_proceso', 'En Proceso'),
        ('lista', 'Lista para servir'),
        ('cerrada', 'Cerrada'),
        ('cancelada', 'Cancelada'),
    ]
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='comandas')
    garzon = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comandas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierta')
    notas = models.TextField(blank=True)
    num_comensales = models.PositiveIntegerField(default=1)
    creada_at = models.DateTimeField(auto_now_add=True)
    actualizada_at = models.DateTimeField(auto_now=True)
    cerrada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creada_at']
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'

    def __str__(self):
        return f'Comanda #{self.id} — Mesa {self.mesa.numero} — {self.garzon.get_full_name() or self.garzon.username}'

    def get_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.cantidad for item in self.items.all())


class ItemComanda(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
    ]
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='items')
    item_menu = models.ForeignKey(ItemMenu, on_delete=models.SET_NULL, null=True)
    nombre_item = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, help_text='Ej: sin cebolla, término medio')
    creado_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_at']

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f'{self.cantidad}x {self.nombre_item} — Mesa {self.comanda.mesa.numero}'


class PerfilGarzon(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_garzon')
    activo = models.BooleanField(default=True)
    zona_asignada = models.CharField(max_length=20, choices=Mesa.ZONA_CHOICES, blank=True)
    foto = models.ImageField(upload_to='garzones/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil de Garzón'
        verbose_name_plural = 'Perfiles de Garzones'

    def __str__(self):
        return f'Garzón: {self.usuario.get_full_name() or self.usuario.username}'