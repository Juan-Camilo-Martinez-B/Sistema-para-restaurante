from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """Categorías de platos (Entradas, Platos principales, Postres, etc.)"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    """Ingredientes disponibles en el restaurante"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, default='unidad')  # kg, litros, unidades, etc.
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Plato(models.Model):
    """Platos del menú del restaurante"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='platos')
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    tiempo_preparacion = models.IntegerField(default=30, help_text="Tiempo en minutos")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plato'
        verbose_name_plural = 'Platos'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class PlatoIngrediente(models.Model):
    """Relación entre platos e ingredientes con cantidad"""
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='ingredientes_plato')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        verbose_name = 'Ingrediente de Plato'
        verbose_name_plural = 'Ingredientes de Platos'
        unique_together = ['plato', 'ingrediente']
    
    def __str__(self):
        return f"{self.plato.nombre} - {self.ingrediente.nombre} ({self.cantidad})"
