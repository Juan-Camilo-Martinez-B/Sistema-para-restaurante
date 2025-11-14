from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Pedido, ItemPedido
from .reportes import generar_reporte_pdf_pedidos, generar_reporte_excel_pedidos
from menu.models import Plato
from inventario.models import MovimientoInventario, StockInventario
from menu.models import PlatoIngrediente
from django.core.mail import send_mail
from django.conf import settings


@login_required
def carrito(request):
    """Vista del carrito de compras"""
    if not request.user.es_cliente():
        messages.error(request, 'Solo los clientes pueden ver el carrito')
        return redirect('menu:index')
    
    pedido = Pedido.objects.filter(cliente=request.user, estado='pendiente').first()
    context = {
        'pedido': pedido,
        'items': pedido.items.all() if pedido else [],
    }
    return render(request, 'pedidos/carrito.html', context)


@login_required
def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    if not request.user.es_cliente():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user, pedido__estado='pendiente')
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad < 1:
        item.delete()
    else:
        item.cantidad = cantidad
        item.save()
    
    return redirect('pedidos:carrito')


@login_required
def eliminar_item_carrito(request, item_id):
    """Elimina un item del carrito"""
    if not request.user.es_cliente():
        messages.error(request, 'No autorizado')
        return redirect('menu:index')
    
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user, pedido__estado='pendiente')
    item.delete()
    messages.success(request, 'Item eliminado del carrito')
    return redirect('pedidos:carrito')


@login_required
def checkout(request):
    """Proceso de pago y confirmación del pedido"""
    if not request.user.es_cliente():
        messages.error(request, 'Solo los clientes pueden realizar pedidos')
        return redirect('menu:index')
    
    pedido = Pedido.objects.filter(cliente=request.user, estado='pendiente').first()
    
    if not pedido or not pedido.items.exists():
        messages.error(request, 'El carrito está vacío')
        return redirect('menu:index')
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        notas = request.POST.get('notas', '')
        
        pedido.estado = 'confirmado'
        pedido.metodo_pago = metodo_pago
        pedido.notas = notas
        pedido.save()
        
        # Actualizar inventario
        for item in pedido.items.all():
            plato = item.plato
            ingredientes_plato = PlatoIngrediente.objects.filter(plato=plato)
            
            for plato_ingrediente in ingredientes_plato:
                ingrediente = plato_ingrediente.ingrediente
                cantidad_necesaria = plato_ingrediente.cantidad * Decimal(item.cantidad)
                
                # Obtener o crear stock
                stock, _ = StockInventario.objects.get_or_create(ingrediente=ingrediente)
                
                # Crear movimiento de salida
                MovimientoInventario.objects.create(
                    ingrediente=ingrediente,
                    tipo_movimiento='salida',
                    cantidad=cantidad_necesaria,
                    motivo=f'Pedido #{pedido.id} - {plato.nombre}',
                    usuario=request.user
                )
                
                # Actualizar stock
                stock.cantidad_actual -= cantidad_necesaria
                if stock.cantidad_actual < 0:
                    stock.cantidad_actual = Decimal('0.00')
                stock.save()
        
        # Enviar correo de confirmación
        try:
            send_mail(
                subject=f'Confirmación de Pedido #{pedido.id}',
                message=f'''
                Hola {request.user.username},
                
                Tu pedido ha sido confirmado exitosamente.
                
                Detalles del pedido:
                - Número de pedido: #{pedido.id}
                - Total: ${pedido.total}
                - Método de pago: {pedido.get_metodo_pago_display()}
                - Estado: {pedido.get_estado_display()}
                
                Gracias por tu compra!
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@restaurante.com',
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error enviando correo: {e}")
        
        messages.success(request, f'¡Pedido confirmado! Número de pedido: #{pedido.id}')
        return redirect('pedidos:historial')
    
    context = {
        'pedido': pedido,
    }
    return render(request, 'pedidos/checkout.html', context)


@login_required
def historial_pedidos(request):
    """Historial de pedidos del usuario"""
    if request.user.es_cliente():
        pedidos = Pedido.objects.filter(cliente=request.user).exclude(estado='pendiente').order_by('-fecha_creacion')
    elif request.user.es_mesero():
        pedidos = Pedido.objects.filter(mesero=request.user).order_by('-fecha_creacion')
    else:
        pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos/historial.html', context)


@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido"""
    if request.user.es_cliente():
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    elif request.user.es_mesero():
        pedido = get_object_or_404(Pedido, id=pedido_id, mesero=request.user)
    elif request.user.es_administrador():
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        messages.error(request, 'No autorizado')
        return redirect('menu:index')
    
    context = {
        'pedido': pedido,
        'items': pedido.items.all(),
    }
    return render(request, 'pedidos/detalle_pedido.html', context)


@staff_member_required
def lista_pedidos(request):
    """Lista de pedidos para meseros y administradores"""
    estado = request.GET.get('estado', '')
    pedidos = Pedido.objects.exclude(estado='pendiente').order_by('-fecha_creacion')
    
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    context = {
        'pedidos': pedidos,
        'estado_actual': estado,
    }
    return render(request, 'pedidos/lista_pedidos.html', context)


@staff_member_required
def actualizar_estado_pedido(request, pedido_id):
    """Actualiza el estado de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in dict(Pedido.ESTADOS):
        pedido.estado = nuevo_estado
        if nuevo_estado == 'entregado':
            pedido.fecha_entrega = timezone.now()
        pedido.save()
        messages.success(request, f'Estado del pedido actualizado a: {pedido.get_estado_display()}')
    
    return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)


@staff_member_required
def dashboard(request):
    """Panel de administración con estadísticas y gráficos"""
    hoy = timezone.now().date()
    mes_actual = hoy.replace(day=1)
    
    # Estadísticas generales
    total_pedidos = Pedido.objects.exclude(estado='pendiente').count()
    pedidos_hoy = Pedido.objects.filter(fecha_creacion__date=hoy).exclude(estado='pendiente').count()
    ventas_hoy = Pedido.objects.filter(fecha_creacion__date=hoy, estado__in=['entregado', 'listo']).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    ventas_mes = Pedido.objects.filter(
        fecha_creacion__date__gte=mes_actual,
        estado__in=['entregado', 'listo']
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Platos más vendidos
    platos_vendidos = ItemPedido.objects.filter(
        pedido__estado__in=['entregado', 'listo', 'confirmado', 'en_preparacion']
    ).values('plato__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:10]
    
    # Ingresos mensuales (últimos 12 meses)
    ingresos_mensuales = []
    for i in range(11, -1, -1):
        fecha = mes_actual - timedelta(days=30*i)
        mes_siguiente = fecha + timedelta(days=30)
        total = Pedido.objects.filter(
            fecha_creacion__date__gte=fecha,
            fecha_creacion__date__lt=mes_siguiente,
            estado__in=['entregado', 'listo']
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        ingresos_mensuales.append({
            'mes': fecha.strftime('%Y-%m'),
            'total': float(total)
        })
    
    # Pedidos por estado
    pedidos_por_estado = Pedido.objects.exclude(estado='pendiente').values('estado').annotate(
        cantidad=Count('id')
    )
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_hoy': pedidos_hoy,
        'ventas_hoy': ventas_hoy,
        'ventas_mes': ventas_mes,
        'platos_vendidos': platos_vendidos,
        'ingresos_mensuales': ingresos_mensuales,
        'pedidos_por_estado': list(pedidos_por_estado),
    }
    return render(request, 'pedidos/dashboard.html', context)


@staff_member_required
def generar_reporte(request, formato='pdf'):
    """Genera reportes en PDF o Excel"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    if formato == 'excel':
        return generar_reporte_excel_pedidos(request, fecha_inicio, fecha_fin)
    else:
        return generar_reporte_pdf_pedidos(request, fecha_inicio, fecha_fin)
