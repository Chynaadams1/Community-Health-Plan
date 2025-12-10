from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import provider_update   # <--- IMPORTANT

urlpatterns = [

    # ========================================================
    # AUTH
    # ========================================================
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),

    # ========================================================
    # APPOINTMENTS
    # ========================================================
    path("appointments/", views.appointment_list, name="appointment-list"),
    path("appointments/<int:apt_id>/", views.appointment_detail, name="appointment-detail"),
    path("appointments/<int:apt_id>/cancel/", views.cancel_appointment, name="appointment-cancel"),
    path("appointments/<int:apt_id>/complete/", views.complete_appointment, name="appointment-complete"),
    path("appointments/<int:apt_id>/reschedule/", views.reschedule_appointment, name="appointment-reschedule"),

    # ========================================================
    # PROVIDERS
    # ========================================================
    path("providers/", views.provider_list, name="provider-list"),
    path("providers/<int:provider_id>/", views.provider_detail, name="provider-detail"),

    # Provider profile update endpoint
    path("providers/<int:provider_id>/update/", provider_update, name="provider-update"),

    # Provider photo upload endpoint
    path("providers/<int:provider_id>/upload-photo/", views.provider_upload_photo),

    # Provider appointments
    path("providers/<int:provider_id>/appointments/", views.provider_appointments),
    path("providers/<int:provider_id>/appointments/upcoming/", views.provider_upcoming),
    path("providers/<int:provider_id>/appointments/past/", views.provider_past),
    path("providers/<int:provider_id>/appointments/today/", views.provider_today),

    # Provider analytics
    path("providers/<int:provider_id>/analytics/", views.provider_analytics, name="provider-analytics"),

    # ========================================================
    # PATIENT DASHBOARD
    # ========================================================
    path("patients/<int:patient_id>/appointments/", views.patient_appointments),
    path("patients/<int:patient_id>/appointments/upcoming/", views.patient_upcoming),
    path("patients/<int:patient_id>/appointments/past/", views.patient_past),

    # ========================================================
    # SPECIALTIES CRUD (ADMIN)
    # ========================================================
    path("admin/specialties/", views.specialty_list),
    path("admin/specialties/create/", views.specialty_create),
    path("admin/specialties/<int:spec_id>/update/", views.specialty_update),
    path("admin/specialties/<int:spec_id>/delete/", views.specialty_delete),

    # ========================================================
    # AVAILABILITY CRUD
    # ========================================================
    path("availability/", views.availability_list),
    path("availability/provider/<int:provider_id>/", views.provider_availability),
    path("availability/create/", views.create_availability),
    path("availability/<int:avail_id>/update/", views.update_availability),
    path("availability/<int:avail_id>/delete/", views.delete_availability),

    # ========================================================
    # ADMIN PROVIDERS
    # ========================================================
    path("admin/providers/", views.admin_provider_list, name="admin-provider-list"),
    path("admin/providers/<int:provider_id>/toggle/", views.admin_toggle_provider, name="admin-provider-toggle"),
    path("admin/stats/", views.admin_stats, name="admin-stats"),
]

# --------------------------------------------------------------
# SERVE MEDIA FILES IN DEVELOPMENT (provider photos)
# --------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
