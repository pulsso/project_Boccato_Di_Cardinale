from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('dispatch/', views.dispatch_dashboard, name='dispatch_dashboard'),
    path('dispatch/<int:pk>/', views.dispatch_order_detail, name='dispatch_order_detail'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/ticket/', views.order_ticket, name='order_ticket'),
]
