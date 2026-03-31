from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from comandas.models import Comanda


class PerfilCaja(models.Model):
    ROL_CHOICES = [
        ('cajero', 'Cajero'),
        ('tesorero', 'Tesorero'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_caja')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cajero')
    activo = models.BooleanField(default=True)
    creado_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de Caja'
        verbose_name_plural = 'Perfiles de Caja'

    def __str__(self):
        return f'{self.get_rol_display()}: {self.usuario.get_full_name() or self.usuario.username}'

    def es_cajero(self):
        return self.rol == 'cajero'

    def es_tesorero(self):
        return self.rol == 'tesorero'


class SecuenciaTransaccion(models.Model):
    """Contador global atomico — nunca se reinicia."""
    ultimo_numero = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = 'Secuencia de Transaccion'

    @classmethod
    def siguiente(cls):
        with transaction.atomic():
            obj, _ = cls.objects.select_for_update().get_or_create(pk=1)
            obj.ultimo_numero += 1
            obj.save()
            return obj.ultimo_numero


class AperturaCaja(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente autorizacion'),
        ('autorizada', 'Autorizada'),
        ('rechazada', 'Rechazada'),
    ]
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               related_name='aperturas_caja')
    autorizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='aperturas_autorizadas')
    monto_inicial = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True)
    notas_rechazo = models.TextField(blank=True)
    solicitada_at = models.DateTimeField(auto_now_add=True)
    autorizada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-solicitada_at']
        verbose_name = 'Apertura de Caja'
        verbose_name_plural = 'Aperturas de Caja'

    def __str__(self):
        return f'Apertura {self.solicitada_at.strftime("%d/%m/%Y %H:%M")} - {self.cajero}'

    def esta_activa(self):
        return self.estado == 'autorizada' and not hasattr(self, 'cierre')

    def autorizar(self, autorizador):
        with transaction.atomic():
            self.estado = 'autorizada'
            self.autorizador = autorizador
            self.autorizada_at = timezone.now()
            self.save()
            TransaccionCaja.registrar(
                tipo='apertura_caja',
                usuario=self.cajero,
                autorizador=autorizador,
                monto=self.monto_inicial,
                descripcion=f'Apertura de caja — Fondo inicial ${self.monto_inicial}',
                referencia_id=self.id,
                referencia_modelo='AperturaCaja',
                apertura=self,
            )

    def rechazar(self, autorizador, motivo=''):
        with transaction.atomic():
            self.estado = 'rechazada'
            self.autorizador = autorizador
            self.notas_rechazo = motivo
            self.save()
            TransaccionCaja.registrar(
                tipo='rechazo_apertura',
                usuario=self.cajero,
                autorizador=autorizador,
                monto=0,
                descripcion=f'Apertura rechazada. Motivo: {motivo or "Sin motivo"}',
                referencia_id=self.id,
                referencia_modelo='AperturaCaja',
            )


class CierreCaja(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente autorizacion'),
        ('autorizado', 'Autorizado'),
        ('rechazado', 'Rechazado'),
    ]
    apertura = models.OneToOneField(AperturaCaja, on_delete=models.CASCADE, related_name='cierre')
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               related_name='cierres_caja')
    autorizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='cierres_autorizados')
    monto_efectivo = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    monto_tarjeta_credito = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    monto_tarjeta_debito = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    monto_transferencia = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    monto_propinas = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    diferencia = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True)
    notas_rechazo = models.TextField(blank=True)
    solicitado_at = models.DateTimeField(auto_now_add=True)
    autorizado_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-solicitado_at']
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def get_total(self):
        return (self.monto_efectivo + self.monto_tarjeta_credito +
                self.monto_tarjeta_debito + self.monto_transferencia)

    def get_total_esperado(self):
        from django.db.models import Sum
        pagos = Pago.objects.filter(apertura_caja=self.apertura, estado='aprobado')
        total_pagos = pagos.aggregate(t=Sum('monto_total'))['t'] or 0
        total_tienda = TransaccionCaja.objects.filter(
            apertura=self.apertura,
            tipo='transferencia',
            referencia_modelo='Payment',
        ).aggregate(t=Sum('monto'))['t'] or 0
        return total_pagos + total_tienda

    def __str__(self):
        return f'Cierre {self.solicitado_at.strftime("%d/%m/%Y %H:%M")} - {self.cajero}'

    def autorizar(self, autorizador):
        with transaction.atomic():
            esperado = self.get_total_esperado()
            self.diferencia = self.get_total() - esperado
            self.estado = 'autorizado'
            self.autorizador = autorizador
            self.autorizado_at = timezone.now()
            self.save()
            TransaccionCaja.registrar(
                tipo='cierre_caja',
                usuario=self.cajero,
                autorizador=autorizador,
                monto=self.get_total(),
                descripcion=(
                    f'Cierre de caja — Total: ${self.get_total()} | '
                    f'Esperado: ${esperado} | Diferencia: ${self.diferencia}'
                ),
                referencia_id=self.id,
                referencia_modelo='CierreCaja',
                apertura=self.apertura,
            )


class Pago(models.Model):
    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_credito', 'Tarjeta Credito (Visa/Mastercard)'),
        ('tarjeta_debito', 'Tarjeta Debito'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('anulado', 'Anulado'),
    ]
    comanda = models.OneToOneField(Comanda, on_delete=models.CASCADE, related_name='pago')
    apertura_caja = models.ForeignKey(AperturaCaja, on_delete=models.SET_NULL,
                                      null=True, related_name='pagos')
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               related_name='pagos_registrados')
    autorizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='pagos_autorizados')
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    monto_total = models.DecimalField(max_digits=12, decimal_places=0)
    propina = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    referencia = models.CharField(max_length=200, blank=True)
    ultimos_4 = models.CharField(max_length=4, blank=True)
    notas = models.TextField(blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    aprobado_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def get_total_con_propina(self):
        return self.monto_total + self.propina

    def __str__(self):
        return f'Pago #{self.id} - Mesa {self.comanda.mesa.numero} - ${self.monto_total}'

    def aprobar(self, autorizador=None):
        with transaction.atomic():
            self.estado = 'aprobado'
            self.autorizador = autorizador
            self.aprobado_at = timezone.now()
            self.save()
            TransaccionCaja.registrar(
                tipo='pago',
                usuario=self.cajero,
                autorizador=autorizador,
                monto=self.monto_total,
                descripcion=(
                    f'Pago {self.get_metodo_display()} — '
                    f'Mesa {self.comanda.mesa.numero} — '
                    f'Comanda #{self.comanda.id}'
                    + (f' — Ref: {self.referencia}' if self.referencia else '')
                    + (f' — ****{self.ultimos_4}' if self.ultimos_4 else '')
                ),
                referencia_id=self.id,
                referencia_modelo='Pago',
                apertura=self.apertura_caja,
            )

    def anular(self, usuario, autorizador, motivo=''):
        with transaction.atomic():
            self.estado = 'anulado'
            self.save()
            Anulacion.objects.create(
                pago=self,
                solicitado_por=usuario,
                autorizado_por=autorizador,
                motivo=motivo,
                monto_anulado=self.monto_total,
            )
            TransaccionCaja.registrar(
                tipo='anulacion',
                usuario=usuario,
                autorizador=autorizador,
                monto=self.monto_total,
                descripcion=(
                    f'ANULACION Pago #{self.id} — '
                    f'Mesa {self.comanda.mesa.numero} — '
                    f'Motivo: {motivo or "Sin motivo"}'
                ),
                referencia_id=self.id,
                referencia_modelo='Pago',
                apertura=self.apertura_caja,
            )


class Anulacion(models.Model):
    """Registro inmutable de anulaciones y reversas."""
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='anulacion')
    solicitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       related_name='anulaciones_solicitadas')
    autorizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       related_name='anulaciones_autorizadas')
    motivo = models.TextField()
    monto_anulado = models.DecimalField(max_digits=12, decimal_places=0)
    creada_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_at']
        verbose_name = 'Anulacion'
        verbose_name_plural = 'Anulaciones'

    def __str__(self):
        return f'Anulacion Pago #{self.pago.id} - ${self.monto_anulado}'


class TransaccionCaja(models.Model):
    """
    Libro mayor inmutable — NUNCA se edita ni elimina.
    Registro de TODAS las operaciones de caja para auditoria.
    """
    TIPO_CHOICES = [
        ('apertura_caja',         'Apertura de Caja'),
        ('rechazo_apertura',      'Rechazo de Apertura'),
        ('cierre_caja',           'Cierre de Caja'),
        ('pago',                  'Pago'),
        ('anulacion',             'Anulacion'),
        ('reversa',               'Reversa'),
        ('transferencia',         'Transferencia Autorizada'),
        ('rechazo_transferencia', 'Rechazo de Transferencia'),
    ]

    numero_transaccion = models.PositiveBigIntegerField(
        unique=True, db_index=True
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='transacciones_caja'
    )
    autorizador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transacciones_autorizadas'
    )
    apertura = models.ForeignKey(
        AperturaCaja, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transacciones'
    )
    monto = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    descripcion = models.TextField()
    referencia_modelo = models.CharField(max_length=50, blank=True)
    referencia_id = models.PositiveBigIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Transaccion de Caja'
        verbose_name_plural = 'Transacciones de Caja'
        default_permissions = ('add', 'view')

    def __str__(self):
        return f'TXN-{self.numero_transaccion:08d} | {self.get_tipo_display()} | ${self.monto}'

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError('Las transacciones de caja son inmutables.')
        if not self.numero_transaccion:
            self.numero_transaccion = SecuenciaTransaccion.siguiente()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('Las transacciones de caja no pueden eliminarse.')

    @classmethod
    def registrar(cls, tipo, usuario, monto, descripcion,
                  autorizador=None, referencia_id=None,
                  referencia_modelo='', apertura=None,
                  ip_address=None):
        with transaction.atomic():
            return cls.objects.create(
                tipo=tipo,
                usuario=usuario,
                autorizador=autorizador,
                apertura=apertura,
                monto=monto,
                descripcion=descripcion,
                referencia_modelo=referencia_modelo,
                referencia_id=referencia_id,
                ip_address=ip_address,
            )
