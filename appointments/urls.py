from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    
    # Specialties
    path('specialties/', views.specialty_list, name='specialty_list'),
    
    # Providers
    path('providers/', views.provider_list, name='provider_list'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/availability/', views.provider_availability, name='provider_availability'),
    
    # Availability
    path('availability/', views.availability_list, name='availability_list'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
]
