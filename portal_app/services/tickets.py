import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generar_boleto_qr(reserva, boleto_model):
    if hasattr(reserva, 'boleto') and reserva.boleto:
        return reserva.boleto
    data = f"RESERVA:{getattr(reserva,'codigo_reserva',reserva.pk)}|PAS:{getattr(reserva.pasajero,'documento',getattr(reserva.pasajero,'document',reserva.pasajero_id))}|VUELO:{getattr(reserva.vuelo,'id',None)}"
    img = qrcode.make(data)
    buf = BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
    boleto = boleto_model.objects.create(reserva=reserva)
    boleto.codigo_barra.save(f"{getattr(reserva,'codigo_reserva','ticket')}.png", ContentFile(buf.read()))
    boleto.save()
    return boleto
