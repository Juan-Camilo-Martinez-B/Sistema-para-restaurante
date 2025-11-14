from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_inventario, name='lista'),
    path('stock/<int:stock_id>/', views.detalle_stock, name='detalle_stock'),
    path('movimiento/crear/', views.crear_movimiento, name='crear_movimiento'),
    path('stock/<int:stock_id>/editar/', views.editar_stock, name='editar_stock'),
]

