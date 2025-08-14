from io import BytesIO
from django.apps import apps
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import IntegrityError
import qrcode, random, string

def _is_filefield(model, field_name):
    try:
        f = model._meta.get_field(field_name)
        return hasattr(f, 'upload_to')
    except Exception:
        return False

def _unique_payload(base_payload, Ticket, max_tries=5):
    """
    Devuelve un payload único para codigo_barra cuando el campo es CharField unique.
    """
    payload = base_payload
    for i in range(max_tries):
        exists = Ticket.objects.filter(codigo_barra=payload).exists()
        if not exists:
            return payload
        # agregar sufijo aleatorio y reintentar
        suf = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        payload = f"{base_payload}-{suf}"
    return payload  # último intento igualmente distinto

def generar_boleto_qr(reserva):
    """
    Asegura un Ticket para la reserva y genera un QR.
    - Si 'codigo_barra' es Image/FileField => guarda PNG con filename único.
    - Si 'codigo_barra' es CharField (unique) => garantiza texto único.
    """
    Ticket = apps.get_model('booking', 'Ticket')
    ticket, _ = Ticket.objects.get_or_create(
        reserva=reserva,
        defaults={'fecha_emision': timezone.now(), 'estado': 'emitido'}
    )

    # Si ya tiene valor, no lo volvemos a generar
    try:
        existing = getattr(ticket, 'codigo_barra', None)
        if existing:  # ya hay código/imagen cargada
            return ticket
    except Exception:
        pass

    # Construir base del payload a partir del código de reserva
    code = getattr(reserva, 'codigo_reserva', None) or getattr(reserva, 'code', None) or f"RES-{reserva.pk}"
    base_payload = f"RES:{code}"

    if _is_filefield(Ticket, 'codigo_barra'):
        # Generar imagen PNG en memoria
        img = qrcode.make(base_payload)
        buff = BytesIO()
        img.save(buff, format='PNG')
        buff.seek(0)

        # Nombre de archivo único
        filename_base = f"qr_{code}"
        filename = f"{filename_base}.png"
        # En caso de colisión por unique, reintentar con sufijo
        for i in range(5):
            try:
                ticket.codigo_barra.save(filename, ContentFile(buff.getvalue()), save=False)
                ticket.fecha_emision = ticket.fecha_emision or timezone.now()
                if not getattr(ticket, 'estado', None):
                    ticket.estado = 'emitido'
                ticket.save()
                return ticket
            except IntegrityError:
                suf = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                filename = f"{filename_base}_{suf}.png"
        # Último intento fuera del loop
        ticket.codigo_barra.save(filename, ContentFile(buff.getvalue()), save=False)
    else:
        # CharField: asegurar unicidad del texto
        payload = _unique_payload(base_payload, Ticket, max_tries=7)
        setattr(ticket, 'codigo_barra', payload)

    ticket.fecha_emision = ticket.fecha_emision or timezone.now()
    if not getattr(ticket, 'estado', None):
        ticket.estado = 'emitido'
    ticket.save()
    return ticket
