from decimal import Decimal

from django.shortcuts import render

from .forms import EligibilityForm
from .rules import run_all_checks


def _dti_percent(dti_ratio_str):
    """Converts a stored decimal-fraction DTI ratio (e.g. '0.3050') into a
    display percentage string (e.g. '30.50'), or None if it can't be read."""
    try:
        return (Decimal(dti_ratio_str) * 100).quantize(Decimal('0.01'))
    except Exception:
        return None


def check(request):
    """
    GET: show the eligibility form, pre-filled from a previous session
    visit if one exists.
    POST: validate the eight fields with EligibilityForm, compute the
    debt-to-income ratio from monthly loan repayments / income, store the
    result in the session, run the three rules, and render the results
    below the form. Invalid submissions re-render the form with field
    errors and do not touch the session or run any rules.
    """
    results = None
    dti_percent = None

    saved = request.session.get('eligibility')

    if request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            income = data['income']
            monthly_repayments = data['monthly_repayments']
            dti_ratio = (monthly_repayments / income) if income > 0 else Decimal('1')

            values = {
                'age': str(data['age']),
                'location': data['location'],
                'income': str(income),
                'nhf_months': str(data['nhf_months']),
                'residency_yrs': str(data['residency_yrs']),
                'monthly_repayments': str(monthly_repayments),
                'dti_ratio': str(dti_ratio),
                'prior_owner': data['prior_owner'],
                'equity': str(data['equity']),
            }
            request.session['eligibility'] = values
            request.session.modified = True
            results = run_all_checks(values)
            dti_percent = _dti_percent(values['dti_ratio'])
            saved = values
    else:
        initial = saved if saved else None
        form = EligibilityForm(initial=initial)
        if saved:
            dti_percent = _dti_percent(saved.get('dti_ratio'))

    context = {
        'form': form,
        'values': saved or {},
        'results': results,
        'dti_percent': dti_percent,
    }
    return render(request, 'eligibility/check.html', context)