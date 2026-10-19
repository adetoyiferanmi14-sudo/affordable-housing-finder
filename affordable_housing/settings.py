"""
Django settings for the Affordable Housing Finder and Eligibility System.

National Diploma project - Lagos State University, Ojo.
No accounts, no passwords, no admin panel.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# For a student ND project this is fine hardcoded; rotate before any
# real-world reuse.
SECRET_KEY = 'django-insecure-ahes-nd-project-lasu-ojo-change-me-in-production'

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.pythonanywhere.com']

# Application definition
# No django.contrib.admin, no django.contrib.auth, no django.contrib.contenttypes.
# Only what sessions/messages/staticfiles actually need.
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'properties',
    'eligibility',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'affordable_housing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'affordable_housing.context_processors.site_meta',
            ],
        },
    },
]

WSGI_APPLICATION = 'affordable_housing.wsgi.application'
ASGI_APPLICATION = 'affordable_housing.asgi.application'

# Database - SQLite only, no MySQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# No AUTH_PASSWORD_VALIDATORS block needed - there is no auth app.

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sessions - signed cookies means no session table is needed in the DB.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://affordablehousing.pythonanywhere.com',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
