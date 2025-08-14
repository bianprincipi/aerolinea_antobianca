from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.apps import apps
from datetime import timedelta
import random, string

class Command(BaseCommand):
    help = "Carga datos demo (admin, usuarios, aviones, asientos, vuelos y algunas reservas)"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        Airplane = apps.get_model('fleet','Airplane')
        Seat     = apps.get_model('fleet','Seat')
        Flight   = apps.get_model('flights','Flight')
        Passenger= apps.get_model('passengers','Passenger')
        Reservation = apps.get_model('booking','Reservation')

        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin','admin@example.com','admin123')
            self.stdout.write(self.style.SUCCESS("Admin creado: admin / admin123"))
        else:
            self.stdout.write("Admin ya existe")

        # Usuarios demo
        for u in ('sofia','lara','constanza'):
            obj, created = User.objects.get_or_create(username=u, defaults={'email': f'{u}@example.com'})
            if created:
                obj.set_password('pass12345'); obj.save()
        self.stdout.write(self.style.SUCCESS("Usuarios: sofia / lara / constanza (pass: pass12345)"))

        # Aviones
        planes = [
            dict(modelo='Boeing 737-800', filas=4, columnas=6),
            dict(modelo='Airbus A320',   filas=5, columnas=6),
            dict(modelo='Embraer E190',  filas=5, columnas=4),
        ]
        for p in planes:
            p['capacidad'] = p['filas'] * p['columnas']
            a, _ = Airplane.objects.get_or_create(**p)
            # Asientos
            creados = 0
            for f in range(1, a.filas+1):
                for c in range(1, a.columnas+1):
                    numero = f"{chr(64+f)}{c}"
                    _, made = Seat.objects.get_or_create(
                        avion=a, numero=numero,
                        defaults={'fila': f, 'columna': c, 'tipo': 'ECO', 'estado': 'DISP'}
                    )
                    if made: creados += 1
            self.stdout.write(f"✈ {a.modelo}: {creados} asientos nuevos")

        # Vuelos
        base = timezone.now().replace(minute=0, second=0, microsecond=0)
        ciudades = ['AEP','EZE','COR','MDZ','BRC','IGR','SAL','NQN','ROS','USH','FTE']
        planes_all = list(Airplane.objects.all())
        created = 0
        for i in range(8):
            av = random.choice(planes_all)
            o = random.choice(ciudades)
            d = random.choice([x for x in ciudades if x != o])
            salida = (base + timedelta(days=random.randint(0,5))).replace(hour=random.choice([6,9,12,15,18]))
            mins = random.choice([70,90,110,120,150])
            llegada = salida + timedelta(minutes=mins)
            obj, made = Flight.objects.get_or_create(
                avion=av, origen=o, destino=d, fecha_salida=salida,
                defaults={'fecha_llegada': llegada, 'duracion': timedelta(minutes=mins), 'estado':'programado', 'precio_base': random.choice([15000,18000,20000,22000])}
            )
            if made: created += 1
        self.stdout.write(self.style.SUCCESS(f"Vuelos creados: {created}"))

        # Pasajeros demo (vinculados por email)
        for name, doc, email in [
            ("Sofía Demo", "30111222", "sofia@example.com"),
            ("Lara Demo",  "31222333", "lara@example.com"),
            ("Constanza",  "32333444", "constanza@example.com"),
        ]:
            Passenger.objects.get_or_create(nombre=name, documento=doc, email=email, defaults={"fecha_nacimiento": timezone.now().date().replace(year=1995), "tipo_documento":"DNI"})

        # Una reserva de ejemplo
        vuelo = Flight.objects.order_by('id').first()
        asiento = Seat.objects.filter(avion=vuelo.avion).first()
        pasajero = Passenger.objects.filter(email="sofia@example.com").first()
        if vuelo and asiento and pasajero:
            code = ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))
            Reservation.objects.get_or_create(
                vuelo=vuelo, pasajero=pasajero, asiento=asiento,
                defaults={'precio': vuelo.precio_base, 'estado': 'CONF', 'codigo_reserva': code}
            )
            self.stdout.write(self.style.SUCCESS("Reserva demo creada"))
        self.stdout.write(self.style.SUCCESS("Seed demo listo"))
