from django.urls import path

from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.carta_home, name='carta_home'),
    path('completa/', views.carta_completa, name='carta_completa'),
    path('desayuno/', views.carta_desayuno, name='desayuno'),
    path('brunch/', views.carta_brunch, name='brunch'),
    path('almuerzo/', views.carta_almuerzo, name='almuerzo'),
    path('cena/', views.carta_cena, name='cena'),
    path('terraza/', views.carta_terraza, name='terraza'),
    path('vinos/', views.carta_vinos, name='vinos'),
    path('licores/', views.carta_licores, name='licores'),
    path('cocteles/', views.carta_cocteles, name='cocteles'),
    path('catering/', views.carta_catering, name='catering'),
    path('panel/', views.panel_menu, name='panel_menu'),
    path('panel/items/', views.panel_items, name='panel_items'),
    path('panel/items/nuevo/', views.panel_item_crear, name='panel_item_crear'),
    path('panel/items/<int:pk>/editar/', views.panel_item_editar, name='panel_item_editar'),
    path('panel/items/<int:pk>/eliminar/', views.panel_item_eliminar, name='panel_item_eliminar'),
    path('panel/categorias/', views.panel_categorias, name='panel_categorias'),
    path('panel/categorias/nueva/', views.panel_categoria_crear, name='panel_categoria_crear'),
    path('panel/categorias/<int:pk>/eliminar/', views.panel_categoria_eliminar, name='panel_categoria_eliminar'),
]
