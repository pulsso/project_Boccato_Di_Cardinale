from django.contrib import admin

from .models import DispatchTask, Order, OrderItem, OrderNotification


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'zone', 'sector', 'status', 'paid', 'delivery_method',
        'estimated_delivery_minutes', 'get_total', 'created_at',
    ]
    list_filter = ['status', 'paid', 'delivery_method', 'zone', 'sector']
    list_editable = ['status', 'paid']
    search_fields = ['user__username', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DispatchTask)
class DispatchTaskAdmin(admin.ModelAdmin):
    list_display = ['order', 'assigned_to', 'status', 'delivery_method', 'estimated_delivery_minutes', 'updated_at']
    list_filter = ['status', 'delivery_method']
    search_fields = ['order__id', 'order__user__username']


@admin.register(OrderNotification)
class OrderNotificationAdmin(admin.ModelAdmin):
    list_display = ['order', 'recipient_type', 'channel', 'recipient_email', 'created_at']
    list_filter = ['recipient_type', 'channel']
    search_fields = ['order__id', 'subject', 'message']
