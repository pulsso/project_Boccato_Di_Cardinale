from django.contrib import admin

from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'zone', 'sector', 'created_at']
    list_filter = ['zone', 'sector']
    search_fields = ['user__username', 'user__email', 'default_address']
