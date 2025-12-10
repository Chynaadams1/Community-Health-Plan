from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import json

from .models import Appointment, Provider, Specialty, Availability

User = get_user_model()

# ======================================================
# AUTH — REGISTER
# ======================================================
@csrf_exempt
def register(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
    except:
        return HttpResponseBadRequest("Invalid JSON")

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return HttpResponseBadRequest("Username and password required")

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    user = User.objects.create(
        username=username,
        email=data.get("email", ""),
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        password=make_password(password),
    )

    return JsonResponse({"status": "created", "user": {"id": user.id}}, status=201)

# ======================================================
# AUTH — LOGIN
# ======================================================
@csrf_exempt
def login(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data = json.loads(request.body)
    user = authenticate(username=data.get("username"), password=data.get("password"))

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # Determine role
    if hasattr(user, "provider_profile"):
        role = "provider"
        provider_id = user.provider_profile.id
    elif user.is_staff:
        role = "admin"
        provider_id = None
    else:
        role = "patient"
        provider_id = None

    return JsonResponse({
        "status": "ok",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role,
            "provider_id": provider_id,
        }
    })

# ======================================================
# PROVIDERS — LIST
# ======================================================
def provider_list(request):
    providers = Provider.objects.select_related("user", "specialty")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "first_name": p.user.first_name,
                "last_name": p.user.last_name,
                "email": p.user.email,
                "user_name": p.user.get_full_name() or p.user.username,
                "specialty_name": p.specialty.name if p.specialty else None,
                "specialty_id": p.specialty_id,
                "location": p.location,
                "bio": p.bio,
                "profile_photo": p.profile_photo.url if p.profile_photo else None,
            }
            for p in providers
        ]
    })

# ======================================================
# PROVIDER DETAIL
# ======================================================
def provider_detail(request, provider_id):
    try:
        p = Provider.objects.select_related("user", "specialty").get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    return JsonResponse({
        "status": "ok",
        "item": {
            "id": p.id,
            "first_name": p.user.first_name,
            "last_name": p.user.last_name,
            "email": p.user.email,
            "user_name": p.user.get_full_name() or p.user.username,
            "specialty_name": p.specialty.name if p.specialty else None,
            "specialty_id": p.specialty_id,
            "location": p.location,
            "bio": p.bio,
            "profile_photo": p.profile_photo.url if p.profile_photo else None,
        }
    })

# ======================================================
# PROVIDER UPDATE
# ======================================================
@csrf_exempt
def provider_update(request, provider_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        provider = Provider.objects.select_related("user").get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Provider not found"}, status=404)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Update user
    user = provider.user
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.save()

    provider.location = data.get("location", provider.location)
    provider.bio = data.get("bio", provider.bio)

    specialty_id = data.get("specialty_id")
    if specialty_id:
        try:
            provider.specialty = Specialty.objects.get(id=specialty_id)
        except Specialty.DoesNotExist:
            return JsonResponse({"error": "Invalid specialty"}, status=400)

    provider.save()
    return JsonResponse({"status": "updated"})

# ======================================================
# PROVIDER PHOTO UPLOAD
# ======================================================
@csrf_exempt
def provider_upload_photo(request, provider_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Provider not found"}, status=404)

    if "photo" not in request.FILES:
        return JsonResponse({"error": "No photo uploaded"}, status=400)

    provider.profile_photo = request.FILES["photo"]
    provider.save()

    return JsonResponse({
        "status": "uploaded",
        "photo_url": provider.profile_photo.url,
    })

# ======================================================
# PROVIDER APPOINTMENTS
# ======================================================
def provider_appointments(request, provider_id):
    qs = Appointment.objects.filter(provider_id=provider_id).order_by("start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "patient": a.patient_id,
                "patient_name": a.patient_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PROVIDER TODAY
# ======================================================
def provider_today(request, provider_id):
    now = timezone.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    qs = Appointment.objects.filter(
        provider_id=provider_id,
        start__gte=start,
        start__lt=end
    ).select_related("provider__user").order_by("start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name(),
                "patient": a.patient_id,
                "patient_name": a.patient_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PROVIDER UPCOMING
# ======================================================
def provider_upcoming(request, provider_id):
    qs = Appointment.objects.filter(
        provider_id=provider_id,
        start__gte=timezone.now()
    ).select_related("provider__user").order_by("start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name(),
                "patient": a.patient_id,
                "patient_name": a.patient_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PROVIDER PAST
# ======================================================
def provider_past(request, provider_id):
    qs = Appointment.objects.filter(
        provider_id=provider_id,
        end__lt=timezone.now()
    ).select_related("provider__user").order_by("-start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name(),
                "patient": a.patient_id,
                "patient_name": a.patient_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PROVIDER ANALYTICS
# ======================================================
def provider_analytics(request, provider_id):
    total = Appointment.objects.filter(provider_id=provider_id).count()
    upcoming = Appointment.objects.filter(provider_id=provider_id, start__gte=timezone.now()).count()

    return JsonResponse({
        "status": "ok",
        "total_appointments": total,
        "upcoming": upcoming
    })

# ======================================================
# PATIENT — UPCOMING
# ======================================================
def patient_upcoming(request, patient_id):
    qs = Appointment.objects.filter(
        patient_id=patient_id,
        start__gte=timezone.now()
    ).select_related("provider__user").order_by("start")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name() or a.provider.user.username,
                "provider_photo": a.provider.profile_photo.url if a.provider.profile_photo else None,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PATIENT — ALL APPOINTMENTS
# ======================================================
def patient_appointments(request, patient_id):
    qs = Appointment.objects.filter(
        patient_id=patient_id
    ).select_related("provider__user").order_by("start")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name() or a.provider.user.username,
                "provider_photo": a.provider.profile_photo.url if a.provider.profile_photo else None,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# PATIENT — PAST APPOINTMENTS
# ======================================================
def patient_past(request, patient_id):
    now = timezone.now()
    qs = Appointment.objects.filter(
        patient_id=patient_id,
        end__lt=now
    ).select_related("provider__user").order_by("-start")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name(),
                "provider_photo": a.provider.profile_photo.url if a.provider.profile_photo else None,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# APPOINTMENTS — LIST ALL
# ======================================================
def appointment_list(request):
    qs = Appointment.objects.select_related("provider__user").order_by("-start")
    
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    
    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "patient": a.patient_id,
                "patient_name": a.patient_name,
                "provider": a.provider_id,
                "provider_name": a.provider.user.get_full_name() or a.provider.user.username,
                "provider_photo": a.provider.profile_photo.url if a.provider.profile_photo else None,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })

# ======================================================
# APPOINTMENT DETAIL
# ======================================================
def appointment_detail(request, apt_id):
    try:
        apt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Appointment not found"}, status=404)

    return JsonResponse({
        "id": apt.id,
        "patient": apt.patient_id,
        "patient_name": apt.patient_name,
        "provider": apt.provider_id,
        "provider_name": apt.provider_name,
        "service": apt.service,
        "start": apt.start.isoformat(),
        "end": apt.end.isoformat(),
        "status": apt.status,
    })

# ======================================================
# CANCEL APPOINTMENT
# ======================================================
@csrf_exempt
def cancel_appointment(request, apt_id):
    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    appt.status = "cancelled"
    appt.save()

    return JsonResponse({"status": "cancelled"})

# ======================================================
# COMPLETE APPOINTMENT
# ======================================================
@csrf_exempt
def complete_appointment(request, apt_id):
    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    appt.status = "completed"
    appt.save()

    return JsonResponse({"status": "completed"})

# ======================================================
# RESCHEDULE APPOINTMENT
# ======================================================
@csrf_exempt
def reschedule_appointment(request, apt_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    data = json.loads(request.body)
    new_dt = data.get("datetime")

    if not new_dt:
        return JsonResponse({"error": "Missing datetime"}, status=400)

    new_start = parse_datetime(new_dt)
    if not new_start:
        return JsonResponse({"error": "Invalid datetime"}, status=400)

    new_end = new_start + timedelta(minutes=30)

    appt.start = new_start
    appt.end = new_end
    appt.save()

    return JsonResponse({"status": "rescheduled"})

# ======================================================
# SPECIALTIES — LIST
# ======================================================
def specialty_list(request):
    specialties = Specialty.objects.all()
    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
            }
            for s in specialties
        ]
    })

# ======================================================
# SPECIALTIES — CREATE
# ======================================================
@csrf_exempt
def specialty_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    name = data.get("name", "").strip()
    if not name:
        return JsonResponse({"error": "Name is required"}, status=400)
    
    specialty = Specialty.objects.create(
        name=name,
        description=data.get("description", "")
    )
    
    return JsonResponse({
        "status": "created",
        "item": {
            "id": specialty.id,
            "name": specialty.name,
            "description": specialty.description,
        }
    }, status=201)

# ======================================================
# SPECIALTIES — UPDATE
# ======================================================
@csrf_exempt
def specialty_update(request, spec_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])
    
    try:
        specialty = Specialty.objects.get(id=spec_id)
    except Specialty.DoesNotExist:
        return JsonResponse({"error": "Specialty not found"}, status=404)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    specialty.name = data.get("name", specialty.name)
    specialty.description = data.get("description", specialty.description)
    specialty.save()
    
    return JsonResponse({"status": "updated"})

# ======================================================
# SPECIALTIES — DELETE
# ======================================================
@csrf_exempt
def specialty_delete(request, spec_id):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        specialty = Specialty.objects.get(id=spec_id)
    except Specialty.DoesNotExist:
        return JsonResponse({"error": "Specialty not found"}, status=404)
    
    specialty.delete()
    return JsonResponse({"status": "deleted"})

# ======================================================
# AVAILABILITY — LIST ALL
# ======================================================
def availability_list(request):
    availabilities = Availability.objects.select_related("provider__user").all()
    
    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "provider_id": a.provider_id,
                "provider_name": a.provider.user.get_full_name() or a.provider.user.username,
                "day_of_week": a.day_of_week,
                "start_time": a.start_time.isoformat(),
                "end_time": a.end_time.isoformat(),
            }
            for a in availabilities
        ]
    })

# ======================================================
# AVAILABILITY — BY PROVIDER
# ======================================================
def provider_availability(request, provider_id):
    availabilities = Availability.objects.filter(provider_id=provider_id)
    
    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": a.id,
                "provider_id": a.provider_id,
                "day_of_week": a.day_of_week,
                "start_time": a.start_time.isoformat(),
                "end_time": a.end_time.isoformat(),
            }
            for a in availabilities
        ]
    })

# ======================================================
# AVAILABILITY — CREATE
# ======================================================
@csrf_exempt
def create_availability(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    provider_id = data.get("provider_id")
    day_of_week = data.get("day_of_week")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    
    if not all([provider_id, day_of_week, start_time, end_time]):
        return JsonResponse({"error": "Missing required fields"}, status=400)
    
    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Provider not found"}, status=404)
    
    availability = Availability.objects.create(
        provider=provider,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time
    )
    
    return JsonResponse({
        "status": "created",
        "item": {
            "id": availability.id,
            "provider_id": availability.provider_id,
            "day_of_week": availability.day_of_week,
            "start_time": availability.start_time.isoformat(),
            "end_time": availability.end_time.isoformat(),
        }
    }, status=201)

# ======================================================
# AVAILABILITY — UPDATE
# ======================================================
@csrf_exempt
def update_availability(request, avail_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])
    
    try:
        availability = Availability.objects.get(id=avail_id)
    except Availability.DoesNotExist:
        return JsonResponse({"error": "Availability not found"}, status=404)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    availability.day_of_week = data.get("day_of_week", availability.day_of_week)
    availability.start_time = data.get("start_time", availability.start_time)
    availability.end_time = data.get("end_time", availability.end_time)
    availability.save()
    
    return JsonResponse({"status": "updated"})

# ======================================================
# AVAILABILITY — DELETE
# ======================================================
@csrf_exempt
def delete_availability(request, avail_id):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        availability = Availability.objects.get(id=avail_id)
    except Availability.DoesNotExist:
        return JsonResponse({"error": "Availability not found"}, status=404)
    
    availability.delete()
    return JsonResponse({"status": "deleted"})

# ======================================================
# ADMIN — PROVIDER LIST
# ======================================================
def admin_provider_list(request):
    providers = Provider.objects.select_related("user", "specialty").all()
    
    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "first_name": p.user.first_name,
                "last_name": p.user.last_name,
                "email": p.user.email,
                "specialty_name": p.specialty.name if p.specialty else None,
                "location": p.location,
                "is_active": p.user.is_active,
            }
            for p in providers
        ]
    })

# ======================================================
# ADMIN — TOGGLE PROVIDER ACTIVE STATUS
# ======================================================
@csrf_exempt
def admin_toggle_provider(request, provider_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        provider = Provider.objects.select_related("user").get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Provider not found"}, status=404)
    
    provider.user.is_active = not provider.user.is_active
    provider.user.save()
    
    return JsonResponse({
        "status": "updated",
        "is_active": provider.user.is_active
    })

# ======================================================
# ADMIN — STATISTICS
# ======================================================
def admin_stats(request):
    total_providers = Provider.objects.count()
    total_appointments = Appointment.objects.count()
    total_patients = User.objects.filter(is_staff=False).exclude(provider_profile__isnull=False).count()
    
    return JsonResponse({
        "status": "ok",
        "stats": {
            "total_providers": total_providers,
            "total_appointments": total_appointments,
            "total_patients": total_patients,
        }
    })