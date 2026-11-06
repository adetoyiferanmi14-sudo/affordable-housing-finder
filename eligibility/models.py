import datetime

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.utils import timezone

from properties.models import Scheme

from . import rules


class EligibilityRule(models.Model):
    """The ACTIVE source of a scheme's eligibility thresholds.

    The engine (eligibility/engine.py) reads these rows and executes them.
    Nothing here is documentation-only: change a value in Django Admin and
    the live eligibility results change with it.

    Versioning: to change a threshold, add a NEW rule for the scheme with a
    later effective_from date. The engine uses, for each scheme, the active
    rule with the latest effective_from that is not in the future. Older
    versions are kept as history.

    Boundaries: every comparison is inclusive (a value exactly equal to a
    minimum or maximum qualifies). A blank parameter means the criterion is
    not applied.
    """

    rule_id = models.AutoField(primary_key=True)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='rules')
    version = models.PositiveIntegerField(default=1)
    effective_from = models.DateField(
        default=datetime.date.today,
        help_text='The rule applies from this date. A future date schedules it.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    min_income = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Minimum monthly income in naira. Inclusive.')
    max_income = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Maximum monthly income in naira. Inclusive. Leave blank for no upper limit.')
    min_nhf_months = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Minimum months of NHF contributions. Inclusive.')
    max_age = models.PositiveIntegerField(
        null=True, blank=True, help_text='Maximum age in years. Inclusive.')
    min_residency_years = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Minimum years of Lagos residency. Inclusive.')
    equity_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Equity required as a percentage of the property price, e.g. 30. '
                  'Inclusive. Checked per property.')
    max_dti = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text='Maximum debt-to-income ratio as a decimal, e.g. 0.40 for 40%. Inclusive.')
    disallow_prior_owner = models.BooleanField(
        default=False, help_text='Tick to exclude applicants who already own a home.')

    source_note = models.TextField(
        blank=True,
        help_text='Where these thresholds come from: a cited official source, or a '
                  'project-defined assumption. Shown to users on the results page.')

    class Meta:
        unique_together = [('scheme', 'version')]
        ordering = ['scheme', '-version']

    def __str__(self):
        return '%s v%s (from %s)' % (self.scheme, self.version, self.effective_from)

    def to_params(self):
        scheme = self.scheme if self.scheme_id else None
        return rules.RuleParams(
            scheme_code=scheme.scheme_name if scheme else '',
            scheme_label=scheme.get_scheme_name_display() if scheme else '',
            official_url=scheme.official_url if scheme else '',
            version=self.version,
            effective_from=self.effective_from,
            source_note=self.source_note,
            min_income=self.min_income,
            max_income=self.max_income,
            min_nhf_months=self.min_nhf_months,
            max_age=self.max_age,
            min_residency_years=self.min_residency_years,
            equity_percent=self.equity_percent,
            max_dti=self.max_dti,
            disallow_prior_owner=self.disallow_prior_owner,
        )

    @property
    def summary(self):
        """Documentation generated from the executed parameters."""
        labels = [label for _, label in rules.describe(self.to_params())]
        return '; '.join(labels) if labels else 'No criteria set'

    def clean(self):
        errors = {}
        if (self.min_income is not None and self.max_income is not None
                and self.min_income > self.max_income):
            errors['max_income'] = 'Maximum income must not be below the minimum income.'
        if self.equity_percent is not None and not (0 <= self.equity_percent <= 100):
            errors['equity_percent'] = 'Equity percentage must be between 0 and 100.'
        if self.max_dti is not None and self.max_dti < 0:
            errors['max_dti'] = 'The debt-to-income ratio cannot be negative.'
        if not errors and not rules.describe(self.to_params()):
            errors[NON_FIELD_ERRORS] = 'Set at least one criterion for this rule.'
        if errors:
            raise ValidationError(errors)
