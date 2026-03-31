from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'authorized_by', 'created_at']
    list_filter = ['movement_type']
    search_fields = ['product__name']
    readonly_fields = ['created_at']