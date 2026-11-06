from django.contrib import admin

from .models import Property, Scheme


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('scheme_name', 'active', 'official_url')
    list_editable = ('active',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('address', 'area', 'price', 'scheme', 'status')
    list_filter = ('scheme', 'status', 'area')
    search_fields = ('address', 'area')
