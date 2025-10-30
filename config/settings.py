# config/settings.py
from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url

# -------------------------------------------------------------------
# Base & environment
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # local dev; Render uses real env vars

def env_bool(name: str, default: bool = False) -> bool:
    return str(os.getenv(name, str(default))).strip().lower() in ("1", "true", "t", "yes", "y")

# -------------------------------------------------------------------
# Core settings from env
# -------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DEBUG", False)

# Hosts & CSRF
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Safe defaults if nothing set
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]

# URLs for CORS/CSRF
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL  = os.getenv("BACKEND_URL", "https://community-health-plan.onrender.com")

# CORS
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True  # if you use cookie/session auth

# CSRF (add env list if provided)
CSRF_TRUSTED_ORIGINS = [
    BACKEND_URL,
    f"https://{RENDER_EXTERNAL_HOSTNAME}" if RENDER_EXTERNAL_HOSTNAME else BACKEND_URL,
    "https://community-health-plan.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Cross-site cookies if you’re using cookies from the frontend
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE    = "None"
SESSION_COOKIE_SECURE   = True
CSRF_COOKIE_SECURE      = True

# -------------------------------------------------------------------
# Installed apps & middleware
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # third-party first so we can see them clearly
    "corsheaders",
    "rest_framework",

    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # your apps
    "appointments",
]

# CORS middleware MUST be high, before CommonMiddleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -------------------------------------------------------------------
# Database (Supabase via pooler)
# -------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", ""),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Render/Cloudflare proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------------------------------------------------
# Passwords / i18n
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files (Whitenoise)
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# If you want hashed filenames in prod, uncomment:
# STORAGES = {
#     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
#     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
# }

# Harden cookies in production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
