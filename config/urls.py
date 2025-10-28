# config/urls.py
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def api_root(_request):
    return JsonResponse({
        "ok": True,
        "service": "Community Health API",
        "endpoints": [
            "/healthz",
            "/api/appointments/ (once wired)",
            "/api/providers/    (once wired)",
        ],
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", lambda r: JsonResponse({"status": "ok"})),
    path("", lambda r: JsonResponse({"message": "Welcome to Community Health"})),
    path("api/", api_root),  # <— this creates /api/
    # path("api/", include("appointments.api_urls")),  # <— add later when you expose real endpoints
]
