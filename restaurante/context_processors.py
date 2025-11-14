def carrito_context(request):
    """Context processor para agregar información del carrito al contexto global"""
    context = {}
    if request.user.is_authenticated and hasattr(request.user, 'es_cliente') and request.user.es_cliente():
        pedido_pendiente = request.user.pedidos.filter(estado='pendiente').first()
        if pedido_pendiente:
            context['carrito_count'] = pedido_pendiente.items.count()
        else:
            context['carrito_count'] = 0
    else:
        context['carrito_count'] = 0
    return context

