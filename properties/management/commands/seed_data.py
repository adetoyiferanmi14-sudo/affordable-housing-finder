from django.core.management.base import BaseCommand

from properties.models import Scheme, Property
from eligibility.models import EligibilityRule


SCHEMES = [
    {
        'scheme_name': Scheme.NHF,
        'description': "Access affordable homes through the Federal Government's contributory housing scheme.",
        'criteria_text': 'Income between N100,000 and N300,000, at least 6 months of NHF contributions, age 60 or under.',
        'icon': 'landmark',
        'active': True,
    },
    {
        'scheme_name': Scheme.LAGOSHOMS,
        'description': "Lagos State's affordable housing scheme for residents, with flexible payment options.",
        'criteria_text': 'Income of at least N343,000 per month, equity of at least 30% of the property price, and a debt-to-income ratio of 0.40 or lower.',
        'icon': 'building',
        'active': True,
    },
    {
        'scheme_name': Scheme.RENT_TO_OWN,
        'description': 'Move in now, own later. A flexible path to homeownership.',
        'criteria_text': 'Income between N100,000 and N300,000, at least 2 years of Lagos residency, no prior homeownership.',
        'icon': 'home',
        'active': True,
    },
]

RULES = [
    {'scheme_name': Scheme.NHF, 'rule_condition': 'income 100000-300000 AND nhf_months>=6 AND age<=60', 'priority': 1},
    {'scheme_name': Scheme.LAGOSHOMS, 'rule_condition': 'income >= 343000 AND equity >= price*0.30 AND dti <= 0.40', 'priority': 1},
    {'scheme_name': Scheme.RENT_TO_OWN, 'rule_condition': 'income 100000-300000 AND residency_yrs>=2 AND prior_owner=False', 'priority': 1},
]

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
    help = 'Seeds the database with the 3 housing schemes, their documentation rules, and 12 sample properties.'

    def handle(self, *args, **options):
        scheme_objs = {}
        for data in SCHEMES:
            scheme, created = Scheme.objects.update_or_create(
                scheme_name=data['scheme_name'],
                defaults={
                    'description': data['description'],
                    'criteria_text': data['criteria_text'],
                    'icon': data['icon'],
                    'active': data['active'],
                },
            )
            scheme_objs[data['scheme_name']] = scheme
            self.stdout.write(self.style.SUCCESS(f'Scheme {"created" if created else "updated"}: {scheme}'))

        for data in RULES:
            scheme = scheme_objs[data['scheme_name']]
            rule, created = EligibilityRule.objects.update_or_create(
                scheme=scheme,
                priority=data['priority'],
                defaults={'rule_condition': data['rule_condition']},
            )
            self.stdout.write(self.style.SUCCESS(f'Rule {"created" if created else "updated"} for {scheme}'))

        for data in PROPERTIES:
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
            self.stdout.write(self.style.SUCCESS(f'Property {"created" if created else "updated"}: {prop}'))

        self.stdout.write(self.style.SUCCESS('Seed data complete.'))