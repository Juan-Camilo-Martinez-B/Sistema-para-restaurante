from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.index, name='index'),
    path('plato/<int:plato_id>/', views.detalle_plato, name='detalle_plato'),
    path('agregar-carrito/<int:plato_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    # URLs para administradores
    path('gestion/platos/', views.lista_platos_admin, name='lista_platos_admin'),
    path('gestion/platos/crear/', views.crear_plato, name='crear_plato'),
    path('gestion/platos/<int:plato_id>/editar/', views.editar_plato, name='editar_plato'),
    path('gestion/platos/<int:plato_id>/eliminar/', views.eliminar_plato, name='eliminar_plato'),
    path('gestion/ingredientes/', views.lista_ingredientes_admin, name='lista_ingredientes_admin'),
    path('gestion/ingredientes/crear/', views.crear_ingrediente, name='crear_ingrediente'),
    path('gestion/ingredientes/<int:ingrediente_id>/editar/', views.editar_ingrediente, name='editar_ingrediente'),
    path('gestion/ingredientes/<int:ingrediente_id>/eliminar/', views.eliminar_ingrediente, name='eliminar_ingrediente'),
]

