from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from menu.decorators import admin_role_required
from django.contrib import messages
from django.db.models import Sum
from .models import StockInventario, MovimientoInventario
from menu.models import Ingrediente
from .forms import MovimientoInventarioForm, StockInventarioForm
from decimal import Decimal


@admin_role_required
def lista_inventario(request):
    """Lista de inventario con stocks"""
    stocks = StockInventario.objects.all().order_by('ingrediente__nombre')
    
    # Filtrar por ingrediente
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        stocks = stocks.filter(ingrediente__nombre__icontains=busqueda)
    
    # Filtrar por bajo stock
    bajo_stock = request.GET.get('bajo_stock', '')
    if bajo_stock == '1':
        stocks = [s for s in stocks if s.necesita_reposicion()]
    
    context = {
        'stocks': stocks,
        'busqueda': busqueda,
        'bajo_stock': bajo_stock,
    }
    return render(request, 'inventario/lista.html', context)


@admin_role_required
def detalle_stock(request, stock_id):
    """Detalle de un stock con movimientos"""
    stock = get_object_or_404(StockInventario, id=stock_id)
    movimientos = MovimientoInventario.objects.filter(ingrediente=stock.ingrediente).order_by('-fecha')[:20]
    
    context = {
        'stock': stock,
        'movimientos': movimientos,
    }
    return render(request, 'inventario/detalle_stock.html', context)


@admin_role_required
def crear_movimiento(request):
    """Crear un movimiento de inventario"""
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            
            # Actualizar stock
            stock, created = StockInventario.objects.get_or_create(
                ingrediente=movimiento.ingrediente
            )
            
            if movimiento.tipo_movimiento == 'entrada':
                stock.cantidad_actual += movimiento.cantidad
            elif movimiento.tipo_movimiento == 'salida':
                stock.cantidad_actual -= movimiento.cantidad
                if stock.cantidad_actual < 0:
                    stock.cantidad_actual = Decimal('0.00')
            elif movimiento.tipo_movimiento == 'ajuste':
                stock.cantidad_actual = movimiento.cantidad
            
            stock.save()
            
            messages.success(request, 'Movimiento registrado exitosamente')
            return redirect('inventario:lista')
    else:
        form = MovimientoInventarioForm()
    
    context = {
        'form': form,
    }
    return render(request, 'inventario/crear_movimiento.html', context)


@admin_role_required
def editar_stock(request, stock_id):
    """Editar configuración de stock (cantidad mínima)"""
    stock = get_object_or_404(StockInventario, id=stock_id)
    
    if request.method == 'POST':
        form = StockInventarioForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock actualizado exitosamente')
            return redirect('inventario:detalle_stock', stock_id=stock.id)
    else:
        form = StockInventarioForm(instance=stock)
    
    context = {
        'form': form,
        'stock': stock,
    }
    return render(request, 'inventario/editar_stock.html', context)
