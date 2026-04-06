from django.contrib import admin

from .models import CategoriaMenu, ItemMenu


@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'orden', 'activa')
    list_filter = ('tipo', 'activa')
    search_fields = ('nombre',)


@admin.register(ItemMenu)
class ItemMenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'precio_oferta', 'tiene_oferta', 'disponible', 'destacado')
    list_filter = ('categoria__tipo', 'disponible', 'destacado', 'tiene_oferta')
    search_fields = ('nombre', 'descripcion')
