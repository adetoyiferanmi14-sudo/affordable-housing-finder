"""
Pure eligibility logic. This file has NO Django imports and NO thresholds.

The thresholds live in the database (eligibility.models.EligibilityRule).
They are loaded by eligibility/engine.py and passed in here as a
RuleParams object, so changing a threshold never needs a code change.

Boundary convention (applies to every rule): all comparisons are INCLUSIVE.
  - minimums ("at least"): a value equal to the minimum qualifies
  - maximums ("or less"):  a value equal to the maximum qualifies

Inputs that are missing, non-numeric or impossible (negative income, age of
zero, ...) make the affected criterion FAIL. They never pass by accident.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

SHORT_NAMES = {
    'NHF': 'NHF',
    'LAGOSHOMS': 'LagosHOMS',
    'RENT_TO_OWN': 'Rent-to-Own',
}


@dataclass(frozen=True)
class RuleParams:
    """One scheme's rule, as read from the database.

    A parameter set to None means "this criterion is not applied".
    """
    scheme_code: str = ''
    scheme_label: str = ''
    official_url: str = ''
    version: Optional[int] = None
    effective_from: Optional[date] = None
    source_note: str = ''
    min_income: Optional[Decimal] = None
    max_income: Optional[Decimal] = None
    min_nhf_months: Optional[int] = None
    max_age: Optional[int] = None
    min_residency_years: Optional[int] = None
    equity_percent: Optional[Decimal] = None   # e.g. 30 means 30%
    max_dti: Optional[Decimal] = None          # ratio, e.g. 0.40 means 40%
    disallow_prior_owner: bool = False


# ---------------------------------------------------------------- helpers

def to_decimal(value, default='0'):
    """Lenient conversion, used only for display-side maths."""
    if value in (None, ''):
        value = default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('yes', 'true', '1', 'on')


def _num(values, key):
    """Strict conversion: returns a finite Decimal or None."""
    raw = values.get(key)
    if raw is None or raw == '' or isinstance(raw, bool):
        return None
    try:
        number = Decimal(str(raw).strip())
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not number.is_finite():
        return None
    return number


def _plain(number):
    """Decimal -> text without trailing zeros (30.00 -> '30')."""
    return format(Decimal(number).normalize(), 'f')


def money(value):
    return '\u20a6{:,.0f}'.format(Decimal(value))


def required_equity(params, price):
    """Equity needed for a property of this price, or None if no equity rule."""
    if params.equity_percent is None or price is None:
        return None
    return to_decimal(price) * Decimal(params.equity_percent) / Decimal('100')


# ------------------------------------------------------------ descriptions

def describe(params):
    """Human-readable criteria, generated from the SAME parameters the
    engine executes. Returns a list of (key, label)."""
    items = []
    if params.min_income is not None and params.max_income is not None:
        items.append(('income_in_range',
                      'Income from %s to %s (both ends included)'
                      % (money(params.min_income), money(params.max_income))))
    elif params.min_income is not None:
        items.append(('income_in_range',
                      'Income of %s or more' % money(params.min_income)))
    elif params.max_income is not None:
        items.append(('income_in_range',
                      'Income of %s or less' % money(params.max_income)))
    if params.min_nhf_months is not None:
        items.append(('nhf_months_sufficient',
                      'At least %s months of NHF contributions' % params.min_nhf_months))
    if params.max_age is not None:
        items.append(('age_within_limit', 'Age %s or under' % params.max_age))
    if params.min_residency_years is not None:
        items.append(('residency_sufficient',
                      'At least %s years of Lagos residency' % params.min_residency_years))
    if params.disallow_prior_owner:
        items.append(('no_prior_ownership', 'No prior homeownership'))
    if params.equity_percent is not None:
        items.append(('equity_sufficient',
                      'Equity of at least %s%% of the property price'
                      % _plain(params.equity_percent)))
    if params.max_dti is not None:
        items.append(('dti_acceptable',
                      'Debt-to-income ratio of %s%% or less'
                      % _plain(Decimal(params.max_dti) * 100)))
    return items


# --------------------------------------------------------------- evaluation

def evaluate(params, values, property_price=None):
    """Run one scheme's rule against the applicant's values.

    property_price=None means "no specific property yet": the equity
    criterion is reported as 'pending' and is neither passed nor failed.
    """
    income = _num(values, 'income')
    months = _num(values, 'nhf_months')
    age = _num(values, 'age')
    residency = _num(values, 'residency_yrs')
    dti = _num(values, 'dti_ratio')
    equity = _num(values, 'equity')
    prior_known = values.get('prior_owner') not in (None, '')
    price = None if property_price is None else to_decimal(property_price)

    results = {}   # key -> True / False / None (pending)

    if params.min_income is not None or params.max_income is not None:
        ok = income is not None and income >= 0
        if ok and params.min_income is not None:
            ok = income >= params.min_income
        if ok and params.max_income is not None:
            ok = income <= params.max_income
        results['income_in_range'] = ok

    if params.min_nhf_months is not None:
        results['nhf_months_sufficient'] = (
            months is not None and months >= 0 and months >= params.min_nhf_months)

    if params.max_age is not None:
        results['age_within_limit'] = (
            age is not None and age > 0 and age <= params.max_age)

    if params.min_residency_years is not None:
        results['residency_sufficient'] = (
            residency is not None and residency >= 0
            and residency >= params.min_residency_years)

    if params.disallow_prior_owner:
        results['no_prior_ownership'] = prior_known and not to_bool(values.get('prior_owner'))

    if params.equity_percent is not None:
        if price is None:
            results['equity_sufficient'] = None
        else:
            needed = required_equity(params, price)
            results['equity_sufficient'] = (
                equity is not None and equity >= 0 and equity >= needed)

    if params.max_dti is not None:
        results['dti_acceptable'] = (
            dti is not None and dti >= 0 and dti <= params.max_dti)

    labels = dict(describe(params))
    if 'dti_acceptable' in labels and dti is not None:
        labels['dti_acceptable'] += ' (yours: %s%%)' % (dti * 100).quantize(Decimal('0.01'))

    rows = []
    for key, outcome in results.items():
        status = 'pending' if outcome is None else ('pass' if outcome else 'fail')
        rows.append({'key': key, 'label': labels[key], 'status': status})

    has_criteria = bool(results)
    eligible = has_criteria and all(outcome is not False for outcome in results.values())
    in_principle = eligible and any(outcome is None for outcome in results.values())

    name = SHORT_NAMES.get(params.scheme_code, params.scheme_label or params.scheme_code)
    if not has_criteria:
        reason = 'No active eligibility rule is configured for %s.' % name
    elif in_principle:
        reason = ('Your details meet the %s requirements that can be checked without '
                  'a specific property. The equity requirement is checked per property '
                  'on the Housing Finder page.' % name)
    elif eligible:
        reason = 'You meet the %s requirements based on the information you provided.' % name
    else:
        reason = 'You do not meet the %s requirements for this session.' % name

    return {
        'eligible': eligible,
        'in_principle': in_principle,
        'checks': results,
        'rows': rows,
        'reason': reason,
        'scheme_code': params.scheme_code,
        'scheme_label': params.scheme_label,
        'version': params.version,
        'effective_from': params.effective_from,
        'source_note': params.source_note,
        'official_url': params.official_url,
        'required_equity': required_equity(params, price),
    }


# ------------------------------------------------------ income-band coverage

def _income_bands(params_list):
    bands = []
    for p in params_list:
        if p.min_income is None and p.max_income is None:
            continue
        low = p.min_income if p.min_income is not None else Decimal('0')
        bands.append((Decimal(low), None if p.max_income is None else Decimal(p.max_income)))
    return bands


def covers_income(params_list, income):
    income = to_decimal(income)
    for low, high in _income_bands(params_list):
        if income >= low and (high is None or income <= high):
            return True
    return False


def uncovered_income_bands(params_list):
    """Whole-naira income bands that NO scheme covers: [(low, high), ...],
    where high=None means 'no upper limit'. Computed from the stored rules,
    so it can never disagree with them."""
    bands = sorted(_income_bands(params_list), key=lambda band: band[0])
    if not bands:
        return [(Decimal('0'), None)]
    merged = []
    for low, high in bands:
        if merged:
            m_low, m_high = merged[-1]
            if m_high is None:
                continue
            if low <= m_high + 1:
                merged[-1] = (m_low, None if high is None else max(m_high, high))
                continue
        merged.append((low, high))
    gaps = []
    if merged[0][0] > 0:
        gaps.append((Decimal('0'), merged[0][0] - 1))
    for (_, a_high), (b_low, _) in zip(merged, merged[1:]):
        gaps.append((a_high + 1, b_low - 1))
    if merged[-1][1] is not None:
        gaps.append((merged[-1][1] + 1, None))
    return gaps


def gap_for_income(gaps, income):
    income = to_decimal(income)
    for low, high in gaps:
        if income >= low and (high is None or income < high + 1):
            return (low, high)
    return None


def describe_band(low, high):
    if high is None:
        return '%s and above' % money(low)
    if low <= 0:
        return 'below %s' % money(high + 1)
    return '%s to %s' % (money(low), money(high))
