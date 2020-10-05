"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

TESTING = sys.argv[1:2] == ["test"] or "pytest" in sys.argv[0]

# Workaround to enable logging errors via gunicorn in docker
import logging

logging.basicConfig(
    level=logging.INFO, format=" %(levelname)s %(name)s: %(message)s",
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "r8qg2gwniy(ay(#^v3^!+vda75us0)e4iac(9-01qjls3gv^!="
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "") != "False"

# In docker use VIRTUAL_HOST environment variable, else use local address
CORE_DOMAIN = os.environ.get("CORE_DOMAIN", "localhost:8000")
ALLOWED_HOSTS = [CORE_DOMAIN]
# Allow internal communication between docker services
ALLOWED_HOSTS.append("core")

# Application definition

INSTALLED_APPS = [
    #
    # Django Apps
    #
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_registration",
    #
    # Third-Party Apps
    #
    "corsheaders",
    "oauth2_provider",
    "rest_framework",
    "rest_framework.authtoken",
    "semanticuiforms",
    "address",
    "macaddress",
    "django_celery_results",
    "graphene_django",
    #
    # Local Apps
    #
    "accounts.apps.AccountsConfig",
    "farms.apps.FarmsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyD--your-google-maps-key-SjQBE")

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
    }
}

if TESTING:
    # Override user and password
    DATABASES["default"]["USER"] = "postgres"
    DATABASES["default"]["PASSWORD"] = os.environ.get("POSTGRES_PASSWORD")
    # Override password hasher
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Celery and RabbitMQ
if DEBUG:
    CELERY_BROKER_URL = "amqp://localhost"
else:
    CELERY_BROKER_URL = (
        "amqp://"
        + os.environ.get("RABBITMQ_DEFAULT_USER")
        + ":"
        + os.environ.get("RABBITMQ_DEFAULT_PASS")
        + "@"
        + os.environ.get("RABBITMQ_HOSTNAME")
    )

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "CET"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = "/static/"

# Authentication
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = (
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",
)

ACCOUNT_ACTIVATION_DAYS = 7

# Authentication related settings
OAUTH2_PROVIDER = {
    # this is the list of available scopes
    "SCOPES": {"userinfo-v1": "Userinfo API v1"}
}

CONTROLLER_TOKEN_BYTES = 20  # Length in bytes

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

LOGIN_REDIRECT_URL = "/"

# Email

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = "notification@" + os.environ.get("VIRTUAL_HOST", "localhost")

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Graphene-Django
# https://docs.graphene-python.org/projects/django/en/latest/

GRAPHENE = {"SCHEMA": "core.schema.schema"}

# REDIS & Channels

ASGI_APPLICATION = "core.routing.application"

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL],},
    },
}

# CORS (Cross-Origin Resource Sharing)

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",  # Angular dev server
]

# Content Security Policy

if DEBUG:
    CORE_CSP_HOST = f"{CORE_DOMAIN}:{os.environ.get('CORE_DEV_SERVER_PORT')}"
else:
    CORE_CSP_HOST = CORE_DOMAIN

CSP_DEFAULT_SRC = [CORE_CSP_HOST] + ["'self'"]
CSP_STYLE_SRC = [CORE_CSP_HOST] + [
    "'unsafe-inline'",
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
    "http://netdna.bootstrapcdn.com",
]
CSP_FONT_SRC = [CORE_CSP_HOST] + [
    "data:",
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
]
CSP_SCRIPT_SRC = [CORE_CSP_HOST] + [
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://code.jquery.com/",
    "https://cdn.jsdelivr.net",
]
if DEBUG:
    CSP_FRAME_ANCESTORS = ["'self'", "http://localhost:4200", "http://127.0.0.1:4200"]
else:
    CSP_FRAME_ANCESTORS = ["'self'"]
