from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from flights.models import Flight
from booking.models import Reservation
from passengers.models import Passenger

def flights_list(request):
    flights = Flight.objects.all()
    return render(request, "flights_list.html", {"flights": flights})

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
    ).select_related("vuelo", "asiento")
    return render(request, "my_reservations.html", {"reservas": reservas})
