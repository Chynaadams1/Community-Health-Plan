from django.contrib import admin
from .models import Specialty, Provider, Availability, Appointment, ChatHistory, DoctorNote

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "location")
    search_fields = ("user__username", "user__first_name", "user__last_name", "location")

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("provider", "start", "end")
    list_filter = ("provider",)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "provider", "start", "end", "status", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("patient__username", "provider__user__username", "patient_name", "provider_name", "service")
    ordering = ("-created_at",)

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("session_id", "created_at", "model_name")
    search_fields = ("session_id", "user_message", "bot_response")

@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ("appointment", "author_name", "created_at")
    search_fields = ("author_name", "note_text")
