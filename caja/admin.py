from django.contrib import admin
from .models import PerfilCaja, AperturaCaja, CierreCaja, Pago, Anulacion, TransaccionCaja, SecuenciaTransaccion


@admin.register(PerfilCaja)
class PerfilCajaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'activo', 'creado_at']
    list_editable = ['rol', 'activo']
    list_filter = ['rol', 'activo']


@admin.register(AperturaCaja)
class AperturaCajaAdmin(admin.ModelAdmin):
    list_display = ['cajero', 'monto_inicial', 'estado', 'solicitada_at', 'autorizador', 'autorizada_at']
    list_filter = ['estado']
    readonly_fields = ['solicitada_at', 'autorizada_at']


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['cajero', 'get_total', 'estado', 'solicitado_at', 'autorizador', 'diferencia']
    list_filter = ['estado']
    readonly_fields = ['solicitado_at', 'autorizado_at', 'diferencia']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'comanda', 'cajero', 'metodo', 'monto_total', 'propina', 'estado', 'creado_at']
    list_filter = ['metodo', 'estado']
    readonly_fields = ['creado_at', 'aprobado_at']
    search_fields = ['comanda__id', 'cajero__username', 'referencia']


@admin.register(Anulacion)
class AnulacionAdmin(admin.ModelAdmin):
    list_display = ['pago', 'monto_anulado', 'solicitado_por', 'autorizado_por', 'creada_at']
    readonly_fields = ['pago', 'monto_anulado', 'solicitado_por', 'autorizado_por', 'creada_at']

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TransaccionCaja)
class TransaccionCajaAdmin(admin.ModelAdmin):
    list_display = ['numero_transaccion', 'tipo', 'monto', 'usuario', 'autorizador', 'fecha']
    list_filter = ['tipo']
    search_fields = ['numero_transaccion', 'descripcion', 'usuario__username']
    readonly_fields = [
        'numero_transaccion', 'tipo', 'usuario', 'autorizador',
        'apertura', 'monto', 'descripcion', 'referencia_modelo',
        'referencia_id', 'ip_address', 'fecha'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False