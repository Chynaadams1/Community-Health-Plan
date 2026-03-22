# Community Health Plan

A full-stack healthcare appointment management platform built with Django. Patients can book appointments with healthcare providers, providers can manage their schedules and patient history, and admins can oversee the entire platform.

---

## Features

### Patients
- Register and log in securely
- Browse providers by specialty and location
- Book, cancel, and reschedule appointments
- View upcoming and past appointment history

### Providers
- Manage profile, bio, and profile photo
- Set availability schedules
- View today's, upcoming, and past appointments
- Track appointment analytics

### Admin
- View and manage all providers and patients
- Toggle provider active status
- Access platform-wide statistics (total providers, patients, appointments)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| REST API | Django REST Framework |
| Database | PostgreSQL (via psycopg) |
| Auth | Django built-in authentication |
| CORS | django-cors-headers |
| Deployment | Render (with Gunicorn + WhiteNoise) |
| Config | python-dotenv |

---

## Project Structure

```
Community-Health-Plan/
├── appointments/
│   ├── models.py        # Specialty, Provider, Availability, Appointment, ChatHistory, DoctorNote
│   ├── views.py         # All API endpoints
│   ├── urls.py          # URL routing
│   ├── serializers.py   # DRF serializers
│   ├── admin.py         # Django admin config
│   └── migrations/      # Database migrations
├── config/
│   ├── settings.py      # App settings (env-based)
│   ├── urls.py          # Root URL config
│   ├── wsgi.py          # WSGI entry point
│   └── asgi.py          # ASGI entry point
├── templates/
│   └── home.html        # Base HTML template
├── manage.py
├── requirements.txt
├── Procfile             # Render/Heroku deploy config
└── .env.example         # Environment variable template
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | Log in and get user role |

### Providers
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/providers/` | List all providers |
| GET | `/api/providers/<id>/` | Provider detail |
| PUT | `/api/providers/<id>/update/` | Update provider profile |
| POST | `/api/providers/<id>/photo/` | Upload profile photo |
| GET | `/api/providers/<id>/appointments/` | All provider appointments |
| GET | `/api/providers/<id>/today/` | Today's appointments |
| GET | `/api/providers/<id>/upcoming/` | Upcoming appointments |
| GET | `/api/providers/<id>/past/` | Past appointments |
| GET | `/api/providers/<id>/analytics/` | Appointment stats |
| GET | `/api/providers/<id>/availability/` | Provider availability |

### Patients
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/patients/<id>/appointments/` | All patient appointments |
| GET | `/api/patients/<id>/upcoming/` | Upcoming appointments |
| GET | `/api/patients/<id>/past/` | Past appointments |

### Appointments
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/appointments/` | List all appointments |
| GET | `/api/appointments/<id>/` | Appointment detail |
| POST | `/api/appointments/<id>/cancel/` | Cancel appointment |
| POST | `/api/appointments/<id>/complete/` | Mark as completed |
| POST | `/api/appointments/<id>/reschedule/` | Reschedule appointment |

### Specialties
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/specialties/` | List all specialties |
| POST | `/api/specialties/create/` | Create specialty |
| PUT | `/api/specialties/<id>/update/` | Update specialty |
| DELETE | `/api/specialties/<id>/delete/` | Delete specialty |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/providers/` | List all providers |
| POST | `/api/admin/providers/<id>/toggle/` | Toggle provider active status |
| GET | `/api/admin/stats/` | Platform statistics |

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/Chynaadams1/Community-Health-Plan.git
cd Community-Health-Plan
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/community_health
FRONTEND_URL=http://localhost:5173
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

API is now running at **http://localhost:8000**

---

## Deployment (Render)

This project is configured for deployment on [Render](https://render.com).

The `Procfile` runs:
```
web: gunicorn config.wsgi:application
```

Set these environment variables in your Render dashboard:
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `FRONTEND_URL`

---

## Data Models

- **Specialty** — Medical specialties (e.g. Cardiology, Pediatrics)
- **Provider** — Healthcare provider profiles linked to users
- **Availability** — Provider schedule windows
- **Appointment** — Bookings between patients and providers (statuses: requested, confirmed, cancelled, completed)
- **ChatHistory** — AI chat session logs
- **DoctorNote** — Notes attached to appointments by providers

---

## Author

**Chyna Adams** — [github.com/Chynaadams1](https://github.com/Chynaadams1)
