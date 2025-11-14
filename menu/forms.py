from django import forms
from .models import Plato, Categoria, Ingrediente, PlatoIngrediente


class PlatoForm(forms.ModelForm):
    """Formulario para crear/editar platos"""
    
    class Meta:
        model = Plato
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'imagen', 'disponible', 'tiempo_preparacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiempo_preparacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class CategoriaForm(forms.ModelForm):
    """Formulario para crear/editar categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IngredienteForm(forms.ModelForm):
    """Formulario para crear/editar ingredientes"""
    
    class Meta:
        model = Ingrediente
        fields = ['nombre', 'descripcion', 'unidad_medida', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

