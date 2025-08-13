from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation

@receiver(post_save, sender=Reservation)
def sync_seat_state(sender, instance, created, **kwargs):
    if instance.asiento:
        seat = instance.asiento
        seat.estado = "OCU" if instance.estado == "PAG" else "RES"
        seat.save(update_fields=["estado"])
