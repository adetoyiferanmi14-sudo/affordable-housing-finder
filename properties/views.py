from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from eligibility import rules
from eligibility.engine import load_params
from .models import Property, Scheme


def home(request):
    """Landing page. Shows the three housing schemes."""
    schemes = Scheme.objects.filter(active=True)
    return render(request, 'home.html', {'schemes': schemes})


def _evaluate(prop, values, params):
    """Run the stored rule for this property's scheme against the property's
    own price (so equity is always checked per property)."""
    rule = params.get(prop.scheme.scheme_name)
    if rule is None:
        rule = rules.RuleParams(scheme_code=prop.scheme.scheme_name)
    return rules.evaluate(rule, values, prop.price)


def search(request):
    """Housing Finder: only properties the session qualifies for, narrowed by
    the search filters. Price, bedrooms and text filters run in the database
    (so the price/area indexes can be used); eligibility is checked per
    property afterwards."""
    values = request.session.get('eligibility')
    if not values:
        return render(request, 'properties/search.html', {'no_session': True})

    params = load_params()
    base = (Property.objects.filter(status=Property.AVAILABLE)
            .select_related('scheme').order_by('property_id'))

    qualifying_ids = {p.pk for p in base if _evaluate(p, values, params)['eligible']}
    total_qualifying = len(qualifying_ids)

    keyword = request.GET.get('keyword', '').strip()
    location = request.GET.get('location', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    bedrooms = request.GET.get('bedrooms', '').strip()

    queryset = base.filter(pk__in=qualifying_ids)
    if keyword:
        queryset = queryset.filter(
            Q(address__icontains=keyword) | Q(description__icontains=keyword)
            | Q(area__icontains=keyword))
    if location:
        queryset = queryset.filter(Q(address__icontains=location) | Q(area__icontains=location))
    if max_price:
        try:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        except (InvalidOperation, ValueError):
            pass
    if bedrooms:
        try:
            queryset = queryset.filter(bedrooms__gte=int(bedrooms))
        except ValueError:
            pass

    filtered = list(queryset)
    context = {
        'no_session': False,
        'properties': filtered,
        'shown_count': len(filtered),
        'total_qualifying': total_qualifying,
        'keyword': keyword,
        'location': location,
        'max_price': max_price,
        'bedrooms': bedrooms,
    }
    return render(request, 'properties/search.html', context)


def detail(request, pk):
    """Property Detail: the property plus this session's eligibility for it."""
    prop = get_object_or_404(Property.objects.select_related('scheme'), pk=pk)
    values = request.session.get('eligibility')
    if not values:
        return render(request, 'properties/detail.html', {'no_session': True, 'property': prop})

    params = load_params()
    result = _evaluate(prop, values, params)

    rule = params.get(prop.scheme.scheme_name)
    required = result['required_equity']
    user_equity = rules.to_decimal(values.get('equity'))

    context = {
        'no_session': False,
        'property': prop,
        'eligible': result['eligible'],
        'result': result,
        'show_equity_card': required is not None,
        'required_equity': required,
        'equity_pct': rules._plain(rule.equity_percent) if rule and rule.equity_percent is not None else '',
        'user_equity': user_equity,
        'equity_covers_price': required is not None and user_equity >= prop.price,
    }
    return render(request, 'properties/detail.html', context)


def data_protection(request):
    """Static public page explaining data handling."""
    return render(request, 'data_protection.html')
