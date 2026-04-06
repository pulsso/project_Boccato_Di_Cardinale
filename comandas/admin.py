from django import forms
from django.contrib import admin

from .models import Comanda, ItemComanda, Mesa, PerfilGarzon


class PerfilGarzonAdminForm(forms.ModelForm):
    nuevo_pin = forms.CharField(
        required=False,
        label='Nuevo PIN',
        widget=forms.PasswordInput(render_value=False),
        help_text='Ingresa un nuevo PIN solo si deseas cambiarlo.',
    )

    class Meta:
        model = PerfilGarzon
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        nuevo_pin = self.cleaned_data.get('nuevo_pin')
        if nuevo_pin:
            instance.set_pin(nuevo_pin)
        if commit:
            instance.save()
        return instance


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'zona', 'capacidad', 'activa', 'garzon_asignado')
    list_filter = ('zona', 'activa')
    search_fields = ('numero', 'garzon_asignado__username', 'garzon_asignado__first_name', 'garzon_asignado__last_name')


class ItemComandaInline(admin.TabularInline):
    model = ItemComanda
    extra = 0
    readonly_fields = ('nombre_item', 'cantidad', 'precio_unitario', 'estado', 'agregado_por', 'creado_at')


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'mesa', 'garzon', 'estado', 'fecha_operacion', 'cerrada_at')
    list_filter = ('estado', 'fecha_operacion', 'mesa__zona')
    search_fields = ('mesa__numero', 'garzon__username', 'garzon__first_name', 'garzon__last_name')
    inlines = [ItemComandaInline]


@admin.register(PerfilGarzon)
class PerfilGarzonAdmin(admin.ModelAdmin):
    form = PerfilGarzonAdminForm
    list_display = ('usuario', 'codigo_operador', 'zona_asignada', 'activo', 'tiene_pin')
    list_filter = ('activo', 'zona_asignada')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')

