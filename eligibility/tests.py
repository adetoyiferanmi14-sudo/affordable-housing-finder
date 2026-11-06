import datetime
from decimal import Decimal

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from properties.models import Property, Scheme

from . import rules
from .engine import load_params, run_all_checks
from .forms import EligibilityForm
from .models import EligibilityRule

# Rule parameters mirroring the version-1 rules seeded into the database.
# The pure-logic tests use these directly, so they need no database.
NHF = rules.RuleParams(
    scheme_code='NHF', scheme_label='National Housing Fund (NHF)',
    min_income=Decimal('100000'), max_income=Decimal('300000'),
    min_nhf_months=6, max_age=60)
LAGOSHOMS = rules.RuleParams(
    scheme_code='LAGOSHOMS', scheme_label='LagosHOMS',
    min_income=Decimal('343000'), equity_percent=Decimal('30'), max_dti=Decimal('0.40'))
RENT_TO_OWN = rules.RuleParams(
    scheme_code='RENT_TO_OWN', scheme_label='Rent-to-Own',
    min_income=Decimal('100000'), max_income=Decimal('300000'),
    min_residency_years=2, disallow_prior_owner=True)


def nhf(income, nhf_months, age):
    values = {'income': income, 'nhf_months': nhf_months, 'age': age}
    return rules.evaluate(NHF, values)['eligible']


def lagoshoms(income, equity, dti_ratio, property_price):
    values = {'income': income, 'equity': equity, 'dti_ratio': dti_ratio}
    return rules.evaluate(LAGOSHOMS, values, property_price)['eligible']


def rent_to_own(income, residency_yrs, prior_owner):
    values = {'income': income, 'residency_yrs': residency_yrs, 'prior_owner': prior_owner}
    return rules.evaluate(RENT_TO_OWN, values)['eligible']


class NHFRuleTests(SimpleTestCase):

    def test_tc001_eligible(self):
        self.assertTrue(nhf(income=250000, nhf_months=8, age=35))

    def test_tc002_not_eligible_low_months(self):
        self.assertFalse(nhf(income=250000, nhf_months=3, age=35))

    def test_tc003_not_eligible_low_income(self):
        self.assertFalse(nhf(income=80000, nhf_months=8, age=35))

    def test_tc004_not_eligible_high_income(self):
        self.assertFalse(nhf(income=350000, nhf_months=8, age=35))


class LagosHOMSRuleTests(SimpleTestCase):

    def test_tc005_eligible(self):
        self.assertTrue(lagoshoms(350000, 4500000, 0.30, 15000000))

    def test_tc006_not_eligible_low_equity(self):
        self.assertFalse(lagoshoms(350000, 2000000, 0.30, 15000000))

    def test_tc007_not_eligible_high_dti(self):
        self.assertFalse(lagoshoms(350000, 4500000, 0.50, 15000000))

    def test_tc008_not_eligible_low_income(self):
        self.assertFalse(lagoshoms(250000, 4500000, 0.30, 15000000))

    def test_tc009_eligible_high_income(self):
        self.assertTrue(lagoshoms(400000, 4500000, 0.30, 15000000))


class RentToOwnRuleTests(SimpleTestCase):

    def test_tc010_eligible(self):
        self.assertTrue(rent_to_own(250000, 3, False))

    def test_tc011_not_eligible_low_residency(self):
        self.assertFalse(rent_to_own(250000, 1, False))

    def test_tc012_not_eligible_prior_owner(self):
        self.assertFalse(rent_to_own(250000, 3, True))

    def test_tc013_not_eligible_low_income(self):
        self.assertFalse(rent_to_own(80000, 3, False))

    def test_tc014_not_eligible_high_income(self):
        self.assertFalse(rent_to_own(350000, 3, False))


class BoundaryTests(SimpleTestCase):
    """Income boundaries: exact bound qualifies, one naira beyond does not."""

    def test_tc015_nhf_eligible_at_exact_upper_bound(self):
        self.assertTrue(nhf(300000, 8, 35))

    def test_tc016_nhf_not_eligible_one_above_upper_bound(self):
        self.assertFalse(nhf(300001, 8, 35))

    def test_tc017_rent_to_own_eligible_at_exact_upper_bound(self):
        self.assertTrue(rent_to_own(300000, 3, False))

    def test_tc018_rent_to_own_not_eligible_one_above_upper_bound(self):
        self.assertFalse(rent_to_own(300001, 3, False))

    def test_tc019_lagoshoms_eligible_at_exact_lower_bound(self):
        self.assertTrue(lagoshoms(343000, 4500000, 0.30, 15000000))

    def test_tc020_lagoshoms_not_eligible_one_below_lower_bound(self):
        self.assertFalse(lagoshoms(342999, 4500000, 0.30, 15000000))


class AllCriteriaBoundaryTests(SimpleTestCase):
    """Both sides of every other threshold. All comparisons are inclusive."""

    def test_tc021_nhf_eligible_at_exact_lower_income_bound(self):
        self.assertTrue(nhf(100000, 8, 35))

    def test_tc022_nhf_not_eligible_one_below_lower_income_bound(self):
        self.assertFalse(nhf(99999, 8, 35))

    def test_tc023_rent_to_own_eligible_at_exact_lower_income_bound(self):
        self.assertTrue(rent_to_own(100000, 3, False))

    def test_tc024_rent_to_own_not_eligible_one_below_lower_income_bound(self):
        self.assertFalse(rent_to_own(99999, 3, False))

    def test_tc025_nhf_eligible_with_exactly_6_months(self):
        self.assertTrue(nhf(250000, 6, 35))

    def test_tc026_nhf_not_eligible_with_5_months(self):
        self.assertFalse(nhf(250000, 5, 35))

    def test_tc027_nhf_eligible_at_age_60(self):
        self.assertTrue(nhf(250000, 8, 60))

    def test_tc028_nhf_not_eligible_at_age_61(self):
        self.assertFalse(nhf(250000, 8, 61))

    def test_tc029_lagoshoms_eligible_with_dti_exactly_0_40(self):
        self.assertTrue(lagoshoms(350000, 4500000, '0.40', 15000000))

    def test_tc030_lagoshoms_not_eligible_with_dti_0_41(self):
        self.assertFalse(lagoshoms(350000, 4500000, '0.41', 15000000))

    def test_tc031_rent_to_own_eligible_with_exactly_2_years(self):
        self.assertTrue(rent_to_own(250000, 2, False))

    def test_tc032_rent_to_own_not_eligible_with_1_year(self):
        self.assertFalse(rent_to_own(250000, 1, False))

    def test_tc033_lagoshoms_eligible_with_equity_exactly_30_percent(self):
        self.assertTrue(lagoshoms(350000, 8400000, 0.30, 28000000))

    def test_tc034_lagoshoms_not_eligible_with_equity_1_naira_short(self):
        self.assertFalse(lagoshoms(350000, 8399999, 0.30, 28000000))


def valid_form_data(**overrides):
    data = {'age': '35', 'income': '250000', 'nhf_months': '8', 'residency_yrs': '3',
            'monthly_repayments': '75000', 'prior_owner': 'no', 'equity': '5000000'}
    data.update(overrides)
    return data


class InvalidInputTests(SimpleTestCase):
    """Invalid input is rejected or fails closed. It never produces a
    misleading 'eligible' result."""

    def test_tc035_form_accepts_valid_data(self):
        self.assertTrue(EligibilityForm(valid_form_data()).is_valid())

    def test_tc036_form_rejects_negative_income(self):
        self.assertFalse(EligibilityForm(valid_form_data(income='-1')).is_valid())

    def test_tc037_form_rejects_zero_income(self):
        self.assertFalse(EligibilityForm(valid_form_data(income='0')).is_valid())

    def test_tc038_form_rejects_age_zero(self):
        self.assertFalse(EligibilityForm(valid_form_data(age='0')).is_valid())

    def test_tc039_form_rejects_age_under_18(self):
        self.assertFalse(EligibilityForm(valid_form_data(age='17')).is_valid())

    def test_tc040_form_rejects_non_numeric_income(self):
        form = EligibilityForm(valid_form_data(income='abc'))
        self.assertFalse(form.is_valid())
        self.assertIn('income', form.errors)

    def test_tc041_form_rejects_negative_equity(self):
        self.assertFalse(EligibilityForm(valid_form_data(equity='-5')).is_valid())

    def test_tc042_form_rejects_negative_repayments(self):
        self.assertFalse(EligibilityForm(valid_form_data(monthly_repayments='-5')).is_valid())

    def test_tc043_form_rejects_unknown_prior_owner_value(self):
        self.assertFalse(EligibilityForm(valid_form_data(prior_owner='maybe')).is_valid())

    def test_tc044_form_rejects_missing_field(self):
        data = valid_form_data()
        del data['equity']
        self.assertFalse(EligibilityForm(data).is_valid())

    def test_tc045_engine_fails_closed_on_negative_income(self):
        self.assertFalse(nhf(-1, 8, 35))

    def test_tc046_engine_fails_closed_on_age_zero(self):
        self.assertFalse(nhf(250000, 8, 0))

    def test_tc047_engine_fails_closed_on_non_numeric_values(self):
        self.assertFalse(nhf('abc', 8, 35))
        self.assertFalse(nhf(250000, 'abc', 35))
        self.assertFalse(lagoshoms(350000, 'abc', 0.30, 15000000))

    def test_tc048_equity_greater_than_price_passes_the_equity_rule(self):
        result = rules.evaluate(
            LAGOSHOMS, {'income': 350000, 'equity': 20000000, 'dti_ratio': '0.30'}, 10000000)
        self.assertTrue(result['eligible'])
        self.assertEqual(result['required_equity'], Decimal('3000000'))

    def test_tc049_missing_prior_owner_does_not_pass_rent_to_own(self):
        result = rules.evaluate(RENT_TO_OWN, {'income': 250000, 'residency_yrs': 3})
        self.assertFalse(result['eligible'])


class GeneratedDocumentationTests(SimpleTestCase):

    def test_labels_are_generated_from_the_parameters(self):
        labels = dict(rules.describe(LAGOSHOMS))
        self.assertEqual(labels['income_in_range'], 'Income of \u20a6343,000 or more')
        self.assertIn('30%', labels['equity_sufficient'])
        self.assertIn('40%', labels['dti_acceptable'])

    def test_labels_follow_a_changed_threshold(self):
        changed = rules.RuleParams(scheme_code='NHF', min_income=Decimal('120000'),
                                   max_income=Decimal('310000'))
        self.assertIn('\u20a6120,000', dict(rules.describe(changed))['income_in_range'])

    def test_equity_is_pending_without_a_property(self):
        result = rules.evaluate(LAGOSHOMS, {'income': 350000, 'dti_ratio': '0.30'})
        self.assertTrue(result['eligible'])
        self.assertTrue(result['in_principle'])
        self.assertIsNone(result['checks']['equity_sufficient'])

    def test_rule_with_no_criteria_is_never_eligible(self):
        result = rules.evaluate(rules.RuleParams(scheme_code='NHF'), {'income': 250000})
        self.assertFalse(result['eligible'])


class IncomeGapTests(SimpleTestCase):
    ALL = [NHF, LAGOSHOMS, RENT_TO_OWN]

    def test_uncovered_bands_are_computed_from_the_rules(self):
        self.assertEqual(
            rules.uncovered_income_bands(self.ALL),
            [(Decimal('0'), Decimal('99999')), (Decimal('300001'), Decimal('342999'))])

    def test_income_just_inside_and_outside_each_band(self):
        self.assertFalse(rules.covers_income(self.ALL, 99999))
        self.assertTrue(rules.covers_income(self.ALL, 100000))
        self.assertTrue(rules.covers_income(self.ALL, 300000))
        self.assertFalse(rules.covers_income(self.ALL, 300001))
        self.assertFalse(rules.covers_income(self.ALL, 342999))
        self.assertTrue(rules.covers_income(self.ALL, 343000))

    def test_band_text(self):
        self.assertEqual(rules.describe_band(Decimal('300001'), Decimal('342999')),
                         '\u20a6300,001 to \u20a6342,999')
        self.assertEqual(rules.describe_band(Decimal('0'), Decimal('99999')),
                         'below \u20a6100,000')


def make_world():
    """Three schemes with version-1 rules and four properties."""
    schemes = {}
    for code in (Scheme.NHF, Scheme.LAGOSHOMS, Scheme.RENT_TO_OWN):
        schemes[code] = Scheme.objects.create(
            scheme_name=code, description='d', official_url='https://example.org')
    day = datetime.date(2026, 1, 1)
    EligibilityRule.objects.create(
        scheme=schemes[Scheme.NHF], version=1, effective_from=day,
        min_income=Decimal('100000'), max_income=Decimal('300000'),
        min_nhf_months=6, max_age=60)
    EligibilityRule.objects.create(
        scheme=schemes[Scheme.LAGOSHOMS], version=1, effective_from=day,
        min_income=Decimal('343000'), equity_percent=Decimal('30'), max_dti=Decimal('0.40'))
    EligibilityRule.objects.create(
        scheme=schemes[Scheme.RENT_TO_OWN], version=1, effective_from=day,
        min_income=Decimal('100000'), max_income=Decimal('300000'),
        min_residency_years=2, disallow_prior_owner=True)
    return schemes


def make_property(scheme, address, price, area='Yaba'):
    return Property.objects.create(
        scheme=scheme, address=address, area=area, price=Decimal(price),
        bedrooms=3, bathrooms=2, description='d')


class RuleLoadingTests(TestCase):
    """Rules come from the database: versions, effective dates, no code change."""

    def setUp(self):
        self.schemes = make_world()
        self.nhf_scheme = self.schemes[Scheme.NHF]

    def test_loader_returns_the_stored_thresholds(self):
        params = load_params(datetime.date(2026, 6, 1))
        self.assertEqual(params['LAGOSHOMS'].min_income, Decimal('343000.00'))
        self.assertEqual(params['NHF'].max_age, 60)

    def test_latest_effective_version_is_used(self):
        EligibilityRule.objects.create(
            scheme=self.nhf_scheme, version=2, effective_from=datetime.date(2026, 3, 1),
            min_income=Decimal('200000'), max_income=Decimal('300000'),
            min_nhf_months=6, max_age=60)
        self.assertEqual(load_params(datetime.date(2026, 2, 1))['NHF'].min_income, Decimal('100000.00'))
        self.assertEqual(load_params(datetime.date(2026, 4, 1))['NHF'].min_income, Decimal('200000.00'))

    def test_future_dated_rule_is_ignored_until_its_date(self):
        EligibilityRule.objects.create(
            scheme=self.nhf_scheme, version=2, effective_from=datetime.date(2030, 1, 1),
            min_income=Decimal('1'), max_income=Decimal('2'), min_nhf_months=1)
        self.assertEqual(load_params(datetime.date(2026, 6, 1))['NHF'].version, 1)

    def test_inactive_rule_is_ignored(self):
        EligibilityRule.objects.filter(scheme=self.nhf_scheme).update(is_active=False)
        result = run_all_checks({'income': 250000}, params_by_scheme=load_params())['NHF']
        self.assertFalse(result['eligible'])
        self.assertIn('No active eligibility rule', result['reason'])

    def test_changing_a_threshold_in_the_database_changes_the_result(self):
        values = {'income': 320000, 'nhf_months': 8, 'age': 35}
        self.assertFalse(run_all_checks(values)['NHF']['eligible'])
        EligibilityRule.objects.filter(scheme=self.nhf_scheme).update(max_income=Decimal('350000'))
        self.assertTrue(run_all_checks(values)['NHF']['eligible'])

    def test_rule_summary_is_generated_from_the_stored_values(self):
        rule = EligibilityRule.objects.get(scheme=self.nhf_scheme)
        self.assertIn('6 months', rule.summary)
        self.assertIn('\u20a6300,000', rule.summary)


class ViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        schemes = make_world()
        cls.nhf_prop = make_property(schemes[Scheme.NHF], '1 Test Road, Yaba', '15000000')
        cls.lh_cheap = make_property(schemes[Scheme.LAGOSHOMS], '2 Test Road, Ikeja', '28000000', 'Ikeja')
        cls.lh_dear = make_property(schemes[Scheme.LAGOSHOMS], '3 Test Road, Ikoyi', '60000000', 'Ikoyi')
        cls.lh_small = make_property(schemes[Scheme.LAGOSHOMS], '4 Test Road, Ikeja', '10000000', 'Ikeja')
        cls.rto_prop = make_property(schemes[Scheme.RENT_TO_OWN], '5 Test Road, Surulere', '12000000', 'Surulere')

    def post(self, **overrides):
        return self.client.post(reverse('eligibility_check'), valid_form_data(**overrides))

    def test_invalid_post_stores_nothing_and_runs_no_rules(self):
        response = self.post(income='-5')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('eligibility', self.client.session)
        self.assertFalse(response.context['cards'])

    def test_non_numeric_post_is_rejected(self):
        response = self.post(income='abc')
        self.assertNotIn('eligibility', self.client.session)
        self.assertIn('income', response.context['form'].errors)

    def test_valid_post_shows_three_cards_and_stores_only_what_it_needs(self):
        response = self.post()
        cards = {c['code']: c['result'] for c in response.context['cards']}
        self.assertEqual(set(cards), {'NHF', 'LAGOSHOMS', 'RENT_TO_OWN'})
        self.assertTrue(cards['NHF']['eligible'])
        self.assertFalse(cards['LAGOSHOMS']['eligible'])
        self.assertTrue(cards['RENT_TO_OWN']['eligible'])
        stored = self.client.session['eligibility']
        self.assertNotIn('location', stored)
        self.assertNotIn('monthly_repayments', stored)
        self.assertEqual(Decimal(stored['dti_ratio']), Decimal('0.3'))

    def test_income_gap_shows_the_required_message(self):
        response = self.post(income='320000', monthly_repayments='96000')
        self.assertTrue(response.context['income_uncovered'])
        self.assertContains(response, 'No scheme currently covers this income band.')

    def test_covered_income_does_not_show_the_gap_message(self):
        response = self.post()
        self.assertFalse(response.context['income_uncovered'])
        self.assertNotContains(response, 'No scheme currently covers this income band.')

    def test_results_page_shows_the_disclaimer(self):
        self.assertContains(self.post(), 'final eligibility is subject to confirmation')

    def test_housing_finder_without_a_session_shows_the_fallback(self):
        response = self.client.get(reverse('property_search'))
        self.assertContains(response, 'Please fill in your details')

    def test_per_property_equity_decides_which_lagoshoms_properties_show(self):
        self.post(income='350000', monthly_repayments='105000', equity='15000000')
        response = self.client.get(reverse('property_search'))
        shown = {p.address for p in response.context['properties']}
        self.assertIn(self.lh_cheap.address, shown)      # needs 8.4m, has 15m
        self.assertNotIn(self.lh_dear.address, shown)    # needs 18m, has 15m
        self.assertNotIn(self.nhf_prop.address, shown)   # income above the NHF band
        self.assertNotIn(self.rto_prop.address, shown)

    def test_location_filter_matches_the_area_field(self):
        self.post(income='350000', monthly_repayments='105000', equity='15000000')
        response = self.client.get(reverse('property_search'), {'location': 'ikeja'})
        self.assertTrue(response.context['properties'])
        self.assertTrue(all(p.area == 'Ikeja' for p in response.context['properties']))

    def test_price_filter_runs_in_the_database(self):
        self.post(income='350000', monthly_repayments='105000', equity='15000000')
        response = self.client.get(reverse('property_search'), {'max_price': '20000000'})
        self.assertEqual([p.pk for p in response.context['properties']], [self.lh_small.pk])

    def test_detail_notes_when_equity_covers_the_whole_price(self):
        self.post(income='350000', monthly_repayments='105000', equity='12000000')
        response = self.client.get(reverse('property_detail', args=[self.lh_small.pk]))
        self.assertTrue(response.context['eligible'])
        self.assertTrue(response.context['equity_covers_price'])

    def test_detail_without_a_session_shows_the_fallback(self):
        response = self.client.get(reverse('property_detail', args=[self.lh_cheap.pk]))
        self.assertContains(response, 'Please fill in your details')
