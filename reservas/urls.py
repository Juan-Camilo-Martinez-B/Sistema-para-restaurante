from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('crear/', views.crear_reserva, name='crear'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar'),
    path('verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
]

