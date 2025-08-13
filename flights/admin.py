from django.contrib import admin
from .models import Flight
from django.http import HttpResponse
import csv

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("origen","destino","fecha_salida","avion","estado")
    actions = ["export_passengers_csv"]

    def export_passengers_csv(self, request, queryset):
        """
        Exporta un CSV con: Vuelo, Origen, Destino, Pasajero, Documento, Asiento, Estado Reserva
        """
        from booking.models import Reservation
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pasajeros_por_vuelo.csv"'
        writer = csv.writer(response)
        writer.writerow(["Vuelo","Origen","Destino","Salida","Pasajero","Documento","Asiento","Estado Reserva"])
        for flight in queryset:
            reservas = Reservation.objects.filter(vuelo=flight).select_related("pasajero","asiento")
            for r in reservas:
                writer.writerow([
                    flight.id, flight.origen, flight.destino, flight.fecha_salida,
                    r.pasajero.nombre, r.pasajero.documento,
                    getattr(r.asiento, "numero", "-"),
                    r.get_estado_display()
                ])
        return response
    export_passengers_csv.short_description = "Exportar pasajeros (CSV)"
