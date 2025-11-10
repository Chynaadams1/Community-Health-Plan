# appointments/views.py
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.utils import timezone
import json

from .models import Appointment, Provider, Specialty, Availability

# ===== YOUR EXISTING CODE (KEEP THIS) =====

def _serialize(a: Appointment) -> dict:
    return {
        "id": str(a.id),
        "patient": a.patient_id,
        "provider": a.provider_id,
        "patient_name": a.patient_name,
        "provider_name": a.provider_name,
        "service": a.service,
        "start": a.start.isoformat(),
        "end": a.end.isoformat(),
        "status": a.status,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }

@csrf_exempt
def appointment_list(request):
    """
    GET  -> list recent appointments
    POST -> create with conflict detection
    """
    if request.method == "GET":
        items = [_serialize(a) for a in Appointment.objects.order_by("-start")[:50]]
        return JsonResponse({"status": "ok", "items": items})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    # POST
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    # Required fields (keep simple while UI stabilizes)
    required = ["provider", "start", "end"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return HttpResponseBadRequest(f"Missing fields: {', '.join(missing)}")

    start_dt = parse_datetime(data["start"])
    end_dt = parse_datetime(data["end"])
    if not start_dt or not end_dt:
        return HttpResponseBadRequest("start/end must be ISO datetimes (e.g. 2025-11-01T13:30:00Z)")
    if end_dt <= start_dt:
        return HttpResponseBadRequest("end must be after start")

    # Conflict detection: same provider + overlapping time
    provider_id = data["provider"]
    overlap = Appointment.objects.filter(
        provider_id=provider_id
    ).filter(
        Q(start__lt=end_dt) & Q(end__gt=start_dt)
    ).exists()

    if overlap:
        return JsonResponse(
            {"status": "error", "error": "Time slot conflicts with an existing appointment."},
            status=409,
        )

    a = Appointment.objects.create(
        provider_id=provider_id,
        patient_id=data.get("patient"),  # optional for now
        patient_name=data.get("patient_name", "").strip(),
        provider_name=data.get("provider_name", "").strip(),
        service=data.get("service", "").strip(),
        start=start_dt,
        end=end_dt,
        status=data.get("status", Appointment.Status.REQUESTED),
        notes=data.get("notes", "").strip(),
    )
    return JsonResponse({"status": "created", "item": _serialize(a)}, status=201)


# ===== ADD THESE NEW VIEWS BELOW =====

def specialty_list(request):
    """GET -> list all specialties"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    specialties = [
        {"id": s.id, "name": s.name}
        for s in Specialty.objects.all()
    ]
    return JsonResponse({"status": "ok", "items": specialties})


def provider_list(request):
    """GET -> list providers (with optional filters)"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    providers = Provider.objects.select_related('user', 'specialty')
    
    # Filter by specialty: ?specialty=1
    specialty_id = request.GET.get('specialty')
    if specialty_id:
        providers = providers.filter(specialty_id=specialty_id)
    
    # Filter by location: ?location=Baltimore
    location = request.GET.get('location')
    if location:
        providers = providers.filter(location__icontains=location)
    
    items = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "user_name": p.user.get_full_name() or p.user.username,
            "specialty_id": p.specialty_id,
            "specialty_name": p.specialty.name,
            "location": p.location,
        }
        for p in providers
    ]
    return JsonResponse({"status": "ok", "items": items})


def provider_detail(request, provider_id):
    """GET -> get single provider details"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    try:
        p = Provider.objects.select_related('user', 'specialty').get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"status": "error", "error": "Provider not found"}, status=404)
    
    data = {
        "id": p.id,
        "user_id": p.user_id,
        "user_name": p.user.get_full_name() or p.user.username,
        "specialty_id": p.specialty_id,
        "specialty_name": p.specialty.name,
        "location": p.location,
    }
    return JsonResponse({"status": "ok", "item": data})


def provider_availability(request, provider_id):
    """GET -> get provider's availability slots"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return JsonResponse({"status": "error", "error": "Provider not found"}, status=404)
    
    # Get future availability
    now = timezone.now()
    availabilities = Availability.objects.filter(
        provider=provider,
        start__gte=now
    ).order_by('start')
    
    items = [
        {
            "id": av.id,
            "provider_id": av.provider_id,
            "provider_name": str(av.provider),
            "start": av.start.isoformat(),
            "end": av.end.isoformat(),
        }
        for av in availabilities
    ]
    return JsonResponse({"status": "ok", "items": items})


def availability_list(request):
    """GET -> list all availability slots (with optional filters)"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    availabilities = Availability.objects.select_related('provider').filter(
        start__gte=timezone.now()
    )
    
    # Filter by provider: ?provider=1
    provider_id = request.GET.get('provider')
    if provider_id:
        availabilities = availabilities.filter(provider_id=provider_id)
    
    items = [
        {
            "id": av.id,
            "provider_id": av.provider_id,
            "provider_name": str(av.provider),
            "start": av.start.isoformat(),
            "end": av.end.isoformat(),
        }
        for av in availabilities.order_by('start')
    ]
    return JsonResponse({"status": "ok", "items": items})