import csv, random, string
from datetime import datetime, timedelta
from django.apps import apps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from portal_app.services.tickets import generar_boleto_qr
from portal_app.services.pdf import render_to_pdf
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Value
from datetime import date


def get_model(cands):
    for app_label, name in cands:
        try:
            m = apps.get_model(app_label, name)
            if m: return m
        except Exception:
            pass
    raise LookupError(str(cands))

Vuelo   = get_model([('flights','Flight')])
Avion   = get_model([('fleet','Airplane')])
Asiento = get_model([('fleet','Seat')])
Pasajero= get_model([('passengers','Passenger')])
Reserva = get_model([('booking','Reservation')])
try:
    Boleto = get_model([('booking','Ticket')])
except LookupError:
    Boleto = None

def is_staff(u): return u.is_staff
def home(request):
    return render(request, 'home.html', {'sugerencias': _sugerencias_lugares()})

def buscar_vuelos(request):
    origen  = request.GET.get('origen','')
    destino = request.GET.get('destino','')
    fecha   = request.GET.get('fecha','')
    vuelos = Vuelo.objects.all().order_by('fecha_salida')
    if origen:  vuelos = vuelos.filter(origen__icontains=origen)
    if destino: vuelos = vuelos.filter(destino__icontains=destino)
    if fecha:
        try:
            dt = datetime.fromisoformat(fecha)
            start = timezone.make_aware(datetime(dt.year, dt.month, dt.day, 0, 0))
            end   = start + timedelta(days=1)
            vuelos = vuelos.filter(fecha_salida__gte=start, fecha_salida__lt=end)
        except Exception:
            pass
    return render(request, 'vuelos/lista.html', {'vuelos':vuelos,'origen':origen,'destino':destino,'fecha':fecha, 'sugerencias': _sugerencias_lugares()})

def vuelo_detalle(request, pk):
    vuelo = get_object_or_404(Vuelo, pk=pk)
    reservas = Reserva.objects.filter(vuelo=vuelo).select_related('asiento')
    estado_por_asiento = {r.asiento_id: getattr(r,'estado','PEN') for r in reservas}
    filas = {}
    for a in Asiento.objects.filter(avion=vuelo.avion).order_by('fila','columna'):
        estado = estado_por_asiento.get(a.id, 'FREE')
        filas.setdefault(getattr(a,'fila',0), []).append({'a':a,'estado':estado})
    grid = [filas[k] for k in sorted(filas.keys())]
        # indicar si el usuario ya tiene reserva activa para este vuelo
    tiene = False
    if request.user.is_authenticated:
        try:
            tiene = bool(_reserva_activa_usuario(request.user, vuelo, Reserva, Pasajero))
        except Exception:
            tiene = False
    return render(request, 'vuelos/detalle.html', {'vuelo':vuelo,'filas':grid})

def _code(n=10): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

@login_required
@login_required
def crear_reserva(request, vuelo_id, asiento_id):
    # Cargar modelos
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asiento = get_object_or_404(Asiento, pk=asiento_id)
    # Validar que el asiento sea del avión del vuelo
    if getattr(asiento, 'avion_id', None) != getattr(vuelo, 'avion_id', None):
        messages.error(request, 'Ese asiento no pertenece a este vuelo.')
        return redirect('portal_vuelo_detalle', pk=vuelo.id)

    # Obtener/crear Pasajero vinculado al usuario
    pasajero = _get_or_create_pasajero(request.user, Pasajero)

    # 1) El pasajero no puede tener más de una reserva en el mismo vuelo (salvo canceladas)
    reserva_existente = Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero).exclude(estado='CANC').first()
    if reserva_existente:
        messages.info(request, 'Ya tenés una reserva para este vuelo. Podés verla o cambiar de asiento.')
        codigo = getattr(reserva_existente, 'codigo_reserva', None) or getattr(reserva_existente, 'code', None) or reserva_existente.pk
        return redirect('portal_ver_boleto', codigo=codigo)

    # 2) El asiento no puede estar tomado para ese vuelo (salvo canceladas)
    asiento_tomado = Reserva.objects.filter(vuelo=vuelo, asiento=asiento).exclude(estado='CANC').exists()
    if asiento_tomado:
        messages.error(request, f'El asiento {getattr(asiento,"numero", asiento.id)} ya está reservado.')
        return redirect('portal_vuelo_detalle', pk=vuelo.id)

    # GET => mostrar confirmación
    if request.method == 'GET':
        return render(request, 'reservas/confirmar.html', {'vuelo': vuelo, 'asiento': asiento})

    # POST => crear la reserva
    if request.method == 'POST':
        precio = getattr(vuelo, 'precio_base', None)
        try:
            precio = Decimal(precio)
        except Exception:
            precio = Decimal('0')

        # Generar código
        def _gen_code(n=8):
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
        codigo = _gen_code()

        # Estado por defecto: 'CONF' si confirmamos de una; si preferís 'PEN', cambiá acá.
        estado = 'CONF' if 'confirmar' in request.POST else 'PEN'

        reserva = Reserva.objects.create(
            vuelo=vuelo,
            pasajero=pasajero,
            asiento=asiento,
            precio=precio,
            estado=estado,
            **({'codigo_reserva': codigo} if 'codigo_reserva' in [f.name for f in Reserva._meta.get_fields()] else {'code': codigo})
        )

        # Marcar asiento como reservado/ocupado si tu modelo lo usa
        try:
            # 'RES' para reservado; si preferís 'OCU' al confirmar, cámbialo
            asiento.estado = 'RES' if estado != 'CONF' else 'OCU'
            asiento.save(update_fields=['estado'])
        except Exception:
            pass

        # Ir al boleto
        codigo = getattr(reserva, 'codigo_reserva', None) or getattr(reserva, 'code', None) or reserva.pk
        return redirect('portal_ver_boleto', codigo=codigo)

    # Método no permitido => redirigir
    messages.error(request, 'Método no permitido.')
    return redirect('portal_vuelo_detalle', pk=vuelo.id)

login_required
def perfil(request):
    defaults={'nombre': request.user.get_full_name() or request.user.username, 'documento': f"TMP{request.user.id}", 'email': request.user.email or 'user@example.com'}
    try:
        pasajero = Pasajero.objects.filter(email__iexact=request.user.email).first()
        if not pasajero:
            pasajero = Pasajero.objects.create(**defaults)
    except Exception:
        pasajero=None
    if request.method=='POST' and pasajero:
        for f in ['nombre','documento','email','telefono','fecha_nacimiento','tipo_documento']:
            if f in request.POST and hasattr(pasajero,f): setattr(pasajero,f, request.POST.get(f))
        pasajero.save(); messages.success(request,'Perfil actualizado.'); return redirect('portal_perfil')
    return render(request, 'pasajeros/perfil.html', {'pasajero':pasajero})

@login_required
@login_required
def historial(request):
    pasajero = _get_or_create_pasajero(request.user, Pasajero)
    reservas = Reserva.objects.filter(pasajero=pasajero).order_by('-id')
    return render(request, 'reservas/historial.html', {'reservas': reservas})


@login_required
def ver_boleto(request, codigo):
    # Busca SIEMPRE por codigo_reserva
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo)
    # Generar/asegurar ticket con QR
    try:
        ticket = generar_boleto_qr(reserva)
    except Exception as e:
        messages.warning(request, f"No se pudo generar QR automáticamente: {e}")
    return render(request, 'reservas/boleto.html', {'reserva': reserva})



@login_required
@user_passes_test(is_staff)

def pasajeros_por_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    reservas = Reserva.objects.filter(vuelo=vuelo).select_related('pasajero','asiento').order_by('id')

    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="pasajeros_vuelo_{vuelo_id}.csv"'
        writer = csv.writer(resp)
        writer.writerow(["codigo_reserva","pasajero","documento","email","asiento","estado"])
        for r in reservas:
            writer.writerow([getattr(r,'codigo_reserva',''), r.pasajero.nombre, r.pasajero.documento, r.pasajero.email, getattr(r.asiento,'numero',r.asiento_id), r.estado])
        return resp

    return render(request, 'reportes/pasajeros_por_vuelo.html', {'vuelo': vuelo, 'reservas': reservas})


from portal_app.forms import SignupForm
from django.contrib.auth import login

def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        from django.contrib.auth import login
        login(request, user)
        from django.shortcuts import redirect
        return redirect('portal_home')
    return render(request, 'registration/signup.html', {'form': form})


# Lugares base (podés editar esta lista)
_LUGARES_BASE = [
    'AEP', 'EZE', 'COR', 'MDZ', 'BRC', 'IGR', 'SAL', 'NQN', 'ROS', 'USH', 'FTE',
    'Buenos Aires', 'Córdoba', 'Mendoza', 'Bariloche', 'Iguazú', 'Salta', 'Neuquén', 'Rosario', 'Ushuaia', 'El Calafate'
]

def _sugerencias_lugares():
    """Combina una lista base con valores existentes en la BD (distinct de Flight)."""
    try:
        # Import local para evitar fallos de import en startup
        from django.apps import apps
        Flight = apps.get_model('flights','Flight')
        # Distinct de origen y destino
        origs = set(Flight.objects.values_list('origen', flat=True).distinct())
        dests = set(Flight.objects.values_list('destino', flat=True).distinct())
        datos = set([x for x in (list(origs)+list(dests)) if x])
    except Exception:
        datos = set()
    # unir con base
    s = list(sorted(set(_LUGARES_BASE) | datos))
    return s



def _get_or_create_pasajero(user, Pasajero):
    """Busca Passenger por email o lo crea con datos mínimos obligatorios."""
    email = (getattr(user, 'email', '') or '').strip()
    nombre = (getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'username', '') or 'Sin nombre').strip() or 'Sin nombre'
    # 1) intentar por email
    p = None
    if email:
        p = Pasajero.objects.filter(email__iexact=email).first()
    # 2) intentar por nombre si no se encontró
    if not p and nombre:
        p = Pasajero.objects.filter(nombre=nombre).first()
    # 3) crear si no existe, completando campos NOT NULL
    if not p:
        tmp_doc = f"TMP-{getattr(user,'id', '')}-{random.randint(1000,9999)}"
        # valores por defecto obligatorios
        valores = {
            'nombre': nombre,
            'email': email or f"user{getattr(user,'id','')}@example.com",
            'documento': tmp_doc,
            'fecha_nacimiento': date(1990, 1, 1),   # default seguro
        }
        # si el modelo tiene tipo_documento/telefono, los completamos también
        if any(f.name == 'tipo_documento' for f in Pasajero._meta.get_fields()):
            valores['tipo_documento'] = 'DNI'
        if any(f.name == 'telefono' for f in Pasajero._meta.get_fields()):
            valores['telefono'] = ''
        p = Pasajero.objects.create(**valores)
    return p


def _reserva_activa_usuario(user, vuelo, Reserva, Pasajero):
    pasajero = _get_or_create_pasajero(user, Pasajero)
    return Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero).exclude(estado='CANC').first()


@login_required
def cambiar_asiento(request, vuelo_id, asiento_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asiento_nuevo = get_object_or_404(Asiento, pk=asiento_id)

    if getattr(asiento_nuevo, 'avion_id', None) != getattr(vuelo, 'avion_id', None):
        messages.error(request, 'Ese asiento no pertenece a este vuelo.')
        return redirect('portal_vuelo_detalle', pk=vuelo.id)

    # Reserva activa del usuario
    reserva_vieja = _reserva_activa_usuario(request.user, vuelo, Reserva, Pasajero)
    if not reserva_vieja:
        messages.info(request, 'No tenías una reserva activa para cambiar.')
        return redirect('portal_vuelo_detalle', pk=vuelo.id)

    # Si el asiento ya está tomado (en otra reserva no cancelada), bloquear
    if Reserva.objects.filter(vuelo=vuelo, asiento=asiento_nuevo).exclude(estado='CANC').exists():
        messages.error(request, f'El asiento {getattr(asiento_nuevo,"numero", asiento_nuevo.id)} ya está reservado.')
        return redirect('portal_vuelo_detalle', pk=vuelo.id)

    # Cancelar la vieja y liberar asiento
    try:
        asiento_viejo = reserva_vieja.asiento
        reserva_vieja.estado = 'CANC'
        reserva_vieja.save(update_fields=['estado'])
        try:
            asiento_viejo.estado = 'DISP'
            asiento_viejo.save(update_fields=['estado'])
        except Exception:
            pass
    except Exception:
        pass

    # Crear nueva reserva confirmada con el nuevo asiento
    from portal_app.services.tickets import generar_boleto_qr
    from portal_app.services.pdf import render_to_pdf
    pasajero = _get_or_create_pasajero(request.user, Pasajero)
    from django.utils.crypto import get_random_string
    codigo = get_random_string(8).upper()
    precio = getattr(vuelo, 'precio_base', 0) or 0
    try:
        precio = Decimal(precio)
    except Exception:
        from decimal import Decimal as _D
        precio = _D('0')

    reserva = Reserva.objects.create(
        vuelo=vuelo, pasajero=pasajero, asiento=asiento_nuevo,
        precio=precio, estado='CONF',
        **({'codigo_reserva': codigo} if 'codigo_reserva' in [f.name for f in Reserva._meta.get_fields()] else {'code': codigo})
    )
    try:
        asiento_nuevo.estado = 'OCU'
        asiento_nuevo.save(update_fields=['estado'])
    except Exception:
        pass

    try:
        generar_boleto_qr(reserva)
    except Exception as e:
        messages.warning(request, f'Reserva cambiada, pero no se pudo generar QR: {e}')

    codigo = getattr(reserva, 'codigo_reserva', None) or getattr(reserva, 'code', None) or reserva.pk
    messages.success(request, '¡Asiento cambiado con éxito!')
    return redirect('portal_ver_boleto', codigo=codigo)


def descargar_boleto_pdf(request, codigo):
    # siempre buscamos por codigo_reserva
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo)
    # asegurar que exista ticket/QR (no es obligatorio para PDF, pero suma)
    try:
        generar_boleto_qr(reserva)
    except Exception:
        pass
    context = {'reserva': reserva}
    pdf = render_to_pdf('reservas/boleto_pdf.html', context)
    if pdf is None:
        # si falla la generación, devolvemos el HTML normal como fallback
        return render(request, 'reservas/boleto.html', context)
    from django.http import HttpResponse
    filename = f"boleto_{reserva.codigo_reserva}.pdf"
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp
