import datetime
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from eligibility import rules
from eligibility.models import EligibilityRule
from properties.models import Property, Scheme


SCHEMES = [
    {
        'scheme_name': Scheme.NHF,
        'description': "Access affordable homes through the Federal Government's contributory housing scheme.",
        'official_url': 'https://www.fmbn.gov.ng',
        'icon': 'landmark',
    },
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'description': "Lagos State's affordable housing scheme for residents, with flexible payment options.",
        'official_url': 'https://lagoshoms.gov.ng',
        'icon': 'building',
    },
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'description': 'Move in now, own later. A flexible path to homeownership.',
        'official_url': 'https://housing.lagosstate.gov.ng/',
        'icon': 'home',
    },
]

# Initial rule (version 1) for each scheme. After this, thresholds are changed
# in Django Admin, not here. seed_data never overwrites a rule that already
# has criteria, so admin edits are safe.
RULES = {
    Scheme.NHF: {
        'min_income': Decimal('100000'), 'max_income': Decimal('300000'),
        'min_nhf_months': 6, 'max_age': 60,
        'source_note': (
            'The minimum of 6 months of NHF contributions follows the conditions '
            'FMBN publishes for NHF loans. The income band of \u20a6100,000 to '
            '\u20a6300,000 and the age limit of 60 are project-defined assumptions '
            'for this demonstration; they were not found in the FMBN conditions reviewed.'),
    },
    Scheme.LAGOSHOMS: {
        'min_income': Decimal('343000'),
        'equity_percent': Decimal('30'), 'max_dti': Decimal('0.40'),
        'source_note': (
            'All thresholds are project-defined assumptions for this demonstration. '
            "They differ from LagosHOMS's own published application requirements."),
    },
    Scheme.RENT_TO_OWN: {
        'min_income': Decimal('100000'), 'max_income': Decimal('300000'),
        'min_residency_years': 2, 'disallow_prior_owner': True,
        'source_note': (
            'All thresholds are project-defined assumptions for this demonstration. '
            'FMBN and the Lagos State Government each run their own Rent-to-Own '
            'programmes with different published criteria.'),
    },
}

PROPERTIES = [
    # NHF
    {
        'scheme_name': Scheme.NHF,
        'address': '15 Adebayo Street, Yaba, Lagos',
        'area': 'Yaba',
        'price': 15000000,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'A comfortable 3 bedroom home in Yaba, close to schools, markets and the Third Mainland Bridge.',
        'image_url': 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900',
    },
    {
        'scheme_name': Scheme.NHF,
        'address': '42 Alhaji Masha Road, Surulere, Lagos',
        'area': 'Surulere',
        'price': 8500000,
        'bedrooms': 2,
        'bathrooms': 1,
        'description': 'A cozy 2 bedroom apartment in the heart of Surulere, ideal for a small family.',
        'image_url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=900',
    },
    {
        'scheme_name': Scheme.NHF,
        'address': '11 Ogunlana Drive, Surulere, Lagos',
        'area': 'Surulere',
        'price': 12000000,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'A spacious 3 bedroom bungalow with a private compound and good road network.',
        'image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900',
    },
    {
        'scheme_name': Scheme.NHF,
        'address': '5 Herbert Macaulay Way, Yaba, Lagos',
        'area': 'Yaba',
        'price': 18000000,
        'bedrooms': 3,
        'bathrooms': 3,
        'description': 'A modern 3 bedroom bungalow in Ajah, well-planned and secure, close to amenities.',
        'image_url': 'https://images.unsplash.com/photo-1602343168117-bb8ffe3e2e9f?w=900',
    },
    # LagosHOMS
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'address': '7 Olayiwola Close, Ikeja, Lagos',
        'area': 'Ikeja',
        'price': 28000000,
        'bedrooms': 4,
        'bathrooms': 3,
        'description': 'A well-finished 4 bedroom apartment in Ikeja, close to the airport and major offices.',
        'image_url': 'https://images.unsplash.com/photo-1613977257363-707ba9348227?w=900',
    },
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'address': '23 Ogunlana Drive, Lekki Phase 1, Lagos',
        'area': 'Lekki Phase 1',
        'price': 45000000,
        'bedrooms': 5,
        'bathrooms': 4,
        'description': 'A 5 bedroom terrace in Victoria Island with premium finishes and 24/7 security.',
        'image_url': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=900',
    },
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'address': '8 Admiralty Way, Lekki Phase 1, Lagos',
        'area': 'Lekki Phase 1',
        'price': 38000000,
        'bedrooms': 4,
        'bathrooms': 4,
        'description': 'A secure and well-planned 4 bedroom duplex in Lekki, featuring fitted kitchen and ensuite rooms.',
        'image_url': 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=900',
    },
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'address': '14 Bourdillon Road, Ikoyi, Lagos',
        'area': 'Ikoyi',
        'price': 60000000,
        'bedrooms': 5,
        'bathrooms': 5,
        'description': 'A luxury 5 bedroom duplex in Ikoyi with a private garden and dedicated parking.',
        'image_url': 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=900',
    },
    # Rent-to-Own
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'address': '8 Babs Animashaun Street, Surulere, Lagos',
        'area': 'Surulere',
        'price': 12000000,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'A 3 bedroom terrace in Surulere available on a flexible rent-to-own payment plan.',
        'image_url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=900',
    },
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'address': '19 Mobolaji Bank Anthony Way, Ikeja, Lagos',
        'area': 'Ikeja',
        'price': 18000000,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'A 3 bedroom apartment in Ikeja, move in now and own it gradually over time.',
        'image_url': 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=900',
    },
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'address': '3 Opebi Road, Ikeja, Lagos',
        'area': 'Ikeja',
        'price': 22000000,
        'bedrooms': 4,
        'bathrooms': 3,
        'description': 'A 4 bedroom terrace on Opebi Road with lower initial payments and gradual ownership.',
        'image_url': 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900',
    },
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'address': '27 Ago Palace Way, Okota, Lagos',
        'area': 'Okota',
        'price': 9500000,
        'bedrooms': 2,
        'bathrooms': 1,
        'description': 'A 2 bedroom bungalow in Okota, a low initial payment start on the path to ownership.',
        'image_url': 'https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=900',
    },
]


class Command(BaseCommand):
    help = 'Seeds schemes, initial (version 1) eligibility rules and 12 sample properties.'

    def handle(self, *args, **options):
        scheme_objs = {}
        for data in SCHEMES:
            scheme, created = Scheme.objects.get_or_create(
                scheme_name=data['scheme_name'],
                defaults={'description': data['description'],
                          'official_url': data['official_url'],
                          'icon': data['icon'], 'active': True})
            if not created and not scheme.official_url:
                scheme.official_url = data['official_url']
                scheme.save(update_fields=['official_url'])
            scheme_objs[data['scheme_name']] = scheme
            self.stdout.write(self.style.SUCCESS(
                'Scheme %s: %s' % ('created' if created else 'kept', scheme)))

        for code, values in RULES.items():
            scheme = scheme_objs[code]
            existing = scheme.rules.order_by('version').first()
            if existing is None:
                EligibilityRule.objects.create(
                    scheme=scheme, version=1,
                    effective_from=datetime.date(2026, 1, 1), is_active=True, **values)
                self.stdout.write(self.style.SUCCESS('Rule v1 created for %s' % scheme))
            elif not rules.describe(existing.to_params()):
                for field, value in values.items():
                    setattr(existing, field, value)
                existing.is_active = True
                existing.save()
                self.stdout.write(self.style.SUCCESS('Rule v%s filled in for %s' % (existing.version, scheme)))
            else:
                self.stdout.write('Rule for %s already has criteria - left unchanged' % scheme)

        for index, data in enumerate(PROPERTIES, start=1):
            scheme = scheme_objs[data['scheme_name']]
            prop, created = Property.objects.update_or_create(
                address=data['address'],
                defaults={
                    'scheme': scheme,
                    'area': data['area'],
                    'price': data['price'],
                    'bedrooms': data['bedrooms'],
                    'bathrooms': data['bathrooms'],
                    'description': data['description'],
                    'status': Property.AVAILABLE,
                    'image_url': data['image_url'],
                },
            )
            # Use a local image if one has been dropped into media/properties/
            local_name = 'properties/property-%02d.jpg' % index
            if not prop.image and (settings.MEDIA_ROOT / local_name).exists():
                prop.image = local_name
                prop.save(update_fields=['image'])
                self.stdout.write('  attached local image %s' % local_name)
            self.stdout.write(self.style.SUCCESS(
                'Property %s: %s' % ('created' if created else 'updated', prop)))

        self.stdout.write(self.style.SUCCESS('Seed data complete.'))
