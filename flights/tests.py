import pytest
from fleet.models import Airplane, Seat
from flights.models import Flight
from passengers.models import Passenger
from booking.models import Reservation

@pytest.mark.django_db
def test_ticket_emitted_when_paid():
    plane = Airplane.objects.create(modelo="A320", capacidad=6, filas=2, columnas=3)
    seat = Seat.objects.create(avion=plane, numero="1A", fila=1, columna="A")
    f = Flight.objects.create(avion=plane, origen="COR", destino="EZE",
                              fecha_salida="2030-01-01T10:00Z",
                              fecha_llegada="2030-01-01T12:00Z",
                              duracion="02:00:00", precio_base=10000)
    p = Passenger.objects.create(nombre="Ana", documento="123", email="a@a.com",
                                 telefono="", fecha_nacimiento="2000-01-01", tipo_documento="DNI")
    r = Reservation.objects.create(vuelo=f, pasajero=p, asiento=seat, precio=10000, estado="RES")
    r.estado = "PAG"
    r.save()
    assert hasattr(r, "boleto")
    assert r.boleto.codigo_barra
