from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from usuarios.models import Usuario
from menu.models import Plato


class Pedido(models.Model):
    """Pedidos realizados por los clientes"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='pedidos')
    mesero = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pedidos_atendidos',
        limit_choices_to={'rol': 'mesero'}
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username} - ${self.total}"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los items"""
        items = self.items.all()
        subtotal = sum(item.subtotal for item in items)
        impuesto = subtotal * Decimal('0.19')  # IVA 19%
        total = subtotal + impuesto
        
        self.subtotal = subtotal
        self.impuesto = impuesto
        self.total = total
        self.save()
        return total


class ItemPedido(models.Model):
    """Items individuales de un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedidos'
    
    def __str__(self):
        return f"{self.plato.nombre} x{self.cantidad} - ${self.subtotal}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente"""
        self.subtotal = self.precio_unitario * Decimal(self.cantidad)
        super().save(*args, **kwargs)
        # Recalcula el total del pedido
        self.pedido.calcular_total()
