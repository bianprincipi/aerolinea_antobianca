from django.urls import path
from . import views

urlpatterns = [
    path('reservas/<str:codigo>/boleto.pdf', views.descargar_boleto_pdf, name='portal_boleto_pdf'),

    path('reservas/cambiar/<int:vuelo_id>/<int:asiento_id>/', views.cambiar_asiento, name='portal_cambiar_asiento'),

    path('signup/', views.signup, name='signup'),

    path('', views.home, name='portal_home'),
    path('vuelos/', views.buscar_vuelos, name='portal_buscar_vuelos'),
    path('vuelos/<int:pk>/', views.vuelo_detalle, name='portal_vuelo_detalle'),
    path('reservas/crear/<int:vuelo_id>/<int:asiento_id>/', views.crear_reserva, name='portal_crear_reserva'),
    path('reservas/<str:codigo>/boleto/', views.ver_boleto, name='portal_ver_boleto'),
    path('perfil/', views.perfil, name='portal_perfil'),
    path('historial/', views.historial, name='portal_historial'),
    path('reportes/pasajeros-por-vuelo/<int:vuelo_id>/', views.pasajeros_por_vuelo, name='portal_pasajeros_por_vuelo'),
]
