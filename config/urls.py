from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Backend is running — API is available at /api/")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('appointments.urls')),
]
