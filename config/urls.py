# config/urls.py
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.urls import path

def api_root(_request):
    return JsonResponse({
        "ok": True,
        "service": "Community Health API",
        "endpoints": [
            "/healthz",
            "/api/appointments/ (coming soon)",
            "/api/providers/    (coming soon)",
        ],
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", lambda r: JsonResponse({"status": "ok"})),
    path("", lambda r: JsonResponse({"message": "Welcome to Community Health"})),
    path("api/", api_root),                             # <— /api/
    path("version.txt", lambda r: HttpResponse("ok")),  # <— sanity check
]
