from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Usuario
from .forms import RegistroForm, LoginForm


def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('menu:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.username}!')
                if user.is_superuser:
                    return redirect('/admin/')
                elif user.es_administrador():
                    return redirect('/gestion/')
                elif user.es_mesero():
                    return redirect('pedidos:lista_pedidos')
                else:
                    return redirect('menu:index')
            else:
                messages.error(request, 'No se pudo iniciar sesión')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


class RegistroView(CreateView):
    """Vista de registro de nuevos usuarios"""
    model = Usuario
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Registro exitoso! Por favor inicia sesión.')
        return super().form_valid(form)


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:login')
