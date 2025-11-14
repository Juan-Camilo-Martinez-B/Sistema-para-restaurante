from django.contrib import admin
from .models import Mesa, Reserva


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidad', 'disponible', 'ubicacion')
    list_filter = ('disponible', 'ubicacion')
    search_fields = ('numero',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'mesa', 'fecha_reserva', 'hora_reserva', 'numero_personas', 'estado')
    list_filter = ('estado', 'fecha_reserva', 'mesa')
    search_fields = ('cliente__username', 'cliente__email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
