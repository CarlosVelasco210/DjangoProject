from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from .models import Gasto, Pago, Usuario, CuentaBancaria, DetallePago
from .forms import GastoForm
from datetime import date 
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            usuario_rol = request.session.get('usuario_rol')
            if usuario_rol == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            usuario = Usuario.objects.get(usuario=username)
            if usuario.contrasena == password:
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol

                if usuario.rol == 'pagos':
                    return redirect('pagos_dashboard')
                elif usuario.rol == 'gastos':
                    return redirect('gastos_dashboard')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@never_cache
@role_required('pagos')
def pagos_dashboard(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    cuentas_bancarias = CuentaBancaria.objects.all()

    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id)

    migrar_gastos_a_pagos()
    pagos = Pago.objects.all()

    return render(request, 'pagos/pagos.html', {'user': usuario, 'pagos': pagos, 'cuentas_bancarias': cuentas_bancarias,})

@role_required('pagos')  
def validar_pago(request, pago_id):
    if request.method == "POST":
        try:
            pago = Pago.objects.get(id=pago_id)

            # Obtener el usuario que está realizando la validación
            usuario_id = request.session.get('usuario_id')
            usuario = Usuario.objects.get(id=usuario_id)

            # Asignar el estado como 'Aprobado' y guardar el usuario que valida el pago
            pago.gasto.estado = "Aprobado"
            pago.gasto.usuario = usuario  # Aquí asignamos el usuario que valida
            pago.gasto.save()
            pago.save()  # Guardamos el pago con el usuario que lo ha validado

            return JsonResponse({
                'success': True,
                'message': 'El pago ha sido validado.',
                'new_state': 'Aprobado',
            })

        except Pago.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'El pago no existe.',
            })

@role_required('pagos')  
def rechazar_pago(request, pago_id):
    if request.method == "POST":
        motivo = request.POST.get('motivo_cancelacion', '')
        try:
            pago = Pago.objects.get(id=pago_id)

            # Obtener el usuario que está realizando la validación
            usuario_id = request.session.get('usuario_id')
            usuario = Usuario.objects.get(id=usuario_id)

            pago.gasto.estado = "Rechazado"
            pago.gasto.usuario = usuario  # Aquí asignamos el usuario que valida
            pago.gasto.motivo_cancelacion = motivo
            pago.gasto.save()

            return JsonResponse({
                "success": True,
                "message": "El pago fue rechazado exitosamente.",
                "new_state": "Rechazado"
            })
        except Pago.DoesNotExist:
            return JsonResponse({"success": False, "message": "El pago no existe."})

    return JsonResponse({"success": False, "message": "Método no permitido."})

    
@never_cache
@role_required('gastos')
def gastos_dashboard(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id)

    gastos = Gasto.objects.all()

    return render(request, 'gastos/gastos.html', {'user': usuario, 'gastos': gastos})

@never_cache
@role_required('gastos')
def crear_gasto(request):
    formulario = GastoForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        usuario_id = request.session.get('usuario_id')
        usuario = get_object_or_404(Usuario, id=usuario_id)

        formulario.instance.usuario = usuario
        formulario.instance.estado = "Pendiente"  # Asigna el estado "Pendiente"
        formulario.instance.fecha_registro = date.today()  # Asigna la fecha actual
        formulario.save()

        #messages.success(request, '¡El gasto ha sido guardado exitosamente!')

        return redirect('crear_gasto')
    return render(request, 'gastos/crear_gasto.html', {'formulario': formulario})


def cancelar_gasto(request, gasto_id):
    try:
        gasto = Gasto.objects.get(id=gasto_id)

        if request.method == "POST":
            motivo_cancelacion = request.POST.get('motivo_cancelacion')
            gasto.motivo_cancelacion = motivo_cancelacion
            gasto.estado = 'Cancelado'
            gasto.save()

            #messages.success(request, "El gasto ha sido cancelado correctamente.")
            return redirect('gastos_dashboard')

        return HttpResponseForbidden("Acción no permitida.")

    except Gasto.DoesNotExist:
        messages.error(request, "El gasto no existe.")
        return redirect('gastos_dashboard')

def cancelar_pago(request, pago_id):
    if request.method == "POST":
        motivo = request.POST.get("motivo_cancelacion", "")
        try:
            usuario_id = request.session.get('usuario_id')
            usuario = Usuario.objects.get(id=usuario_id)

            pago = get_object_or_404(Pago, id=pago_id)
            gasto = pago.gasto
            gasto.estado = "Cancelado"
            gasto.usuario = usuario
            gasto.motivo_cancelacion = motivo
            gasto.save()

            return JsonResponse({
                "success": True,
                "message": "El pago ha sido cancelado correctamente.",
                "new_state": "Cancelado"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error al cancelar el pago: {str(e)}"})
    return JsonResponse({"success": False, "message": "Método no permitido."})

def migrar_gastos_a_pagos():
    gastos_sin_pago = Gasto.objects.filter(pago__isnull=True)

    # Crear un pago para cada gasto
    for gasto in gastos_sin_pago:
        Pago.objects.create(
            gasto=gasto,
        )
    print(f"Se migraron {gastos_sin_pago.count()} gastos a la tabla de pagos.")

@csrf_exempt
def pagar_multiple(request):
    if request.method == 'POST':
        # Obtener los IDs de los pagos seleccionados desde la solicitud POST
        pagos_ids = request.POST.getlist('pagos_ids[]')  # Usar el mismo nombre que en el frontend
        cuenta_bancaria_id = request.POST.get('cuenta_bancaria')  # Obtener la cuenta bancaria seleccionada
        
        if not cuenta_bancaria_id:
            return JsonResponse({'success': False, 'message': 'Debe seleccionar una cuenta bancaria.'})
        # Verificar que la cuenta bancaria exista
        cuenta_bancaria = get_object_or_404(CuentaBancaria, id=cuenta_bancaria_id)

        # Calcular el monto total de los pagos seleccionados
        monto_total = 0
        for pago_id in pagos_ids:
            pago = get_object_or_404(Pago, id=pago_id)
            monto_total += int(pago.gasto.monto)  # Sumar el monto de cada pago

        if cuenta_bancaria.saldo < monto_total:
            return JsonResponse({'success': False, 'message': 'Saldo insuficiente en la cuenta bancaria.'})

        cuenta_bancaria.saldo -= monto_total
        cuenta_bancaria.save()

        # Procesar cada pago
        for pago_id in pagos_ids:
            pago = get_object_or_404(Pago, id=pago_id)
            gasto = pago.gasto
            gasto.estado = 'Pagado'  # Cambiar el estado a "Pagado"
            gasto.save()  # Guardar el cambio de estado en la base de datos

            # Crear el detalle de pago
            detalle_pago = DetallePago(
                pago=pago,
                monto_pagado=int(pago.gasto.monto),  # El monto pagado es el monto del pago
                fecha_pago=date.today(),  # La fecha de pago es hoy
                cuenta_bancaria=cuenta_bancaria  # La cuenta bancaria seleccionada
            )
            detalle_pago.save()  # Guardar el detalle de pago

        return JsonResponse({'success': True, 'message': 'Pagos procesados correctamente.'})

@never_cache
@role_required('pagos')  
def mostrar_detalle_pagos(request):
    detalles_pago = DetallePago.objects.select_related('pago', 'cuenta_bancaria')
    total_monto_pagado = detalles_pago.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0

    return render(request, 'pagos/detalles_pagos.html', {
        'detalles_pago': detalles_pago,
        'total_monto_pagado': total_monto_pagado,
    })