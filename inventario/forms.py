from django import forms
from .models import MovimientoInventario, StockInventario
from menu.models import Ingrediente


class MovimientoInventarioForm(forms.ModelForm):
    """Formulario para crear movimientos de inventario"""
    
    class Meta:
        model = MovimientoInventario
        fields = ['ingrediente', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo del movimiento'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingrediente'].queryset = Ingrediente.objects.filter(activo=True)


class StockInventarioForm(forms.ModelForm):
    """Formulario para editar stock"""
    
    class Meta:
        model = StockInventario
        fields = ['cantidad_minima']
        widgets = {
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

