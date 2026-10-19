def site_meta(request):
    """Makes the site brand/tagline available in every template without
    repeating it in every view."""
    return {
        'SITE_BRAND': 'Affordable Housing',
        'SITE_SUBTITLE': 'Finder and Eligibility System',
        'SITE_TAGLINE': 'Homes. People. Progress.',
    }
