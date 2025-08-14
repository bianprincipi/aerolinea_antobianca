from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Avion, Asiento

@receiver(post_save, sender=Avion)
def generar_asientos(sender, instance: Avion, created, **kwargs):
    def _regenerar():
        instance.asientos.all().delete()
        for f in range(1, instance.filas + 1):
            for c in range(1, instance.columnas + 1):
                numero = f"{f}{chr(64 + c)}"  # 1A, 1B, ...
                Asiento.objects.create(
                    avion=instance, numero=numero, fila=f, columna=c,
                    tipo='ECO', estado='DISP'
                )
    transaction.on_commit(_regenerar)
