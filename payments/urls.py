from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('security/', views.treasury_security, name='treasury_security'),
    path('<int:order_id>/', views.payment_process, name='payment_process'),
    path('authorize/<int:payment_id>/', views.payment_authorize, name='payment_authorize'),
    path('<int:order_id>/success/', views.payment_success, name='payment_success'),
    path('<int:order_id>/cancel/', views.payment_cancel, name='payment_cancel'),
]
