from django.db import models
from django.contrib.auth.models import User

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="pending",
    )

    def __str__(self):
        return f"{self.patient.username} → {self.provider.user.username} on {self.date}"
