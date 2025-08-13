from django.db import models
from django.utils.crypto import get_random_string
from flights.models import Flight
from passengers.models import Passenger
from fleet.models import Seat

class Reservation(models.Model):
    ESTADOS = [("RES", "Reservado"), ("PAG", "Pagado"), ("CAN", "Cancelado")]

    vuelo = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="reservas")
    pasajero = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="reservas")
    asiento = models.OneToOneField(Seat, on_delete=models.PROTECT, related_name="reserva", null=True, blank=True)
    estado = models.CharField(max_length=3, choices=ESTADOS, default="RES")
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=12, unique=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["vuelo", "pasajero"], name="unique_passenger_per_flight"),
        ]

    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = get_random_string(12).upper()
        if self.asiento and self.asiento.avion_id != self.vuelo.avion_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("El asiento debe pertenecer al avión del vuelo.")
        super().save(*args, **kwargs)

class Ticket(models.Model):
    ESTADOS = [("EMI", "Emitido"), ("ANU", "Anulado")]
    reserva = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name="boleto")
    codigo_barra = models.CharField(max_length=32, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=3, choices=ESTADOS, default="EMI")
