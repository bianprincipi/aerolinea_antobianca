from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        AGENT = "AGENT", "Agente"
        CUSTOMER = "CUSTOMER", "Usuario"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)

    @property
    def is_staff_like(self):
        return self.is_staff or self.role in {self.Roles.ADMIN, self.Roles.AGENT}
