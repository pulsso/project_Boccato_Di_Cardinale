from django.contrib import admin

from .models import (
    Payment,
    PaymentSequence,
    PaymentValidationLog,
    TreasuryAuthorizationSettings,
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'user', 'method', 'status',
        'treasury_number', 'rejection_number', 'confirmed_at',
    ]
    list_filter = ['status', 'method']
    search_fields = ['order__id', 'user__username', 'reference']


@admin.register(PaymentSequence)
class PaymentSequenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_number', 'last_rejection_number']


@admin.register(TreasuryAuthorizationSettings)
class TreasuryAuthorizationSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'updated_by', 'updated_at']
    readonly_fields = ['approval_code_hash', 'updated_at']


@admin.register(PaymentValidationLog)
class PaymentValidationLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'action', 'actor', 'code', 'created_at']
    list_filter = ['action']
    search_fields = ['payment__order__id', 'detail', 'code']
