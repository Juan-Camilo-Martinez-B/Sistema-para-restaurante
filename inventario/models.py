from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from menu.models import Ingrediente


class MovimientoInventario(models.Model):
    """Movimientos de inventario (entradas y salidas)"""
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    motivo = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.ingrediente.nombre} - {self.cantidad}"


class StockInventario(models.Model):
    """Stock actual de cada ingrediente"""
    ingrediente = models.OneToOneField(Ingrediente, on_delete=models.CASCADE, related_name='stock')
    cantidad_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cantidad_minima = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cantidad mínima antes de alertar"
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Stock de Inventario'
        verbose_name_plural = 'Stocks de Inventario'
        ordering = ['ingrediente']
    
    def __str__(self):
        return f"{self.ingrediente.nombre} - Stock: {self.cantidad_actual}"
    
    def necesita_reposicion(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.cantidad_actual <= self.cantidad_minima
