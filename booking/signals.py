from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Reservation, Ticket
from .models import Reservation as R

@receiver(post_save, sender=Reservation)
def issue_ticket_on_paid(sender, instance, created, **kwargs):
    # Si la reserva está PAGADA y no hay boleto, emitir
    if instance.estado == "PAG" and not hasattr(instance, "boleto"):
        Ticket.objects.create(reserva=instance, codigo_barra=gen_barcode())
