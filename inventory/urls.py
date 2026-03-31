from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('<int:product_id>/movement/', views.stock_movement, name='stock_movement'),
]