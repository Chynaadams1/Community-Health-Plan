# config/settings.py
from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url

# -------------------------------------------------------------------
# Base & environment
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local dev; on Render, real env vars are already present
load_dotenv(BASE_DIR / ".env")

def env_bool(name: str, default: bool = False) -> bool:
    return str(os.getenv(name, str(default))).strip().lower() in ("1", "true", "t", "yes", "y")

# -------------------------------------------------------------------
# Core settings from env
# -------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DEBUG", False)

# Build ALLOWED_HOSTS from env, then add Render host if present
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# Safe defaults if nothing set
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]

# CSRF trusted origins (env + Render host)
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Timezone
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_TZ = True
LANGUAGE_CODE = "en-us"
USE_I18N = True

# -------------------------------------------------------------------
# Database (Supabase via Render pooler)
# -------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", ""),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Behind Render/Cloudflare proxies
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------------------------------------------------
# Static files (Whitenoise)
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Optional but recommended for hashed static files in prod:
# STORAGES = {
#     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
#     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
# }

# Harden cookies in production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# -------------------------------------------------------------------
# Django defaults below (unchanged except duplicates removed)
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "appointments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
