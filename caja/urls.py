# ============================================================
# ARCHIVO: caja/urls.py
# ============================================================
from django.urls import path
from . import views

app_name = 'caja'

urlpatterns = [
    # Cajero
    path('', views.dashboard, name='dashboard'),
    path('apertura/', views.solicitar_apertura, name='solicitar_apertura'),
    path('apertura/<int:apertura_id>/cierre/', views.solicitar_cierre, name='solicitar_cierre'),
    path('comanda/<int:comanda_id>/pagar/', views.registrar_pago, name='registrar_pago'),
    path('pago/<int:pago_id>/recibo/', views.recibo, name='recibo'),
    path('historial/', views.historial_pagos, name='historial_pagos'),

    # Tesorero
    path('tesorero/', views.tesorero_dashboard, name='tesorero_dashboard'),
    path('tesorero/apertura/<int:pk>/autorizar/', views.autorizar_apertura, name='autorizar_apertura'),
    path('tesorero/cierre/<int:pk>/autorizar/', views.autorizar_cierre, name='autorizar_cierre'),
    path('tesorero/transferencia/<int:pago_id>/autorizar/', views.autorizar_transferencia, name='autorizar_transferencia'),
    path('tesorero/pago/<int:pago_id>/anular/', views.anular_pago, name='anular_pago'),
    path('tesorero/auditoria/', views.auditoria, name='auditoria'),
]