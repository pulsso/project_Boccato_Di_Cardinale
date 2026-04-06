from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone

from menu.models import ItemMenu

IVA_RATE = Decimal('0.19')
ONE_HUNDRED = Decimal('100')


class Mesa(models.Model):
    ZONA_CHOICES = [
        ('salon', 'Salon Principal'),
        ('terraza', 'Terraza'),
        ('vip', 'Salon VIP'),
        ('barra', 'Barra'),
    ]

    numero = models.PositiveIntegerField(unique=True)
    zona = models.CharField(max_length=20, choices=ZONA_CHOICES, default='salon')
    capacidad = models.PositiveIntegerField(default=4)
    activa = models.BooleanField(default=True)
    garzon_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mesas_asignadas',
    )
    pos_x = models.PositiveIntegerField(default=0, help_text='Posicion X en el layout')
    pos_y = models.PositiveIntegerField(default=0, help_text='Posicion Y en el layout')

    class Meta:
        ordering = ['zona', 'numero']
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'

    def __str__(self):
        return f'Mesa {self.numero} - {self.get_zona_display()}'

    @property
    def responsable_label(self):
        if self.garzon_asignado:
            return self.garzon_asignado.get_full_name() or self.garzon_asignado.username
        return 'Sin asignar'

    def tiene_comanda_activa(self):
        return self.comandas.filter(estado__in=['abierta', 'en_proceso', 'lista']).exists()

    def comanda_activa(self):
        return self.comandas.filter(estado__in=['abierta', 'en_proceso', 'lista']).first()


class ComandaSequence(models.Model):
    fecha = models.DateField(unique=True)
    ultimo_numero = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Secuencia diaria de comanda'
        verbose_name_plural = 'Secuencias diarias de comanda'

    @classmethod
    def next_for_today(cls):
        today = timezone.localdate()
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(fecha=today)
            sequence.ultimo_numero += 1
            sequence.save(update_fields=['ultimo_numero'])
            return sequence.ultimo_numero


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
    numero_dia = models.PositiveIntegerField(default=0, db_index=True)
    fecha_operacion = models.DateField(default=timezone.localdate, db_index=True)
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
        constraints = [
            models.UniqueConstraint(
                fields=['fecha_operacion', 'numero_dia'],
                name='unique_comanda_numero_por_dia',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.fecha_operacion:
            self.fecha_operacion = timezone.localdate()
        if not self.numero_dia:
            self.numero_dia = ComandaSequence.next_for_today()
        super().save(*args, **kwargs)

    def __str__(self):
        garzon = self.garzon.get_full_name() if self.garzon else 'Sin garzon'
        return f'Comanda {self.folio} - Mesa {self.mesa.numero} - {garzon}'

    @property
    def folio(self):
        return f'{self.fecha_operacion.strftime("%Y%m%d")}-{self.numero_dia:03d}'

    def get_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.cantidad for item in self.items.all())

    def get_net_total(self):
        gross_total = Decimal(self.get_total())
        return (gross_total / (Decimal('1.00') + IVA_RATE)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    def get_tax_amount(self):
        return self.get_total() - self.get_net_total()

    def get_total_with_tax(self):
        return self.get_total()

    def get_suggested_tip(self):
        return (Decimal(self.get_total_with_tax()) * Decimal('0.10')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


class ItemComanda(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
    ]

    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='items')
    item_menu = models.ForeignKey(ItemMenu, on_delete=models.SET_NULL, null=True)
    agregado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_agregados_comanda',
    )
    nombre_item = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, help_text='Ej: sin cebolla, termino medio')
    creado_at = models.DateTimeField(auto_now_add=True)
    preparando_at = models.DateTimeField(null=True, blank=True)
    listo_at = models.DateTimeField(null=True, blank=True)
    entregado_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['creado_at']
        verbose_name = 'Item de comanda'
        verbose_name_plural = 'Items de comanda'

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def get_net_subtotal(self):
        gross_total = Decimal(self.subtotal())
        return (gross_total / (Decimal('1.00') + IVA_RATE)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    def get_tax_amount(self):
        return self.subtotal() - self.get_net_subtotal()

    def advance_status(self):
        status_flow = ['pendiente', 'preparando', 'listo', 'entregado']
        current_index = status_flow.index(self.estado)
        self.estado = status_flow[(current_index + 1) % len(status_flow)]
        now = timezone.now()
        if self.estado == 'preparando' and not self.preparando_at:
            self.preparando_at = now
        elif self.estado == 'listo' and not self.listo_at:
            self.listo_at = now
        elif self.estado == 'entregado' and not self.entregado_at:
            self.entregado_at = now
        self.save(update_fields=[
            'estado', 'preparando_at', 'listo_at', 'entregado_at',
        ])

    def __str__(self):
        return f'{self.cantidad}x {self.nombre_item} - Mesa {self.comanda.mesa.numero}'


class PerfilGarzon(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_garzon')
    activo = models.BooleanField(default=True)
    codigo_operador = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text='Numero operativo del garzon o bartender para equipos compartidos.',
    )
    pin_acceso_hash = models.CharField(max_length=128, blank=True)
    zona_asignada = models.CharField(max_length=20, choices=Mesa.ZONA_CHOICES, blank=True)
    foto = models.ImageField(upload_to='garzones/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil de garzon'
        verbose_name_plural = 'Perfiles de garzones'

    def __str__(self):
        return f'Garzon: {self.usuario.get_full_name() or self.usuario.username}'

    @property
    def operador_label(self):
        if self.codigo_operador:
            return f'G{self.codigo_operador:02d}'
        return self.usuario.username

    @property
    def tiene_pin(self):
        return bool(self.pin_acceso_hash)

    def set_pin(self, raw_pin):
        self.pin_acceso_hash = make_password(str(raw_pin))

    def check_pin(self, raw_pin):
        if not self.pin_acceso_hash:
            return False
        return check_password(str(raw_pin), self.pin_acceso_hash)
