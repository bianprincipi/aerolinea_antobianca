from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('portal_app.urls')),

    path("admin/", admin.site.urls),
    path("", include(("web.urls", "web"), namespace="web")),
    path("cuentas/", include(("accounts.urls", "accounts"), namespace="accounts")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
