from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Plato, Categoria, Ingrediente
from .forms import PlatoForm, CategoriaForm, IngredienteForm, PlatoIngredienteFormSet
from .decorators import staff_or_mesero_required
from pedidos.models import ItemPedido, Pedido
from decimal import Decimal


def index(request):
    """Página principal con el menú de platos"""
    categorias = Categoria.objects.filter(activa=True)
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '')
    
    platos = Plato.objects.filter(disponible=True)
    
    if categoria_id:
        platos = platos.filter(categoria_id=categoria_id)
    
    if busqueda:
        platos = platos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )
    
    context = {
        'platos': platos,
        'categorias': categorias,
        'categoria_actual': int(categoria_id) if categoria_id else None,
        'busqueda': busqueda,
    }
    return render(request, 'menu/index.html', context)


def detalle_plato(request, plato_id):
    """Detalle de un plato"""
    plato = get_object_or_404(Plato, id=plato_id, disponible=True)
    return render(request, 'menu/detalle_plato.html', {'plato': plato})


@login_required
def agregar_al_carrito(request, plato_id):
    """Agrega un plato al carrito de compras"""
    if not request.user.es_cliente():
        messages.error(request, 'Solo los clientes pueden realizar pedidos')
        return redirect('menu:index')
    
    plato = get_object_or_404(Plato, id=plato_id, disponible=True)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad < 1:
        messages.error(request, 'La cantidad debe ser mayor a 0')
        return redirect('menu:detalle_plato', plato_id=plato_id)
    
    # Obtener o crear pedido pendiente del usuario
    pedido, created = Pedido.objects.get_or_create(
        cliente=request.user,
        estado='pendiente',
        defaults={'subtotal': Decimal('0.00'), 'impuesto': Decimal('0.00'), 'total': Decimal('0.00')}
    )
    
    # Verificar si el plato ya está en el pedido
    item, item_created = ItemPedido.objects.get_or_create(
        pedido=pedido,
        plato=plato,
        defaults={
            'cantidad': cantidad,
            'precio_unitario': plato.precio,
        }
    )
    
    if not item_created:
        item.cantidad += cantidad
        item.save()
    
    messages.success(request, f'{plato.nombre} agregado al carrito')
    return redirect('pedidos:carrito')


# Vistas CRUD para administradores y meseros
@staff_or_mesero_required
def lista_platos_admin(request):
    """Lista de platos para administradores"""
    platos = Plato.objects.all().order_by('-fecha_creacion')
    busqueda = request.GET.get('busqueda', '')
    
    if busqueda:
        platos = platos.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda))
    
    context = {
        'platos': platos,
        'busqueda': busqueda,
    }
    return render(request, 'menu/admin/lista_platos.html', context)


@staff_or_mesero_required
def crear_plato(request):
    """Crear un nuevo plato"""
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES)
        if form.is_valid():
            plato = form.save()
            formset = PlatoIngredienteFormSet(request.POST, instance=plato)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Plato creado exitosamente')
                return redirect('menu:lista_platos_admin')
            else:
                return render(request, 'menu/admin/form_plato.html', {'form': form, 'formset': formset, 'plato': plato, 'titulo': 'Crear Plato'})
        else:
            formset = PlatoIngredienteFormSet()
            return render(request, 'menu/admin/form_plato.html', {'form': form, 'formset': formset, 'titulo': 'Crear Plato'})
    else:
        form = PlatoForm()
        formset = PlatoIngredienteFormSet()
    
    return render(request, 'menu/admin/form_plato.html', {'form': form, 'formset': formset, 'titulo': 'Crear Plato'})


@staff_or_mesero_required
def editar_plato(request, plato_id):
    """Editar un plato existente"""
    plato = get_object_or_404(Plato, id=plato_id)
    
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES, instance=plato)
        formset = PlatoIngredienteFormSet(request.POST, instance=plato)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Plato actualizado exitosamente')
            return redirect('menu:lista_platos_admin')
    else:
        form = PlatoForm(instance=plato)
        formset = PlatoIngredienteFormSet(instance=plato)
    
    return render(request, 'menu/admin/form_plato.html', {'form': form, 'formset': formset, 'plato': plato, 'titulo': 'Editar Plato'})


@staff_or_mesero_required
def eliminar_plato(request, plato_id):
    """Eliminar un plato"""
    plato = get_object_or_404(Plato, id=plato_id)
    
    if request.method == 'POST':
        plato.delete()
        messages.success(request, 'Plato eliminado exitosamente')
        return redirect('menu:lista_platos_admin')
    
    return render(request, 'menu/admin/confirmar_eliminar.html', {'objeto': plato, 'tipo': 'plato'})


@staff_or_mesero_required
def lista_ingredientes_admin(request):
    """Lista de ingredientes para administradores"""
    ingredientes = Ingrediente.objects.all().order_by('nombre')
    busqueda = request.GET.get('busqueda', '')
    
    if busqueda:
        ingredientes = ingredientes.filter(nombre__icontains=busqueda)
    
    context = {
        'ingredientes': ingredientes,
        'busqueda': busqueda,
    }
    return render(request, 'menu/admin/lista_ingredientes.html', context)


@staff_or_mesero_required
def crear_ingrediente(request):
    """Crear un nuevo ingrediente"""
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            ingrediente = form.save()
            # Crear stock inicial
            from inventario.models import StockInventario
            StockInventario.objects.get_or_create(ingrediente=ingrediente)
            messages.success(request, 'Ingrediente creado exitosamente')
            return redirect('menu:lista_ingredientes_admin')
    else:
        form = IngredienteForm()
    
    return render(request, 'menu/admin/form_ingrediente.html', {'form': form, 'titulo': 'Crear Ingrediente'})


@staff_or_mesero_required
def editar_ingrediente(request, ingrediente_id):
    """Editar un ingrediente existente"""
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
    
    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente actualizado exitosamente')
            return redirect('menu:lista_ingredientes_admin')
    else:
        form = IngredienteForm(instance=ingrediente)
    
    return render(request, 'menu/admin/form_ingrediente.html', {'form': form, 'ingrediente': ingrediente, 'titulo': 'Editar Ingrediente'})


@staff_or_mesero_required
def eliminar_ingrediente(request, ingrediente_id):
    """Eliminar un ingrediente"""
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
    
    if request.method == 'POST':
        ingrediente.delete()
        messages.success(request, 'Ingrediente eliminado exitosamente')
        return redirect('menu:lista_ingredientes_admin')
    
    return render(request, 'menu/admin/confirmar_eliminar.html', {'objeto': ingrediente, 'tipo': 'ingrediente'})
