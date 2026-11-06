"""Loads the active eligibility rules from the database and runs them."""
from django.utils import timezone

from properties.models import Scheme

from . import rules


def load_params(on_date=None):
    """Return {scheme_code: RuleParams} using, for each active scheme, the
    active rule with the latest effective_from that is not in the future.

    A scheme with no usable rule gets an empty RuleParams, which the
    engine treats as 'not eligible: no active rule configured'.
    """
    on_date = on_date or timezone.localdate()
    params = {}
    schemes = Scheme.objects.filter(active=True).order_by('scheme_id').prefetch_related('rules')
    for scheme in schemes:
        candidates = [r for r in scheme.rules.all()
                      if r.is_active and r.effective_from <= on_date]
        if candidates:
            rule = max(candidates, key=lambda r: (r.effective_from, r.version))
            params[scheme.scheme_name] = rule.to_params()
        else:
            params[scheme.scheme_name] = rules.RuleParams(
                scheme_code=scheme.scheme_name,
                scheme_label=scheme.get_scheme_name_display(),
                official_url=scheme.official_url,
            )
    return params


def run_all_checks(values, property_price=None, params_by_scheme=None):
    """Evaluate every scheme. Returns {scheme_code: result dict}."""
    if params_by_scheme is None:
        params_by_scheme = load_params()
    return {code: rules.evaluate(p, values, property_price)
            for code, p in params_by_scheme.items()}
