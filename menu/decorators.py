from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def staff_or_mesero_required(view_func):
    """Decorador que permite acceso a administradores y meseros"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('usuarios:login')
        
        if request.user.es_administrador() or request.user.es_mesero():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'No tienes permisos para acceder a esta página')
            return redirect('menu:index')
    
    return _wrapped_view


def admin_role_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('usuarios:login')
        if request.user.is_superuser or request.user.es_administrador():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('menu:index')
    return _wrapped_view

