from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

