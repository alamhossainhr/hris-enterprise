import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-default-key-for-dev")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # Core Enterprise Modules
    "core",
    "accounts",
    "audit",
    "organization",
    "period_lock",
    "approvals",
    # Operational Modules
    "employees",
    "shifts",
    "attendance",
    "leave",
    "payroll",
    "loans",
    "benefits",
    "increments",
    "promotions",
    "separation",
    "settlement",
    "documents",
    "notifications",
    "ess",
    "reports",
    "dashboard",
    "integrations",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.audit_middleware.AuditLogMiddleware",
    "period_lock.middleware.period_lock_middleware.PeriodLockMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# MSSQL Database Configuration
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": os.getenv("DB_NAME", "ALAMHRMDB"),
        "USER": os.getenv("DB_USER", "sa"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "1433"),
        "OPTIONS": {
            "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            "extra_params": f"TrustServerCertificate={os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes')}",
        },
    }
}

AUTH_USER_MODEL = "accounts.UserAccount"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = False  # Set to False to match MSSQL DateTime expectations without UTC conversion mismatch

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}