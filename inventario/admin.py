from django.contrib import admin
from .models import MovimientoInventario, StockInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('ingrediente', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo_movimiento', 'fecha', 'ingrediente')
    search_fields = ('ingrediente__nombre', 'motivo')
    readonly_fields = ('fecha',)


@admin.register(StockInventario)
class StockInventarioAdmin(admin.ModelAdmin):
    list_display = ('ingrediente', 'cantidad_actual', 'cantidad_minima', 'necesita_reposicion', 'fecha_actualizacion')
    list_filter = ('ingrediente',)
    search_fields = ('ingrediente__nombre',)
    readonly_fields = ('fecha_actualizacion',)
    
    def necesita_reposicion(self, obj):
        return obj.necesita_reposicion()
    necesita_reposicion.boolean = True
    necesita_reposicion.short_description = 'Necesita Reposición'
