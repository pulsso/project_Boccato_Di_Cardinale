from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Tienda pública
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='products'),
    path('terraza/', views.terraza, name='terraza'),

    # CRUD — rutas específicas ANTES de <slug>
    path('products/new/', views.product_create, name='product_create'),

    # Panel admin personalizado
    path('panel/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/productos/', views.panel_productos, name='panel_productos'),
    path('panel/productos/nuevo/', views.panel_producto_crear, name='panel_producto_crear'),
    path('panel/productos/<int:pk>/editar/', views.panel_producto_editar, name='panel_producto_editar'),
    path('panel/productos/<int:pk>/eliminar/', views.panel_producto_eliminar, name='panel_producto_eliminar'),
    path('panel/categorias/', views.panel_categorias, name='panel_categorias'),
    path('panel/ofertas/', views.panel_ofertas, name='panel_ofertas'),
    path('panel/ofertas/nueva/', views.panel_oferta_crear, name='panel_oferta_crear'),
    path('panel/ofertas/<int:pk>/eliminar/', views.panel_oferta_eliminar, name='panel_oferta_eliminar'),
    path('panel/campanas/', views.panel_campanas, name='panel_campanas'),
    path('panel/campanas/nueva/', views.panel_campana_crear, name='panel_campana_crear'),
    path('panel/campanas/<int:pk>/eliminar/', views.panel_campana_eliminar, name='panel_campana_eliminar'),
    path('panel/ordenes/', views.panel_ordenes, name='panel_ordenes'),
    path('panel/ordenes/<int:pk>/', views.panel_orden_detalle, name='panel_orden_detalle'),
    path('panel/galeria/', views.panel_galeria, name='panel_galeria'),
    path('panel/galeria/nueva/', views.panel_galeria_crear, name='panel_galeria_crear'),
    path('panel/galeria/<int:pk>/eliminar/', views.panel_galeria_eliminar, name='panel_galeria_eliminar'),
    path('panel/historial/', views.panel_historial, name='panel_historial'),
    path('panel/reportes/', views.panel_reportes, name='panel_reportes'),

    # Rutas con slug — SIEMPRE AL FINAL
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/<slug:slug>/edit/', views.product_update, name='product_update'),
    path('products/<slug:slug>/delete/', views.product_delete, name='product_delete'),
]