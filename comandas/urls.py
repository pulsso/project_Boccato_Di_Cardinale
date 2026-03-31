from django.urls import path
from . import views

app_name = 'comandas'

urlpatterns = [
    # Layout mesas (garzón)
    path('', views.layout_mesas, name='layout_mesas'),
    path('mesa/<int:mesa_id>/', views.mesa_detalle, name='mesa_detalle'),
    path('mesa/<int:mesa_id>/nueva/', views.comanda_nueva, name='comanda_nueva'),
    path('comanda/<int:comanda_id>/', views.comanda_detalle, name='comanda_detalle'),
    path('comanda/<int:comanda_id>/agregar/', views.comanda_agregar_item, name='comanda_agregar_item'),
    path('comanda/<int:comanda_id>/item/<int:item_id>/eliminar/', views.comanda_eliminar_item, name='comanda_eliminar_item'),
    path('comanda/<int:comanda_id>/cerrar/', views.comanda_cerrar, name='comanda_cerrar'),
    path('comanda/<int:comanda_id>/cancelar/', views.comanda_cancelar, name='comanda_cancelar'),

    # Panel admin comandas
    path('panel/', views.panel_comandas, name='panel_comandas'),
    path('panel/mesas/', views.panel_mesas, name='panel_mesas'),
    path('panel/mesas/nueva/', views.panel_mesa_crear, name='panel_mesa_crear'),
    path('panel/mesas/<int:pk>/editar/', views.panel_mesa_editar, name='panel_mesa_editar'),
    path('panel/mesas/<int:pk>/eliminar/', views.panel_mesa_eliminar, name='panel_mesa_eliminar'),
    path('panel/garzones/', views.panel_garzones, name='panel_garzones'),
    path('panel/historial/', views.panel_historial, name='panel_historial'),

    # API para pantalla táctil
    path('api/item/<int:item_id>/toggle/', views.api_toggle_item, name='api_toggle_item'),
    path('api/comanda/<int:comanda_id>/estado/', views.api_estado_comanda, name='api_estado_comanda'),
]