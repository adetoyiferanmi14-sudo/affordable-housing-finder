from django.db import models

from properties.models import Scheme


class EligibilityRule(models.Model):
    """Documentation-only record of a scheme's rule. The actual logic that
    is executed lives in eligibility/rules.py as plain Python functions -
    nothing here is ever parsed or evaluated."""

    rule_id = models.AutoField(primary_key=True)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='rules')
    rule_condition = models.CharField(max_length=255)
    priority = models.IntegerField(default=1)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f'{self.scheme.scheme_name}: {self.rule_condition}'
