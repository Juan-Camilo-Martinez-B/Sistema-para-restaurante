from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        error_messages={'required': 'Ingresa tu usuario'}
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        error_messages={'required': 'Ingresa tu contraseña'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            return cleaned_data

        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            raise forms.ValidationError('No existe un usuario con ese nombre')

        if not user.is_active:
            raise forms.ValidationError('Tu cuenta está desactivada')

        if not user.check_password(password):
            raise forms.ValidationError('Contraseña incorrecta')

        self.user = user
        return cleaned_data

    def get_user(self):
        return self.user


class RegistroForm(UserCreationForm):
    """Formulario de registro"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    rol = forms.ChoiceField(
        label='Tipo de Usuario',
        choices=[
            ('cliente', 'Cliente'),
            ('mesero', 'Mesero'),
        ],
        initial='cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección'})
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2', 'rol', 'telefono', 'direccion')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        self.fields['username'].error_messages.update({'required': 'Ingresa un nombre de usuario'})
        self.fields['email'].error_messages.update({'required': 'Ingresa tu correo electrónico'})
        self.fields['password1'].error_messages.update({'required': 'Ingresa una contraseña'})
        self.fields['password2'].error_messages.update({'required': 'Confirma tu contraseña'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.rol = self.cleaned_data.get('rol', 'cliente')
        user.telefono = self.cleaned_data.get('telefono', '')
        user.direccion = self.cleaned_data.get('direccion', '')
        user.is_active = False
        if commit:
            user.save()
        return user

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('No existe una cuenta con ese correo')
        return email

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned
