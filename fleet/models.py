from django.db import models

class Airplane(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField()
    filas = models.PositiveIntegerField()
    columnas = models.PositiveIntegerField()
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    fabricante = models.CharField(max_length=50, null=True, blank=True)
    anio_fabricacion = models.PositiveIntegerField(null=True, blank=True)
    ultimo_mantenimiento = models.DateField(null=True, blank=True)
    notas_tecnicas = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.modelo} ({self.filas}x{self.columnas})"

class Seat(models.Model):
    TIPOS = [("ECO", "Económica"), ("BUS", "Business"), ("PRE", "Premium")]
    ESTADOS = [("DISP", "Disponible"), ("RES", "Reservado"), ("OCU", "Ocupado")]

    avion = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="asientos")
    numero = models.CharField(max_length=5)
    fila = models.PositiveIntegerField()
    columna = models.CharField(max_length=1)
    tipo = models.CharField(max_length=3, choices=TIPOS, default="ECO")
    estado = models.CharField(max_length=4, choices=ESTADOS, default="DISP")
    class Meta:
        unique_together = ("avion", "numero")
        indexes = [models.Index(fields=["avion", "numero"])]

    def __str__(self):
        return f"{self.numero} - {self.avion.modelo}"
