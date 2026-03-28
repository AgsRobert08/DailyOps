from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-f+tw3^m)-sco4hvgq*p$bk+=2-%kvsudtc2#s*0+9vrx9kqxa#'

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost','18.188.10.113','ark-kos.com', 'www.ark-kos.com', 'miepi.ark-kos.com', '.ngrok-free.dev',]

CSRF_TRUSTED_ORIGINS = [
    'https://ark-kos.com',
    'https://www.ark-kos.com',
    'https://miepi.ark-kos.com',
    'https://emelia-protomorphic-fermin.ngrok-free.dev',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'company',
    'cursos',
    'whatsapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config_ops.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'company.context_processors.company_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config_ops.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':     os.environ.get('DB_NAME',     'dailyops_db'),
        'USER':     os.environ.get('DB_USER',     'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST',     'localhost'),
        'PORT':     os.environ.get('DB_PORT',     '3306'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE     = 'America/Mexico_City'
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL    = 'company.User'
LOGIN_REDIRECT_URL = 'company:dashboard'
LOGIN_URL          = 'company:login'

# ── EMAIL ─────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER',     'serviceswebsoportepy@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'kqkb wmui rioj lhny')
DEFAULT_FROM_EMAIL  = os.environ.get('EMAIL_HOST_USER',     'serviceswebsoportepy@gmail.com')

# ── WHATSAPP ──────────────────────────────────────────────
WHATSAPP_PROVIDER  = 'twilio'
WHATSAPP_FROM      = 'whatsapp:+14155238886'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'ACb1633b2279b97b12776b176e7b5326c6')
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN',  '9eaa8dd31bf45f16700665cc59916405')



# ── YCLOUD ────────────────────────────────────────────────
YCLOUD_API_KEY         = "26075487c078de553f0e548cdeb262da"       # yCloud Console → Developers → API Keys
YCLOUD_WHATSAPP_NUMBER = "+527717884363"          # Tu número de yCloud (el que recibe mensajes)
# ── LOCAL OVERRIDES (no se sube a GitHub) ────────────────

# Credenciales de Google para Calendar API

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = "http://localhost:8000/calendar/oauth/callback/"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True
# Necesario para OAuth en desarrollo local (http)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


try:
    from .settings_local import *
except ImportError:
    pass