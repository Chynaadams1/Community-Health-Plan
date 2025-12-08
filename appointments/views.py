from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import timedelta
import json

from .models import Appointment, Provider, Specialty, Availability

User = get_user_model()

# ========================================================
# AUTH: REGISTER
# ========================================================
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


# ========================================================
# AUTH: LOGIN
# ========================================================
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


# ========================================================
# PROVIDERS LIST + DETAIL
# ========================================================
def provider_list(request):
    providers = Provider.objects.select_related("user", "specialty")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "user_name": p.user.get_full_name() or p.user.username,
                "specialty_name": p.specialty.name,
                "location": p.location,
                "profile_photo": p.profile_photo.url if p.profile_photo else None,
            }
            for p in providers
        ]
    })


def provider_detail(request, provider_id):
    try:
        p = Provider.objects.select_related("user", "specialty").get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    return JsonResponse({
        "status": "ok",
        "item": {
            "id": p.id,
            "user_name": p.user.get_full_name() or p.user.username,
            "specialty_name": p.specialty.name,
            "location": p.location,
            "profile_photo": p.profile_photo.url if p.profile_photo else None,
        }
    })

    


# ========================================================
# PROVIDER PHOTO UPLOAD
# ========================================================
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


# ========================================================
# ADMIN — PROVIDER LIST + TOGGLE APPROVAL
# ========================================================
def admin_provider_list(request):
    qs = Provider.objects.select_related("user", "specialty")

    return JsonResponse({
        "status": "ok",
        "providers": [
            {
                "id": p.id,
                "user_name": p.user.get_full_name(),
                "email": p.user.email,
                "specialty": p.specialty.name,
                "location": p.location,
                "is_approved": p.is_approved,
                "profile_photo": p.profile_photo.url if p.profile_photo else None,
            }
            for p in qs
        ]
    })


@csrf_exempt
def admin_toggle_provider(request, provider_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        p = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    p.is_approved = not p.is_approved
    p.save()

    return JsonResponse({"status": "updated", "is_approved": p.is_approved})


# ========================================================
# SPECIALTIES CRUD
# ========================================================
@csrf_exempt
def specialty_list(request):
    items = [{"id": s.id, "name": s.name} for s in Specialty.objects.all().order_by("name")]
    return JsonResponse({"status": "ok", "items": items})


@csrf_exempt
def specialty_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data = json.loads(request.body)
    name = data.get("name", "").strip()

    if Specialty.objects.filter(name__iexact=name).exists():
        return JsonResponse({"error": "Specialty already exists"}, status=400)

    spec = Specialty.objects.create(name=name)

    return JsonResponse({"status": "created", "id": spec.id, "name": name})


@csrf_exempt
def specialty_update(request, spec_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        spec = Specialty.objects.get(id=spec_id)
    except Specialty.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    data = json.loads(request.body)
    name = data.get("name", "").strip()

    if Specialty.objects.filter(name__iexact=name).exclude(id=spec_id).exists():
        return JsonResponse({"error": "Duplicate name"}, status=400)

    spec.name = name
    spec.save()

    return JsonResponse({"status": "updated"})


@csrf_exempt
def specialty_delete(request, spec_id):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])

    try:
        Specialty.objects.get(id=spec_id).delete()
        return JsonResponse({"status": "deleted"})
    except Specialty.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)


# ========================================================
# APPOINTMENTS LIST + CREATE
# ========================================================
@csrf_exempt
def appointment_list(request):
    if request.method == "GET":
        qs = Appointment.objects.order_by("-start")

        if request.GET.get("patient"):
            qs = qs.filter(patient_id=request.GET["patient"])
        if request.GET.get("provider"):
            qs = qs.filter(provider_id=request.GET["provider"])

        return JsonResponse({
            "status": "ok",
            "items": [
                {
                    "id": a.id,
                    "patient": a.patient_id,
                    "provider": a.provider_id,
                    "patient_name": a.patient_name,
                    "provider_name": a.provider_name,
                    "service": a.service,
                    "start": a.start.isoformat(),
                    "end": a.end.isoformat(),
                    "status": a.status,
                }
                for a in qs
            ]
        })

    if request.method == "POST":
        data = json.loads(request.body)

        start_dt = parse_datetime(data.get("start"))
        end_dt = parse_datetime(data.get("end"))

        conflict = Appointment.objects.filter(
            provider_id=data["provider"],
            start__lt=end_dt,
            end__gt=start_dt
        ).exists()

        if conflict:
            return JsonResponse({"error": "Time conflict"}, status=409)

        appt = Appointment.objects.create(
            provider_id=data["provider"],
            patient_id=data["patient"],
            patient_name=data.get("patient_name", ""),
            provider_name=data.get("provider_name", ""),
            service=data.get("service", ""),
            start=start_dt,
            end=end_dt,
            status="confirmed"
        )

        return JsonResponse({"status": "created", "id": appt.id}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


# ========================================================
# APPOINTMENT DETAIL
# ========================================================
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


# ========================================================
# PROVIDER APPOINTMENT FILTERS
# ========================================================
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


def provider_today(request, provider_id):
    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    qs = Appointment.objects.filter(
        provider_id=provider_id,
        start__gte=start_of_day,
        start__lt=end_of_day
    ).order_by("start")

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


def provider_upcoming(request, provider_id):
    now = timezone.now()
    qs = Appointment.objects.filter(provider_id=provider_id, start__gte=now).order_by("start")

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


def provider_past(request, provider_id):
    now = timezone.now()
    qs = Appointment.objects.filter(provider_id=provider_id, end__lt=now).order_by("-start")

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


# ========================================================
# PATIENT APPOINTMENTS
# ========================================================
def patient_appointments(request, patient_id):
    qs = Appointment.objects.filter(patient_id=patient_id).order_by("start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })


def patient_upcoming(request, patient_id):
    now = timezone.now()
    qs = Appointment.objects.filter(patient_id=patient_id, start__gte=now).order_by("start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })


def patient_past(request, patient_id):
    now = timezone.now()
    qs = Appointment.objects.filter(patient_id=patient_id, end__lt=now).order_by("-start")

    return JsonResponse({
        "status": "ok",
        "appointments": [
            {
                "id": a.id,
                "provider": a.provider_id,
                "provider_name": a.provider_name,
                "service": a.service,
                "start": a.start.isoformat(),
                "end": a.end.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
    })


# ========================================================
# CANCEL / COMPLETE / RESCHEDULE
# ========================================================
@csrf_exempt
def cancel_appointment(request, apt_id):
    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    appt.status = "cancelled"
    appt.save()

    return JsonResponse({"status": "cancelled"})


@csrf_exempt
def complete_appointment(request, apt_id):
    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    appt.status = "completed"
    appt.save()

    return JsonResponse({"status": "completed"})


@csrf_exempt
def reschedule_appointment(request, apt_id):
    try:
        appt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    data = json.loads(request.body)

    start_dt = parse_datetime(data.get("start"))
    end_dt = parse_datetime(data.get("end"))

    conflict = Appointment.objects.filter(
        provider_id=appt.provider_id,
        start__lt=end_dt,
        end__gt=start_dt
    ).exclude(id=apt_id).exists()

    if conflict:
        return JsonResponse({"error": "Conflict"}, status=409)

    appt.start = start_dt
    appt.end = end_dt
    appt.save()

    return JsonResponse({"status": "rescheduled"})


# ========================================================
# AVAILABILITY CRUD
# ========================================================
def provider_availability(request, provider_id):
    slots = Availability.objects.filter(provider_id=provider_id).order_by("start")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": s.id,
                "provider_id": s.provider_id,
                "start": s.start.isoformat(),
                "end": s.end.isoformat(),
            }
            for s in slots
        ]
    })


def availability_list(request):
    slots = Availability.objects.select_related("provider").order_by("start")

    return JsonResponse({
        "status": "ok",
        "items": [
            {
                "id": s.id,
                "provider_id": s.provider_id,
                "provider_name": s.provider.user.get_full_name(),
                "start": s.start.isoformat(),
                "end": s.end.isoformat(),
            }
            for s in slots
        ]
    })


@csrf_exempt
def create_availability(request):
    data = json.loads(request.body)

    provider = data["provider"]
    start = parse_datetime(data["start"])
    end = parse_datetime(data["end"])

    conflict = Availability.objects.filter(
        provider_id=provider,
        start__lt=end,
        end__gt=start
    ).exists()

    if conflict:
        return JsonResponse({"error": "Conflict"}, status=409)

    Availability.objects.create(provider_id=provider, start=start, end=end)

    return JsonResponse({"status": "created"})


@csrf_exempt
def update_availability(request, avail_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        slot = Availability.objects.get(id=avail_id)
    except Availability.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    data = json.loads(request.body)
    start = parse_datetime(data["start"])
    end = parse_datetime(data["end"])

    conflict = Availability.objects.filter(
        provider_id=slot.provider_id,
        start__lt=end,
        end__gt=start
    ).exclude(id=avail_id).exists()

    if conflict:
        return JsonResponse({"error": "Conflict"}, status=409)

    slot.start = start
    slot.end = end
    slot.save()

    return JsonResponse({"status": "updated"})


@csrf_exempt
def delete_availability(request, avail_id):
    try:
        Availability.objects.get(id=avail_id).delete()
        return JsonResponse({"status": "deleted"})
    except Availability.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

def provider_analytics(request, provider_id):
    """
    Returns all analytics for the provider dashboard in one API call.
    """

    now = timezone.now()

    # Today's appointments
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    today = Appointment.objects.filter(
        provider_id=provider_id,
        start__gte=start_of_day,
        start__lt=end_of_day
    ).count()

    # Upcoming
    upcoming = Appointment.objects.filter(
        provider_id=provider_id,
        start__gte=now
    ).count()

    # Past
    past = Appointment.objects.filter(
        provider_id=provider_id,
        end__lt=now
    )

    completed = past.filter(status="completed").count()
    cancelled = past.filter(status="cancelled").count()

    # Total patients ever seen
    total_patients = Appointment.objects.filter(
        provider_id=provider_id
    ).count()

    # Availability slots
    availability_slots = Availability.objects.filter(
        provider_id=provider_id
    ).count()

    return JsonResponse({
        "status": "ok",
        "analytics": {
            "today": today,
            "upcoming": upcoming,
            "completed": completed,
            "cancelled": cancelled,
            "total_patients": total_patients,
            "availability_slots": availability_slots,
        }
    })


# ========================================================
# ADMIN DASHBOARD STATS
# ========================================================
def admin_stats(request):
    """
    Returns system-wide summary numbers for the admin dashboard.
    """

    total_providers = Provider.objects.count()
    approved_providers = Provider.objects.filter(is_approved=True).count()
    pending_providers = Provider.objects.filter(is_approved=False).count()

    provider_user_ids = Provider.objects.values_list("user_id", flat=True)
    total_patients = User.objects.exclude(id__in=provider_user_ids).exclude(is_staff=True).count()

    return JsonResponse({
        "status": "ok",
        "stats": {
            "total_providers": total_providers,
            "approved_providers": approved_providers,
            "pending_providers": pending_providers,
            "total_patients": total_patients,
        }
    })


# ========================================================
# PROVIDER UPDATE PROFILE
# ========================================================
@csrf_exempt
def provider_update(request, provider_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        provider = Provider.objects.select_related("user").get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Provider not found"}, status=404)

    data = json.loads(request.body)

    # Update user fields
    provider.user.first_name = data.get("first_name", provider.user.first_name)
    provider.user.last_name = data.get("last_name", provider.user.last_name)
    provider.user.email = data.get("email", provider.user.email)
    provider.user.save()

    # Update provider fields
    provider.location = data.get("location", provider.location)
    provider.bio = data.get("bio", provider.bio)

    # Update specialty if provided
    specialty_id = data.get("specialty_id")
    if specialty_id:
        try:
            provider.specialty = Specialty.objects.get(id=specialty_id)
        except Specialty.DoesNotExist:
            return JsonResponse({"error": "Invalid specialty"}, status=400)

    provider.save()

    return JsonResponse({"status": "updated"})
