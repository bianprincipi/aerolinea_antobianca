import csv, random, string
from datetime import datetime, timedelta
from django.apps import apps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

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
def home(request): return render(request, 'home.html')

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
    return render(request, 'vuelos/lista.html', {'vuelos':vuelos,'origen':origen,'destino':destino,'fecha':fecha})

def vuelo_detalle(request, pk):
    vuelo = get_object_or_404(Vuelo, pk=pk)
    reservas = Reserva.objects.filter(vuelo=vuelo).select_related('asiento')
    estado_por_asiento = {r.asiento_id: getattr(r,'estado','PEN') for r in reservas}
    filas = {}
    for a in Asiento.objects.filter(avion=vuelo.avion).order_by('fila','columna'):
        estado = estado_por_asiento.get(a.id, 'FREE')
        filas.setdefault(getattr(a,'fila',0), []).append({'a':a,'estado':estado})
    grid = [filas[k] for k in sorted(filas.keys())]
    return render(request, 'vuelos/detalle.html', {'vuelo':vuelo,'filas':grid})

def _code(n=10): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

@login_required
def crear_reserva(request, vuelo_id, asiento_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    asiento = get_object_or_404(Asiento, id=asiento_id)
    pasajero = getattr(request.user, 'pasajero', None) or Pasajero.objects.filter(usuario=request.user).first()
    if not pasajero:
        messages.error(request,'Completá tu perfil de pasajero.'); return redirect('portal_perfil')
    if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero).exists():
        messages.error(request, 'Ya tenés una reserva para este vuelo.'); return redirect('portal_vuelo_detalle', pk=vuelo.id)
    if Reserva.objects.filter(vuelo=vuelo, asiento=asiento).exists():
        messages.error(request, 'Ese asiento ya está reservado.'); return redirect('portal_vuelo_detalle', pk=vuelo.id)
    if getattr(asiento,'avion_id', None) != getattr(vuelo,'avion_id', None):
        messages.error(request, 'El asiento no pertenece a este vuelo.'); return redirect('portal_vuelo_detalle', pk=vuelo.id)
    if request.method == 'POST':
        reserva = Reserva.objects.create(
            vuelo=vuelo, pasajero=pasajero, asiento=asiento,
            estado='CONF' if request.POST.get('confirmar') else 'PEN',
            precio=getattr(vuelo,'precio_base',0),
            codigo_reserva=_code()
        )
        messages.success(request, f"Reserva creada: {getattr(reserva,'codigo_reserva',reserva.pk)}")
        return redirect('portal_ver_boleto', codigo=getattr(reserva,'codigo_reserva',reserva.pk))
    return render(request, 'reservas/confirmar.html', {'vuelo':vuelo,'asiento':asiento})

@login_required
def perfil(request):
    defaults={'nombre': request.user.get_full_name() or request.user.username, 'documento': f"TMP{request.user.id}", 'email': request.user.email or 'user@example.com'}
    try:
        pasajero,_=Pasajero.objects.get_or_create(usuario=request.user, defaults=defaults)
    except Exception:
        pasajero=None
    if request.method=='POST' and pasajero:
        for f in ['nombre','documento','email','telefono','fecha_nacimiento','tipo_documento']:
            if f in request.POST and hasattr(pasajero,f): setattr(pasajero,f, request.POST.get(f))
        pasajero.save(); messages.success(request,'Perfil actualizado.'); return redirect('portal_perfil')
    return render(request, 'pasajeros/perfil.html', {'pasajero':pasajero})

@login_required
def historial(request):
    pasajero = getattr(request.user,'pasajero',None) or Pasajero.objects.filter(usuario=request.user).first()
    reservas = Reserva.objects.filter(pasajero=pasajero).select_related('vuelo','asiento').order_by('-fecha_reserva') if pasajero else []
    return render(request, 'reservas/historial.html', {'reservas':reservas})

@login_required
def ver_boleto(request, codigo):
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo)
    if getattr(reserva,'pasajero_id',None) and getattr(reserva.pasajero,'usuario_id',None) and reserva.pasajero.usuario_id != request.user.id:
        messages.error(request,'No podés ver este boleto.'); return redirect('portal_historial')
    if getattr(reserva,'estado','PEN') == 'CANC':
        messages.error(request,'La reserva fue cancelada.'); return redirect('portal_historial')
    if getattr(reserva,'estado','PEN') == 'CONF' and Boleto is not None:
        from portal_app.services.tickets import generar_boleto_qr
        generar_boleto_qr(reserva, Boleto)
    return render(request, 'reservas/boleto.html', {'reserva':reserva})

@login_required
@user_passes_test(is_staff)
def pasajeros_por_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    reservas = Reserva.objects.filter(vuelo=vuelo).select_related('pasajero','asiento').order_by('pasajero__nombre')
    if request.GET.get('export')=='csv':
        r=HttpResponse(content_type='text/csv'); r['Content-Disposition']=f'attachment; filename="pasajeros_vuelo_{vuelo_id}.csv"'
        w=csv.writer(r); w.writerow(['Reserva','Pasajero','Documento','Email','Asiento','Estado'])
        for x in reservas:
            w.writerow([getattr(x,'codigo_reserva',x.pk),
                        getattr(x.pasajero,'nombre',x.pasajero_id),
                        getattr(x.pasajero,'documento',getattr(x.pasajero,'document',x.pasajero_id)),
                        getattr(x.pasajero,'email',''),
                        getattr(x.asiento,'numero',getattr(x.asiento,'number',x.asiento_id)),
                        getattr(x,'estado','')])
        return r
    return render(request, 'reportes/pasajeros_por_vuelo.html', {'vuelo':vuelo,'reservas':reservas})
