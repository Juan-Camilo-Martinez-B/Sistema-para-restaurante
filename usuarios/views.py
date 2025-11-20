from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Usuario, RegistroPendiente
from .forms import RegistroForm, LoginForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.utils import OperationalError
import time
import importlib


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

def solicitar_reset(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                messages.error(request, 'No existe una cuenta con ese correo')
                return render(request, 'usuarios/reset_password_request.html', {'form': form})
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse_lazy('usuarios:reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            ok = _send_email(
                to_email=email,
                subject='Restablece tu contraseña',
                html_content=f"<p>Hola {user.username},</p><p>Puedes restablecer tu contraseña haciendo clic en el siguiente enlace:</p><p><a href='{reset_url}'>{reset_url}</a></p>",
                plain_text=f"Hola {user.username},\n\nPuedes restablecer tu contraseña haciendo clic en el siguiente enlace:\n{reset_url}",
            )
            if not ok:
                messages.error(request, 'No pudimos enviar el enlace. Revisa la configuración de correo.')
                return render(request, 'usuarios/reset_password_request.html', {'form': form})
            messages.success(request, 'Hemos enviado un enlace de restablecimiento a tu correo')
            return redirect('usuarios:login')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'usuarios/reset_password_request.html', {'form': form})

def reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None
    if not user or not default_token_generator.check_token(user, token):
        messages.error(request, 'El enlace de restablecimiento no es válido o ha expirado')
        return redirect('usuarios:login')
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            for _ in range(5):
                try:
                    with transaction.atomic():
                        user.set_password(form.cleaned_data['password1'])
                        user.save()
                    break
                except OperationalError:
                    time.sleep(0.3)
            messages.success(request, 'Tu contraseña ha sido actualizada')
            return redirect('usuarios:login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'usuarios/reset_password_confirm.html', {'form': form})


class RegistroView(CreateView):
    """Vista de registro de nuevos usuarios"""
    model = Usuario
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')
    
    def form_valid(self, form):
        data = form.cleaned_data
        pending = RegistroPendiente.objects.create(
            username=data['username'],
            email=data['email'],
            password_hash=make_password(data['password1']),
            rol=data.get('rol', 'cliente'),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', ''),
        )
        activation_url = self.request.build_absolute_uri(
            reverse_lazy('usuarios:activar_pendiente', kwargs={'pid': str(pending.id)})
        )
        ok = _send_email(
            to_email=pending.email,
            subject='Verifica tu correo',
            html_content=f"<p>Hola {pending.username},</p><p>Por favor verifica tu correo haciendo clic en el siguiente enlace:</p><p><a href='{activation_url}'>{activation_url}</a></p><p>Si no solicitaste este registro, ignora este mensaje.</p>",
            plain_text=f"Hola {pending.username},\n\nPor favor verifica tu correo haciendo clic en el siguiente enlace:\n{activation_url}\n\nSi no solicitaste este registro, ignora este mensaje.",
        )
        if not ok:
            messages.error(self.request, 'No se pudo enviar el correo de verificación. Verifica tu remitente y configuración de correo.')
            return redirect(self.success_url)
        messages.success(self.request, 'Registro iniciado. Revisa tu correo para activar tu cuenta.')
        return redirect(self.success_url)


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:login')


def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Tu cuenta ha sido activada. Ahora puedes iniciar sesión.')
        return redirect('usuarios:login')
    messages.error(request, 'El enlace de activación no es válido o ha expirado.')
    return redirect('usuarios:login')

def activar_pendiente(request, pid):
    from django.shortcuts import get_object_or_404
    pending = get_object_or_404(RegistroPendiente, pk=pid)
    if Usuario.objects.filter(username=pending.username).exists() or Usuario.objects.filter(email=pending.email).exists():
        pending.delete()
        messages.error(request, 'Ya existe un usuario con esos datos')
        return redirect('usuarios:login')
    user = Usuario(
        username=pending.username,
        email=pending.email,
        rol=pending.rol,
        telefono=pending.telefono or '',
        direccion=pending.direccion or '',
        is_active=True,
    )
    user.password = pending.password_hash
    user.save()
    pending.delete()
    messages.success(request, 'Tu cuenta ha sido activada. Ahora puedes iniciar sesión.')
    return redirect('usuarios:login')
def _send_email(to_email, subject, html_content, plain_text):
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@restaurante.com')
    if api_key:
        try:
            sendgrid = importlib.import_module('sendgrid')
            Mail = importlib.import_module('sendgrid.helpers.mail').Mail
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            resp = sg.send(message)
            if 200 <= int(getattr(resp, 'status_code', 0)) < 300:
                return True
        except Exception:
            pass
    try:
        send_mail(
            subject=subject,
            message=plain_text,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False
