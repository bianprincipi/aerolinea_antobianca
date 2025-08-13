from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("vuelos/<int:pk>/", views.flight_detail, name="flight_detail"),
    path("vuelos/<int:pk>/asientos/", views.seat_map, name="seat_map"),
    path("reservas/mias/", views.my_reservations, name="my_reservations"),
]
