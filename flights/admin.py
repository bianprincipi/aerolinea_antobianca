from django.contrib import admin
from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id","origen","destino","fecha_salida","fecha_llegada","estado","precio_base","avion")
    search_fields = ("origen","destino","avion__modelo")
    list_filter = ("estado","origen","destino")
    date_hierarchy = "fecha_salida"
