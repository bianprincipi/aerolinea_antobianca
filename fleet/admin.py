from django.contrib import admin
from .models import Airplane, Seat

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("modelo","capacidad","filas","columnas")
    search_fields = ("modelo",)
    list_filter = ("filas","columnas")

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("numero","avion","fila","columna","tipo","estado")
    search_fields = ("numero","avion__modelo")
    list_filter = ("tipo","estado","avion")
