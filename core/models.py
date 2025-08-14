from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField()
    filas = models.PositiveIntegerField()
    columnas = models.PositiveIntegerField()

    def clean(self):
        if self.capacidad != self.filas * self.columnas:
            raise ValidationError({'capacidad': 'La capacidad debe coincidir con filas × columnas'})

    def __str__(self):
        return f"{self.modelo} ({self.capacidad} pax)"

class Asiento(models.Model):
    TIPO_CHOICES = [('ECO','Económica'),('PREF','Preferencial')]
    ESTADO_CHOICES = [('DISP','Disponible'),('RES','Reservado'),('OCU','Ocupado')]
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE, related_name='asientos')
    numero = models.CharField(max_length=5)
    fila = models.PositiveIntegerField()
    columna = models.PositiveIntegerField()
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES, default='ECO')
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='DISP')

    class Meta:
        unique_together = [('avion','numero')]
        indexes = [models.Index(fields=['avion','numero'])]

    def __str__(self):
        return f"{self.numero} - {self.avion.modelo}"

class Vuelo(models.Model):
    ESTADO_CHOICES = [
        ('PROG','Programado'),('HORA','En horario'),('DEM','Demorado'),
        ('CANC','Cancelado'),('FIN','Finalizado')
    ]
    avion = models.ForeignKey(Avion, on_delete=models.PROTECT, related_name='vuelos')
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.PositiveIntegerField(help_text='Duración en minutos')
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='PROG')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.fecha_llegada <= self.fecha_salida:
            raise ValidationError({'fecha_llegada': 'La fecha de llegada debe ser posterior a la salida'})
        if self.duracion <= 0:
            raise ValidationError({'duracion': 'La duración debe ser positiva'})

    def __str__(self):
        return f"{self.origen} → {self.destino} ({self.fecha_salida:%Y-%m-%d %H:%M})"

class Pasajero(models.Model):
    TIPO_DOC_CHOICES = [('DNI','DNI'),('PAS','Pasaporte'),('OTR','Otro')]
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pasajero')
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOC_CHOICES, default='DNI')

    class Meta:
        indexes = [models.Index(fields=['documento'])]

    def __str__(self):
        return f"{self.nombre} ({self.documento})"

class Reserva(models.Model):
    ESTADO_CHOICES = [('PEN','Pendiente'),('CONF','Confirmada'),('CANC','Cancelada')]
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name='reservas')
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE, related_name='reservas')
    asiento = models.ForeignKey(Asiento, on_delete=models.PROTECT)
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='PEN')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=12, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vuelo','pasajero'], name='unique_reserva_por_pasajero'),
            models.UniqueConstraint(fields=['vuelo','asiento'], name='unique_reserva_por_asiento'),
        ]
        indexes = [models.Index(fields=['codigo_reserva'])]

    def clean(self):
        if self.asiento and self.vuelo and self.asiento.avion_id != self.vuelo.avion_id:
            raise ValidationError({'asiento': 'El asiento no pertenece al avión de este vuelo.'})

    def __str__(self):
        return f"{self.codigo_reserva} - {self.vuelo} - {self.pasajero}"

class Boleto(models.Model):
    ESTADO_CHOICES = [('EMI','Emitido'),('ANU','Anulado')]
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='boleto')
    codigo_barra = models.ImageField(upload_to='boletos/', blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='EMI')

    def __str__(self):
        return f"Boleto {self.reserva.codigo_reserva}"
