from django.db import models

class Passenger(models.Model):
    TIPOS_DOC = [("DNI", "DNI"), ("PAS", "Pasaporte"), ("LE", "LE"), ("LC", "LC")]

    nombre = models.CharField(max_length=120)
    documento = models.CharField(max_length=32, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=32)
    fecha_nacimiento = models.DateField()
    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOC)

    def __str__(self):
        return f"{self.nombre} ({self.documento})"
