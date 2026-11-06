from django.contrib import admin

from .models import EligibilityRule


@admin.register(EligibilityRule)
class EligibilityRuleAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'version', 'effective_from', 'is_active', 'summary')
    list_filter = ('scheme', 'is_active')
    ordering = ('scheme', '-version')
    readonly_fields = ('version', 'created_at', 'summary')
    fieldsets = (
        ('Rule identity', {
            'fields': ('scheme', 'version', 'effective_from', 'is_active', 'created_at'),
            'description': (
                'To change a threshold, ADD a new rule for the scheme with a later '
                'effective date. The earlier version is kept as history. Editing an '
                'existing row rewrites history, so only do that to fix a mistake. '
                'The Version number is assigned automatically.'),
        }),
        ('Income (both ends inclusive)', {'fields': ('min_income', 'max_income')}),
        ('Other criteria (blank = not applied)', {
            'fields': ('min_nhf_months', 'max_age', 'min_residency_years',
                       'disallow_prior_owner', 'equity_percent', 'max_dti'),
        }),
        ('Documentation', {
            'fields': ('source_note', 'summary'),
            'description': 'The summary below is generated from the values above, '
                           'so it always matches what the engine executes.',
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            last = (EligibilityRule.objects.filter(scheme=obj.scheme)
                    .order_by('-version').first())
            obj.version = last.version + 1 if last else 1
        super().save_model(request, obj, form, change)
