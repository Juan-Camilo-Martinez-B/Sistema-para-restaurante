from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, date, time, timedelta
from .models import Reserva, Mesa
from .forms import ReservaForm
from django.core.mail import send_mail
from django.conf import settings


@login_required
def crear_reserva(request):
    """Crear una nueva reserva"""
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = request.user
            
            # Verificar disponibilidad
            reservas_existentes = Reserva.objects.filter(
                mesa=reserva.mesa,
                fecha_reserva=reserva.fecha_reserva,
                estado__in=['pendiente', 'confirmada', 'en_curso']
            ).exclude(id=reserva.id if reserva.id else None)
            
            # Verificar si hay conflicto de horario (asumiendo 2 horas por reserva)
            hora_fin = datetime.combine(reserva.fecha_reserva, reserva.hora_reserva).time()
            hora_fin_objeto = datetime.combine(date.today(), hora_fin) + timedelta(hours=2)
            hora_fin = hora_fin_objeto.time()
            
            conflicto = False
            for reserva_existente in reservas_existentes:
                hora_existente = reserva_existente.hora_reserva
                hora_existente_fin = datetime.combine(date.today(), hora_existente) + timedelta(hours=2)
                hora_existente_fin = hora_existente_fin.time()
                
                if not (reserva.hora_reserva >= hora_existente_fin or hora_fin <= hora_existente):
                    conflicto = True
                    break
            
            if conflicto:
                messages.error(request, 'La mesa no está disponible en ese horario')
            else:
                reserva.save()
                messages.success(request, f'Reserva creada exitosamente. Número de reserva: #{reserva.id}')
                
                # Enviar correo de confirmación
                try:
                    send_mail(
                        subject=f'Confirmación de Reserva #{reserva.id}',
                        message=f'''
                        Hola {request.user.username},
                        
                        Tu reserva ha sido confirmada.
                        
                        Detalles de la reserva:
                        - Número de reserva: #{reserva.id}
                        - Mesa: {reserva.mesa.numero}
                        - Fecha: {reserva.fecha_reserva}
                        - Hora: {reserva.hora_reserva}
                        - Número de personas: {reserva.numero_personas}
                        - Estado: {reserva.get_estado_display()}
                        
                        ¡Te esperamos!
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@restaurante.com',
                        recipient_list=[request.user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Error enviando correo: {e}")
                
                return redirect('reservas:mis_reservas')
    else:
        form = ReservaForm()
    
    # Obtener mesas disponibles
    mesas = Mesa.objects.filter(disponible=True)
    context = {
        'form': form,
        'mesas': mesas,
    }
    return render(request, 'reservas/crear_reserva.html', context)


@login_required
def mis_reservas(request):
    """Lista de reservas del usuario"""
    reservas = Reserva.objects.filter(cliente=request.user).order_by('-fecha_reserva', '-hora_reserva')
    context = {
        'reservas': reservas,
    }
    return render(request, 'reservas/mis_reservas.html', context)


@login_required
def detalle_reserva(request, reserva_id):
    """Detalle de una reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    context = {
        'reserva': reserva,
    }
    return render(request, 'reservas/detalle_reserva.html', context)


@login_required
def cancelar_reserva(request, reserva_id):
    """Cancela una reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    
    if reserva.estado in ['completada', 'cancelada']:
        messages.error(request, 'No se puede cancelar una reserva completada o ya cancelada')
    else:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente')
    
    return redirect('reservas:mis_reservas')


def verificar_disponibilidad(request):
    """Verifica disponibilidad de mesas (AJAX)"""
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')
    
    if not fecha or not hora:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora, '%H:%M').time()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha/hora inválido'}, status=400)
    
    # Obtener mesas ocupadas
    reservas = Reserva.objects.filter(
        fecha_reserva=fecha_obj,
        estado__in=['pendiente', 'confirmada', 'en_curso']
    )
    
    mesas_ocupadas = []
    for reserva in reservas:
        hora_fin = datetime.combine(date.today(), reserva.hora_reserva) + timedelta(hours=2)
        hora_fin = hora_fin.time()
        
        if not (hora_obj >= hora_fin or hora_obj <= reserva.hora_reserva):
            mesas_ocupadas.append(reserva.mesa.id)
    
    mesas_disponibles = Mesa.objects.filter(disponible=True).exclude(id__in=mesas_ocupadas)
    
    return JsonResponse({
        'mesas_disponibles': [{'id': m.id, 'numero': m.numero, 'capacidad': m.capacidad} for m in mesas_disponibles]
    })
