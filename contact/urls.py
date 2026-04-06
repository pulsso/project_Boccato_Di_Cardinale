from django.urls import path

from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('documentos-tributarios/', views.billing_hub, name='billing_hub'),
]
