"""
WSGI config for the Affordable Housing Finder and Eligibility System.

Exposes the WSGI callable as a module-level variable named ``application``.
This is the file PythonAnywhere's Web tab points at (with the path adjusted
to match your PythonAnywhere username/project folder).
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'affordable_housing.settings')

application = get_wsgi_application()
