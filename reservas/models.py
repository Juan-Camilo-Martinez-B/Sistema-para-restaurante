from django.db import models
from usuarios.models import Usuario


class Mesa(models.Model):
    """Mesas del restaurante"""
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(help_text="Número de personas que caben")
    disponible = models.BooleanField(default=True)
    ubicacion = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: Interior, Terraza, Ventana")
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero']
    
    def __str__(self):
        return f"Mesa {self.numero} (Capacidad: {self.capacidad})"


class Reserva(models.Model):
    """Reservas de mesas"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='reservas')
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_personas = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva', '-hora_reserva']
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente.username} - Mesa {self.mesa.numero} - {self.fecha_reserva}"
