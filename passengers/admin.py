from django.contrib import admin
from .models import Passenger

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("nombre","documento","email","telefono","fecha_nacimiento","tipo_documento")
    search_fields = ("nombre","documento","email")
    list_filter = ("tipo_documento",)
