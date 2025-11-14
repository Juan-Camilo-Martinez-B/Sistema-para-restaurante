from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.rol = self.cleaned_data.get('rol', 'cliente')
        user.telefono = self.cleaned_data.get('telefono', '')
        user.direccion = self.cleaned_data.get('direccion', '')
        if commit:
            user.save()
        return user

