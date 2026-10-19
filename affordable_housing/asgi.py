"""
ASGI config for the Affordable Housing Finder and Eligibility System.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'affordable_housing.settings')

application = get_asgi_application()
