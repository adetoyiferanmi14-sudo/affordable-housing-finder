from django.db import models


class Scheme(models.Model):
    """One of the three housing schemes: NHF, LagosHOMS, Rent-to-Own."""

    NHF = 'NHF'
    LAGOSHOMS = 'LAGOSHOMS'
    RENT_TO_OWN = 'RENT_TO_OWN'

    SCHEME_CHOICES = [
        (NHF, 'National Housing Fund (NHF)'),
        (LAGOSHOMS, 'LagosHOMS'),
        (RENT_TO_OWN, 'Rent-to-Own'),
    ]

    scheme_id = models.AutoField(primary_key=True)
    scheme_name = models.CharField(max_length=20, choices=SCHEME_CHOICES, unique=True)
    description = models.TextField()
    # Human-readable summary only - NOT the executed rule. The rule that is
    # actually evaluated lives in eligibility/rules.py as plain Python
    # conditionals. This field exists purely for display to the user.
    criteria_text = models.TextField(
        help_text='Human-readable summary, not the executed rule. '
                   'The executed rule lives in eligibility/rules.py.'
    )
    icon = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_scheme_name_display()


class Property(models.Model):
    """A single listed property that belongs to one housing scheme."""

    AVAILABLE = 'AVAILABLE'
    PENDING = 'PENDING'
    SOLD = 'SOLD'

    STATUS_CHOICES = [
        (AVAILABLE, 'Available'),
        (PENDING, 'Pending'),
        (SOLD, 'Sold'),
    ]

    property_id = models.AutoField(primary_key=True)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='properties')
    address = models.CharField(max_length=255)
    area = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    image_url = models.URLField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address