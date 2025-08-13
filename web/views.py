from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from flights.models import Flight
from booking.models import Reservation
from passengers.models import Passenger

def home(request):
    # Widget de búsqueda (filtros simples)
    qs = Flight.objects.all()
    origen = request.GET.get("origen")
    destino = request.GET.get("destino")
    fecha = request.GET.get("fecha")
    if origen: qs = qs.filter(origen__icontains=origen)
    if destino: qs = qs.filter(destino__icontains=destino)
    if fecha: qs = qs.filter(fecha_salida__date=fecha)
    resultados = qs.order_by("fecha_salida")[:12]

    # Promos / Destinos (mock, estático por ahora)
    promos = [
        {"titulo": "12 cuotas sin interés", "detalle": "Bancos seleccionados", "cta": "#"},
        {"titulo": "Tarifas Flex domésticas", "detalle": "Cambios sin penalidad", "cta": "#"},
        {"titulo": "Semana de descuentos", "detalle": "Hasta 30% off", "cta": "#"},
    ]
    destinos = [
        {"codigo": "EZE", "nombre": "Buenos Aires", "desc": "Cultural y gastronómica"},
        {"codigo": "COR", "nombre": "Córdoba", "desc": "Sierras y ciudad universitaria"},
        {"codigo": "MDZ", "nombre": "Mendoza", "desc": "Vinos y alta montaña"},
        {"codigo": "BRC", "nombre": "Bariloche", "desc": "Lagos, nieve y chocolate"},
        {"codigo": "IGR", "nombre": "Iguazú", "desc": "Maravilla natural"},
        {"codigo": "USH", "nombre": "Ushuaia", "desc": "Fin del mundo"},
    ]

    return render(request, "home.html", {
        "resultados": resultados,
        "promos": promos,
        "destinos": destinos,
    })

def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, "flight_detail.html", {"flight": flight})

@login_required
def seat_map(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    seats = flight.avion.asientos.all()
    if request.method == "POST":
        seat_id = request.POST.get("seat_id")
        pasajero, _ = Passenger.objects.get_or_create(
            documento=request.user.username,
            defaults={
                "nombre": request.user.get_full_name() or request.user.username,
                "email": request.user.email or "",
                "telefono": "",
                "fecha_nacimiento": "2000-01-01",
                "tipo_documento": "DNI",
            }
        )
        seat = seats.get(id=seat_id)
        Reservation.objects.create(
            vuelo=flight, pasajero=pasajero, asiento=seat,
            precio=flight.precio_base, estado="RES"
        )
        return redirect("web:my_reservations")
    return render(request, "seat_map.html", {"flight": flight, "seats": seats})

@login_required
def my_reservations(request):
    reservas = Reservation.objects.filter(
        pasajero__documento=request.user.username
    ).select_related("vuelo","asiento")
    return render(request, "my_reservations.html", {"reservas": reservas})
