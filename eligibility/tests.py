from django.test import SimpleTestCase

from .rules import check_nhf, check_lagoshoms, check_rent_to_own


class NHFRuleTests(SimpleTestCase):

    def test_tc001_eligible(self):
        result = check_nhf(income=250000, nhf_months=8, age=35)
        self.assertTrue(result['eligible'])

    def test_tc002_not_eligible_low_months(self):
        result = check_nhf(income=250000, nhf_months=3, age=35)
        self.assertFalse(result['eligible'])

    def test_tc003_not_eligible_low_income(self):
        result = check_nhf(income=80000, nhf_months=8, age=35)
        self.assertFalse(result['eligible'])

    def test_tc004_not_eligible_high_income(self):
        result = check_nhf(income=350000, nhf_months=8, age=35)
        self.assertFalse(result['eligible'])


class LagosHOMSRuleTests(SimpleTestCase):

    def test_tc005_eligible(self):
        result = check_lagoshoms(income=350000, equity=4500000, dti_ratio=0.30, property_price=15000000)
        self.assertTrue(result['eligible'])

    def test_tc006_not_eligible_low_equity(self):
        result = check_lagoshoms(income=350000, equity=2000000, dti_ratio=0.30, property_price=15000000)
        self.assertFalse(result['eligible'])

    def test_tc007_not_eligible_high_dti(self):
        result = check_lagoshoms(income=350000, equity=4500000, dti_ratio=0.50, property_price=15000000)
        self.assertFalse(result['eligible'])

    def test_tc008_not_eligible_low_income(self):
        result = check_lagoshoms(income=250000, equity=4500000, dti_ratio=0.30, property_price=15000000)
        self.assertFalse(result['eligible'])

    def test_tc009_eligible_high_income(self):
        result = check_lagoshoms(income=400000, equity=4500000, dti_ratio=0.30, property_price=15000000)
        self.assertTrue(result['eligible'])


class RentToOwnRuleTests(SimpleTestCase):

    def test_tc010_eligible(self):
        result = check_rent_to_own(income=250000, residency_yrs=3, prior_owner=False)
        self.assertTrue(result['eligible'])

    def test_tc011_not_eligible_low_residency(self):
        result = check_rent_to_own(income=250000, residency_yrs=1, prior_owner=False)
        self.assertFalse(result['eligible'])

    def test_tc012_not_eligible_prior_owner(self):
        result = check_rent_to_own(income=250000, residency_yrs=3, prior_owner=True)
        self.assertFalse(result['eligible'])

    def test_tc013_not_eligible_low_income(self):
        result = check_rent_to_own(income=80000, residency_yrs=3, prior_owner=False)
        self.assertFalse(result['eligible'])

    def test_tc014_not_eligible_high_income(self):
        result = check_rent_to_own(income=350000, residency_yrs=3, prior_owner=False)
        self.assertFalse(result['eligible'])


class BoundaryTests(SimpleTestCase):
    """Upper and lower boundary cases for each scheme's income threshold."""

    def test_tc015_nhf_eligible_at_exact_upper_bound(self):
        result = check_nhf(income=300000, nhf_months=8, age=35)
        self.assertTrue(result['eligible'])

    def test_tc016_nhf_not_eligible_one_above_upper_bound(self):
        result = check_nhf(income=300001, nhf_months=8, age=35)
        self.assertFalse(result['eligible'])

    def test_tc017_rent_to_own_eligible_at_exact_upper_bound(self):
        result = check_rent_to_own(income=300000, residency_yrs=3, prior_owner=False)
        self.assertTrue(result['eligible'])

    def test_tc018_rent_to_own_not_eligible_one_above_upper_bound(self):
        result = check_rent_to_own(income=300001, residency_yrs=3, prior_owner=False)
        self.assertFalse(result['eligible'])

    def test_tc019_lagoshoms_eligible_at_exact_lower_bound(self):
        result = check_lagoshoms(income=343000, equity=4500000, dti_ratio=0.30, property_price=15000000)
        self.assertTrue(result['eligible'])

    def test_tc020_lagoshoms_not_eligible_one_below_lower_bound(self):
        result = check_lagoshoms(income=342999, equity=4500000, dti_ratio=0.30, property_price=15000000)
        self.assertFalse(result['eligible'])