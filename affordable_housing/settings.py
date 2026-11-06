"""
Django settings for the Affordable Housing Finder and Eligibility System.

National Diploma project - Lagos State University, Ojo.

Production-safe by default: DEBUG is OFF unless you opt in locally with the
environment variable DJANGO_DEBUG=1 (e.g.  DJANGO_DEBUG=1 python manage.py runserver).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set DJANGO_SECRET_KEY in the PythonAnywhere WSGI file to override this
# placeholder. The placeholder is only acceptable for an academic demo.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-ahes-nd-project-lasu-ojo-change-me-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.pythonanywhere.com']

INSTALLED_APPS = [
    'django.contrib.admin',          # used ONLY to manage rules, schemes and properties
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'properties',
    'eligibility',
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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'affordable_housing.context_processors.site_meta',
            ],
        },
    },
]

WSGI_APPLICATION = 'affordable_housing.wsgi.application'
ASGI_APPLICATION = 'affordable_housing.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Uploaded property images
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- Sessions: stored on the SERVER (database), not in a readable cookie.
# The browser only holds a random session id. Expired rows are removed by
# `python manage.py clearsessions` (schedule it daily).
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG     # HTTPS-only cookie in production
SESSION_COOKIE_HTTPONLY = True        # not readable by JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://affordablehousing.pythonanywhere.com',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
