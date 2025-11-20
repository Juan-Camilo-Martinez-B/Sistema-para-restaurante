from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class Usuario(AbstractUser):
    """Modelo de usuario personalizado con roles"""
    ROLES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
        ('mesero', 'Mesero'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para asignar rol de administrador a superusuarios"""
        # Si es superusuario, automáticamente es administrador
        if self.is_superuser:
            self.rol = 'administrador'
            self.is_staff = True  # Los superusuarios también deben ser staff
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    def es_administrador(self):
        """Verifica si el usuario es administrador (por rol o superusuario)"""
        return self.rol == 'administrador' or self.is_superuser
    
    def es_mesero(self):
        return self.rol == 'mesero'
    
    def es_cliente(self):
        return self.rol == 'cliente'

class RegistroPendiente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128)
    rol = models.CharField(max_length=20, choices=Usuario.ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
