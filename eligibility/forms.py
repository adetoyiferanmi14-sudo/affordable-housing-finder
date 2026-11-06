from decimal import Decimal

from django import forms


class EligibilityForm(forms.Form):
    """Server-side validation of every public input.

    Only the inputs the rules actually need are collected: no name, email,
    phone number or location.
    """
    age = forms.IntegerField(min_value=18, max_value=100)
    income = forms.DecimalField(min_value=Decimal('1'), max_digits=12, decimal_places=2)
    nhf_months = forms.IntegerField(min_value=0, max_value=600)
    residency_yrs = forms.IntegerField(min_value=0, max_value=100)
    monthly_repayments = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2)
    prior_owner = forms.ChoiceField(choices=[('no', 'No'), ('yes', 'Yes')])
    equity = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2)
