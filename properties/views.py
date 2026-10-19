from decimal import Decimal, InvalidOperation

from django.shortcuts import render, get_object_or_404

from eligibility.rules import run_all_checks
from .models import Scheme, Property


def home(request):
    """Landing page. Shows the three housing schemes."""
    schemes = Scheme.objects.filter(active=True)
    return render(request, 'home.html', {'schemes': schemes})


def _qualifies(prop, values):
    """Runs the correct scheme rule for a single property and returns
    (qualifies: bool, result: dict)."""
    if prop.scheme.scheme_name == Scheme.LAGOSHOMS:
        results = run_all_checks(values, property_price=prop.price)
        result = results['LAGOSHOMS']
    else:
        results = run_all_checks(values)
        result = results[prop.scheme.scheme_name]
    return result['eligible'], result


def search(request):
    """Housing Finder page - shows only properties the session qualifies
    for, further narrowed by the search filters."""
    values = request.session.get('eligibility')

    if not values:
        return render(request, 'properties/search.html', {'no_session': True})

    # All available properties the user qualifies for, before filters.
    all_available = Property.objects.filter(status=Property.AVAILABLE).select_related('scheme')
    qualifying = [p for p in all_available if _qualifies(p, values)[0]]
    total_qualifying = len(qualifying)

    # Apply search filters on top.
    keyword = request.GET.get('keyword', '').strip()
    location = request.GET.get('location', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    bedrooms = request.GET.get('bedrooms', '').strip()

    filtered = qualifying

    if keyword:
        filtered = [p for p in filtered if keyword.lower() in p.address.lower()
                    or keyword.lower() in p.description.lower()]

    if location:
        location_lower = location.lower()
        filtered = [
            p for p in filtered
            if location_lower in p.address.lower() or location_lower in (p.area or '').lower()
        ]

    if max_price:
        try:
            max_price_val = Decimal(max_price)
            filtered = [p for p in filtered if p.price <= max_price_val]
        except (InvalidOperation, ValueError):
            pass

    if bedrooms:
        try:
            bedrooms_val = int(bedrooms)
            filtered = [p for p in filtered if p.bedrooms >= bedrooms_val]
        except ValueError:
            pass

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
    """Property Detail page - shows the property plus the session's
    eligibility for this specific property."""
    prop = get_object_or_404(Property.objects.select_related('scheme'), pk=pk)
    values = request.session.get('eligibility')

    if not values:
        return render(request, 'properties/detail.html', {'no_session': True, 'property': prop})

    eligible, result = _qualifies(prop, values)

    required_equity = None
    if prop.scheme.scheme_name == Scheme.LAGOSHOMS:
        required_equity = prop.price * Decimal('0.30')

    context = {
        'no_session': False,
        'property': prop,
        'eligible': eligible,
        'result': result,
        'required_equity': required_equity,
        'user_equity': values.get('equity'),
    }
    return render(request, 'properties/detail.html', context)


def data_protection(request):
    """Static public page explaining data handling."""
    return render(request, 'data_protection.html')