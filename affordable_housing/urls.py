"""
URL configuration. Five public pages plus the Django Admin used by the
project owner to manage rules, schemes and properties.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from properties import views as properties_views

admin.site.site_header = 'Affordable Housing Finder - administration'
admin.site.site_title = 'AHES admin'
admin.site.index_title = 'Rules, schemes and properties'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('properties.urls')),
    path('eligibility/', include('eligibility.urls')),
    path('data-protection/', properties_views.data_protection, name='data_protection'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
