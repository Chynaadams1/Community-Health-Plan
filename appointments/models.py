from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


# ======================================
# SPECIALTY
# ======================================
class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ======================================
# PROVIDER
# ======================================
class Provider(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="provider_profile"
    )
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT)
    location = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)


    # NEW — profile photo for providers
    profile_photo = models.ImageField(
        upload_to="provider_photos/",
        blank=True,
        null=True
    )

    # NEW — approval system for admin dashboard
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        display = self.user.get_full_name() or self.user.username
        return f"{display} ({self.specialty})"


# ======================================
# AVAILABILITY
# ======================================
class Availability(models.Model):
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["provider", "start", "end"])]

    def __str__(self):
        return f"{self.provider} | {self.start:%Y-%m-%d %H:%M} - {self.end:%H:%M}"


# ======================================
# APPOINTMENT
# ======================================
class Appointment(models.Model):

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    # denormalized fields
    patient_name = models.CharField(max_length=120, blank=True)
    provider_name = models.CharField(max_length=120, blank=True)
    service = models.CharField(max_length=120, blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField()

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.REQUESTED
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "start", "end")
        indexes = [models.Index(fields=["provider", "start", "end"])]

    def __str__(self):
        return f"{self.patient} → {self.provider} ({self.start:%Y-%m-%d %H:%M})"


# ======================================
# CHAT HISTORY
# ======================================
class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    user_message = models.TextField()
    bot_response = models.TextField(blank=True)
    model_name = models.CharField(max_length=80, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat #{self.session_id} @ {self.created_at:%Y-%m-%d %H:%M}"


# ======================================
# DOCTOR NOTES
# ======================================
class DoctorNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="doctor_notes"
    )
    author_name = models.CharField(max_length=120)
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.author_name} on {self.appointment_id}"
