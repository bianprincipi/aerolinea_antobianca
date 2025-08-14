# flights/admin.py
from django.contrib import admin
from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "origen",
        "destino",
        "fecha_salida",
        "fecha_llegada",
        "precio_base",
        "estado",
    )
    list_filter = ("origen", "destino", "estado")
    date_hierarchy = "fecha_salida"
    ordering = ("fecha_salida",)

    # ⚠️ Requisito para que funcione el autocomplete desde ReservationAdmin
    search_fields = (
        "origen",
        "destino",
        "avion__modelo", # FK al avión (opcional, si existe)
    )

    # Opcional: si en tu admin querés autocompletar el avión
    autocomplete_fields = ("avion",)  # quitá si no existe el FK
