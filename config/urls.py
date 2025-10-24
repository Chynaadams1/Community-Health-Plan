"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(_request):
    return HttpResponse(
        "✅ Community Health app is live. Visit <a href='/admin/'>/admin</a>.",
        content_type="text/html",
    )

def health(_request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path("", home),            # /
    path("healthz/", health),  # /healthz/  (note the trailing slash)
    path("admin/", admin.site.urls),
]
