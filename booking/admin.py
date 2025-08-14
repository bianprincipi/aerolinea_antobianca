from django.contrib import admin
from .models import Reservation, Ticket

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("codigo_reserva","vuelo","pasajero","asiento","precio","estado","fecha_reserva")
    search_fields = ("codigo_reserva","pasajero__nombre","pasajero__documento","vuelo__origen","vuelo__destino")
    list_filter = ("estado","vuelo__origen","vuelo__destino")
    autocomplete_fields = ("vuelo","pasajero","asiento")

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("reserva","fecha_emision","estado","codigo_barra")
    search_fields = ("reserva__codigo_reserva",)
    list_filter = ("estado",)
