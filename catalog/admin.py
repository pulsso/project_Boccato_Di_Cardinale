from django.contrib import admin
from .models import Category, Product, GaleriaFoto, Oferta, Campana, HistorialCambio


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'active']
    list_editable = ['active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'category', 'price', 'stock', 'available', 'featured']
    list_filter = ['available', 'featured', 'category']
    list_editable = ['price', 'stock', 'available', 'featured']
    search_fields = ['name', 'description', 'external_image_url']


@admin.register(GaleriaFoto)
class GaleriaFotoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'seccion', 'orden', 'activa']
    list_editable = ['orden', 'activa']
    list_filter = ['seccion', 'activa']
    search_fields = ['titulo', 'descripcion', 'external_image_url']


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'descuento_porcentaje', 'fecha_inicio', 'fecha_fin', 'activa']
    list_editable = ['activa']
    list_filter = ['activa']


@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'fecha_inicio', 'fecha_fin', 'activa']
    list_editable = ['activa']
    list_filter = ['tipo', 'activa']


@admin.register(HistorialCambio)
class HistorialCambioAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'usuario', 'accion', 'modelo', 'objeto_nombre']
    list_filter = ['accion', 'modelo', 'usuario']
    readonly_fields = ['usuario', 'accion', 'modelo', 'objeto_id', 'objeto_nombre', 'detalle', 'fecha']
    search_fields = ['objeto_nombre', 'detalle']
