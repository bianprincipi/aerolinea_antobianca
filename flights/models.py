from django.db import models
from fleet.models import Airplane
from django.conf import settings

class Flight(models.Model):
    ESTADOS = [
        ("PROG", "Programado"),
        ("ABOR", "Abordando"),
        ("ENVO", "En vuelo"),
        ("CANC", "Cancelado"),
        ("FIN", "Finalizado"),
    ]

    avion = models.ForeignKey(Airplane, on_delete=models.PROTECT, related_name="vuelos")
    origen = models.CharField(max_length=80)
    destino = models.CharField(max_length=80)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField()
    estado = models.CharField(max_length=5, choices=ESTADOS, default="PROG")
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="flights_managed",
        help_text="Usuarios que gestionan este vuelo",
    )
    class Meta:
        ordering = ["fecha_salida"]
        indexes = [models.Index(fields=["origen", "destino", "fecha_salida"])]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_llegada <= self.fecha_salida:
            raise ValidationError("La fecha de llegada debe ser posterior a la salida.")
