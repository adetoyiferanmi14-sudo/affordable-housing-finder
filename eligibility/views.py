from decimal import Decimal, InvalidOperation

from django.shortcuts import render

from . import rules
from .engine import load_params, run_all_checks
from .forms import EligibilityForm

CARD_ORDER = ['NHF', 'LAGOSHOMS', 'RENT_TO_OWN']


def _initial_from_session(saved):
    """Pre-fill the form from this visit's session. The repayments figure is
    not kept, so it is reconstructed from the stored ratio and income."""
    if not saved:
        return None
    initial = {key: saved[key] for key in
               ('age', 'income', 'nhf_months', 'residency_yrs', 'prior_owner', 'equity')
               if saved.get(key) not in (None, '')}
    try:
        initial['monthly_repayments'] = (
            Decimal(saved['dti_ratio']) * Decimal(saved['income'])).quantize(Decimal('0.01'))
    except (InvalidOperation, KeyError, TypeError):
        pass
    return initial


def _results_context(values):
    params = load_params()
    results = run_all_checks(values, params_by_scheme=params)
    cards = [{'code': code, 'result': results[code]} for code in CARD_ORDER if code in results]

    param_list = list(params.values())
    income = rules.to_decimal(values.get('income'))
    income_uncovered = not rules.covers_income(param_list, income)
    gap = rules.gap_for_income(rules.uncovered_income_bands(param_list), income)
    all_gaps = [rules.describe_band(low, high)
                for low, high in rules.uncovered_income_bands(param_list)]

    return {
        'cards': cards,
        'income_uncovered': income_uncovered,
        'gap_text': rules.describe_band(*gap) if gap else '',
        'all_gap_text': '; '.join(all_gaps),
        'none_eligible': not any(r['eligible'] for r in results.values()),
    }


def check(request):
    """
    GET: show the form, pre-filled from this visit's session if there is one.
    POST: validate with EligibilityForm. Invalid input is rejected with field
    errors: nothing is stored and no rule is run. Valid input is turned into a
    debt-to-income ratio, kept in the session, and the stored rules are run.
    """
    saved = request.session.get('eligibility')
    context = {'cards': None, 'income_uncovered': False, 'none_eligible': False}

    if request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            dti_ratio = data['monthly_repayments'] / data['income']   # income >= 1
            values = {
                'age': str(data['age']),
                'income': str(data['income']),
                'nhf_months': str(data['nhf_months']),
                'residency_yrs': str(data['residency_yrs']),
                'dti_ratio': str(dti_ratio),
                'prior_owner': data['prior_owner'],
                'equity': str(data['equity']),
            }
            request.session['eligibility'] = values
            request.session.modified = True
            context.update(_results_context(values))
    else:
        form = EligibilityForm(initial=_initial_from_session(saved))

    context['form'] = form
    return render(request, 'eligibility/check.html', context)
