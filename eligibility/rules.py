"""
The three eligibility rules for the Affordable Housing Finder.

These thresholds were developed for this project. They are not official
FMBN, LagosHOMS, or Rent-to-Own criteria - the scheme names are used to
represent the general category of housing programme being modelled, but
every numeric threshold below was chosen by the project team for
demonstration and academic purposes.

Plain Python conditionals only. No eval(). No dynamic parsing.
Each check_* function returns a dict with:
    eligible: bool
    checks: dict[str, bool]   (one entry per criterion)
    reason: str
"""
from decimal import Decimal, InvalidOperation

# NHF income band: N100,000 - N300,000
# Rule developed for this project. Not an official FMBN rule.
INCOME_MIN = Decimal('100000')
INCOME_MAX = Decimal('300000')

# LagosHOMS income: N343,000 per month (no upper limit)
# Rule developed for this project. Not an official LagosHOMS rule.
LAGOSHOMS_MIN_INCOME = Decimal('343000')


def _to_decimal(value, default='0'):
    """Safely coerce a form/session value to Decimal."""
    if value in (None, ''):
        value = default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def _to_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _to_bool(value):
    """Interprets 'Yes'/'True'/True/'1' as True, everything else as False."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('yes', 'true', '1', 'on')


def check_nhf(income, nhf_months, age):
    """
    NHF eligibility (rules developed for this project, not official FMBN rules):
        income between 100,000 and 300,000
        AND nhf_months >= 6
        AND age <= 60
    """
    income = _to_decimal(income)
    nhf_months = _to_int(nhf_months)
    age = _to_int(age)

    checks = {
        # NHF income band: N100,000 - N300,000
        # Rule developed for this project.
        'income_in_range': INCOME_MIN <= income <= INCOME_MAX,
        # NHF minimum contributions: 6 months
        # Rule developed for this project.
        'nhf_months_sufficient': nhf_months >= 6,
        # NHF age limit: 60 years
        # Rule developed for this project.
        'age_within_limit': age <= 60,
    }
    eligible = all(checks.values())

    if eligible:
        reason = 'You meet the NHF requirements based on the information you provided.'
    else:
        reason = 'You do not meet the NHF requirements for this session.'

    return {'eligible': eligible, 'checks': checks, 'reason': reason}


def check_lagoshoms(income, equity, dti_ratio, property_price):
    """
    LagosHOMS eligibility (rules developed for this project, not official
    LagosHOMS rules):
        income >= 343,000 (no upper limit)
        AND equity >= property_price * 0.30
        AND dti_ratio <= 0.40

    dti_ratio is a decimal fraction (e.g. 0.30 for 30%), computed upstream
    from the applicant's monthly loan repayments divided by their monthly
    income - see eligibility/views.py.
    """
    income = _to_decimal(income)
    equity = _to_decimal(equity)
    dti_ratio = _to_decimal(dti_ratio)
    property_price = _to_decimal(property_price)

    required_equity = property_price * Decimal('0.30')

    checks = {
        # LagosHOMS income: N343,000 per month
        # Rule developed for this project.
        'income_in_range': income >= LAGOSHOMS_MIN_INCOME,
        # LagosHOMS equity: 30% of property price
        # Rule developed for this project.
        'equity_sufficient': equity >= required_equity,
        # LagosHOMS DTI: 0.40 or below
        # Rule developed for this project.
        'dti_acceptable': dti_ratio <= Decimal('0.40'),
    }
    eligible = all(checks.values())

    if eligible:
        reason = 'You meet the LagosHOMS requirements based on the information you provided.'
    else:
        reason = 'You do not meet the LagosHOMS requirements for this session.'

    return {'eligible': eligible, 'checks': checks, 'reason': reason}


def check_rent_to_own(income, residency_yrs, prior_owner):
    """
    Rent-to-Own eligibility (rules developed for this project, not
    official Rent-to-Own rules):
        income between 100,000 and 300,000
        AND residency_yrs >= 2
        AND prior_owner is False
    """
    income = _to_decimal(income)
    residency_yrs = _to_int(residency_yrs)
    prior_owner = _to_bool(prior_owner)

    checks = {
        # Rent-to-Own income: N100,000 - N300,000
        # Rule developed for this project.
        'income_in_range': INCOME_MIN <= income <= INCOME_MAX,
        # Rent-to-Own residency: 2 years minimum
        # Rule developed for this project.
        'residency_sufficient': residency_yrs >= 2,
        # Rent-to-Own: no prior homeownership
        # Rule developed for this project.
        'no_prior_ownership': prior_owner is False,
    }
    eligible = all(checks.values())

    if eligible:
        reason = 'You meet the Rent-to-Own requirements based on the information you provided.'
    else:
        reason = 'You do not meet the Rent-to-Own requirements for this session.'

    return {'eligible': eligible, 'checks': checks, 'reason': reason}


def run_all_checks(values, property_price=None):
    """
    Runs all three rules against a dict of session/form values.

    values keys expected: age, location, income, nhf_months,
    residency_yrs, dti_ratio, prior_owner, equity

    (dti_ratio here is the computed decimal fraction, not the raw monthly
    repayments figure the applicant typed in - see eligibility/views.py
    for where monthly_repayments / income is turned into dti_ratio.)

    If property_price is given, LagosHOMS is checked against that specific
    property's price (equity must be >= 30% of THAT price). Otherwise it
    falls back to the general equity_available value with a price of 0,
    which only passes if the person entered no equity requirement context -
    callers checking a specific LagosHOMS property should always pass
    property_price.

    Returns a dict keyed by scheme code: NHF, LAGOSHOMS, RENT_TO_OWN.
    """
    income = values.get('income')
    age = values.get('age')
    nhf_months = values.get('nhf_months')
    residency_yrs = values.get('residency_yrs')
    dti_ratio = values.get('dti_ratio')
    prior_owner = values.get('prior_owner')
    equity = values.get('equity')

    if property_price is None:
        property_price = 0

    return {
        'NHF': check_nhf(income, nhf_months, age),
        'LAGOSHOMS': check_lagoshoms(income, equity, dti_ratio, property_price),
        'RENT_TO_OWN': check_rent_to_own(income, residency_yrs, prior_owner),
    }