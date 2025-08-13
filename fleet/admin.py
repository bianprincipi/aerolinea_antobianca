from django.contrib import admin
from .models import Airplane, Seat

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
<<<<<<< HEAD
    list_display = ("modelo","capacidad","filas","columnas")
    search_fields = ("modelo",)
    list_filter = ("filas","columnas")

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("numero","avion","fila","columna","tipo","estado")
    search_fields = ("numero","avion__modelo")
    list_filter = ("tipo","estado","avion")
=======
    list_display = ("modelo","matricula","capacidad","filas","columnas","ultimo_mantenimiento")
    search_fields = ("modelo","matricula","fabricante")
    list_filter = ("fabricante",)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("avion","numero","tipo","estado")
    list_filter = ("avion","tipo","estado")
>>>>>>> 50499df (faet(fleet): datos tecnicos de avion (matricula, fabricante, mantenimiento))
