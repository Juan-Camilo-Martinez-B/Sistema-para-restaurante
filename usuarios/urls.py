from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar'),
    path('activar-pendiente/<uuid:pid>/', views.activar_pendiente, name='activar_pendiente'),
    path('password/reset/', views.solicitar_reset, name='solicitar_reset'),
    path('password/reset/<uidb64>/<token>/', views.reset_confirm, name='reset_confirm'),
]

