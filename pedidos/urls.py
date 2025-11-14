from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('carrito/', views.carrito, name='carrito'),
    path('actualizar-carrito/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('eliminar-item/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('historial/', views.historial_pedidos, name='historial'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('lista/', views.lista_pedidos, name='lista_pedidos'),
    path('actualizar-estado/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reporte/<str:formato>/', views.generar_reporte, name='generar_reporte'),
]

