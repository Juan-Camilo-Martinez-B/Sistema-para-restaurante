from django import forms
from .models import Reserva, Mesa
from django.utils import timezone
from datetime import date, time


class ReservaForm(forms.ModelForm):
    """Formulario para crear/editar reservas"""
    
    class Meta:
        model = Reserva
        fields = ['mesa', 'fecha_reserva', 'hora_reserva', 'numero_personas', 'notas']
        widgets = {
            'mesa': forms.Select(attrs={'class': 'form-control'}),
            'fecha_reserva': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_reserva': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'numero_personas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mesa'].queryset = Mesa.objects.filter(disponible=True)
    
    def clean_fecha_reserva(self):
        fecha = self.cleaned_data.get('fecha_reserva')
        if fecha and fecha < date.today():
            raise forms.ValidationError('La fecha no puede ser en el pasado')
        return fecha
    
    def clean_numero_personas(self):
        numero_personas = self.cleaned_data.get('numero_personas')
        mesa = self.cleaned_data.get('mesa')
        
        if numero_personas and mesa and numero_personas > mesa.capacidad:
            raise forms.ValidationError(f'La mesa solo tiene capacidad para {mesa.capacidad} personas')
        
        return numero_personas

