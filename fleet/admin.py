from django.contrib import admin
from .models import Airplane, Seat

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("modelo", "matricula", "capacidad", "filas", "columnas", "ultimo_mantenimiento")
    search_fields = ("modelo", "matricula", "fabricante")
    list_filter = ("fabricante", "filas", "columnas")

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("numero", "avion", "fila", "columna", "tipo", "estado")
    search_fields = ("numero", "avion__modelo")
    list_filter = ("tipo", "estado", "avion")

