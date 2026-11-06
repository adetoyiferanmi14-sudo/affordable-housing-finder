from django.db import models


class Scheme(models.Model):
    """One of the three housing schemes: NHF, LagosHOMS, Rent-to-Own.

    The eligibility thresholds are NOT stored here. They live in
    eligibility.EligibilityRule, which the engine executes, so there is a
    single source of truth.
    """

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
    official_url = models.URLField(
        blank=True,
        help_text='Official page users are sent to for the next step. Verify it before publishing.')
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
    area = models.CharField(max_length=100, blank=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    image = models.ImageField(upload_to='properties/', blank=True)
    image_url = models.URLField(
        max_length=500, blank=True,
        help_text='Fallback only. Used when no image file has been uploaded.')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    @property
    def image_src(self):
        """Uploaded file if there is one, otherwise the fallback URL."""
        if self.image:
            return self.image.url
        return self.image_url
