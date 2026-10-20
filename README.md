# Affordable Housing Finder and Eligibility System

National Diploma project - Lagos State University, Ojo.
Django + SQLite. No accounts, no passwords, no admin panel. Five pages.

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
# Affordable Housing Finder and Eligibility System

National Diploma project - Lagos State University, Ojo.
Django + SQLite. No accounts, no passwords, no admin panel. Five pages.
Live at: https://affordablehousing.pythonanywhere.com

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py seed_data



## Run the eligibility rule tests (20 test cases)

```bash
python manage.py test eligibility
```

20 tests across 4 classes: NHF (4), LagosHOMS (5), Rent-to-Own (5), and
boundary tests covering both sides of each income threshold (6).

## Deploy on PythonAnywhere

1. Push this project to GitHub (or upload a zip directly).
2. Open a Bash console on PythonAnywhere and clone the repo (or unzip the upload).
3. Create a virtualenv and `pip install -r requirements.txt`.
4. Run `python manage.py makemigrations`, `migrate`, then `python manage.py seed_data`.
5. Create a new Web App (manual configuration, matching your Python version).
6. Point the WSGI file at `affordable_housing.wsgi.application` (edit the
   PythonAnywhere-generated `wsgi.py` to import from this project, or set
   the working directory so `affordable_housing/wsgi.py` is used directly).
7. In the Web tab, add a static files mapping: URL `/static/` -> directory
   `.../affordable_housing/staticfiles`, and run `python manage.py collectstatic`.
8. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `settings.py` with your
   actual PythonAnywhere subdomain if it isn't `affordablehousing.pythonanywhere.com`.
9. Set `DEBUG = False` in `settings.py` before final deployment.
10. Reload the web app and test the live URL.

## Structure

- `properties/` - Scheme + Property models (Property includes an `area` field), home/search/detail/data-protection views
- `eligibility/` - EligibilityRule model (docs only), `rules.py` (the real logic), `forms.py` (server-side validation), check view, 20 tests
- `templates/` - the five pages, all extending `base.html`
- `static/css/style.css` - dark theme, emerald accents, mobile breakpoints at 720px/400px

## The three rules (eligibility/rules.py)

- **NHF**: income 100,000-300,000, NHF contributions >= 6 months, age <= 60
- **LagosHOMS**: income >= 343,000 (no upper limit), equity >= 30% of the specific property's price, DTI <= 0.40
- **Rent-to-Own**: income 100,000-300,000, Lagos residency >= 2 years, no prior homeownership

All thresholds were developed for this project - they are not official
FMBN, LagosHOMS, or government criteria. No `eval()`, no dynamic parsing -
plain Python conditionals in pure functions.

Note: because the NHF/Rent-to-Own band (100,000-300,000) and the LagosHOMS
floor (343,000+) do not overlap, a user earning between 300,001 and 342,999
will not qualify for any of the three schemes. This is expected behaviour
given how the thresholds are defined, not a bug.

LagosHOMS's equity check is evaluated per property (30% of that specific
property's price), not as a single global check - see `_qualifies()` in
`properties/views.py`.

## Debt-to-income ratio

The form does not ask for a DTI ratio directly - it asks for "Monthly Loan
Repayments," and the server computes `dti_ratio = monthly_repayments / income`
before running the LagosHOMS rule.

## Session and data handling

No personal data is written to the database. The eight eligibility inputs
live only in a signed (not encrypted) session cookie, expiring after 1 hour
or on browser close. See the Data Protection page for the full explanation.


## Run the eligibility rule tests (14 test cases)

```bash
python manage.py test eligibility
```

## Deploy on PythonAnywhere

1. Push this project to GitHub.
2. Open a Bash console on PythonAnywhere and clone the repo.
3. Create a virtualenv and `pip install -r requirements.txt`.
4. Run `python manage.py makemigrations`, `migrate`, then `python manage.py seed_data`.
5. Create a new Web App (manual configuration, matching your Python version).
6. Point the WSGI file at `affordable_housing.wsgi.application` (edit the
   PythonAnywhere-generated `wsgi.py` to import from this project, or set
   the working directory so `affordable_housing/wsgi.py` is used directly).
7. In the Web tab, add a static files mapping: URL `/static/` -> directory
   `.../affordable_housing/staticfiles`, and run `python manage.py collectstatic`.
8. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `settings.py` with your
   actual PythonAnywhere subdomain if it isn't `bumble001.pythonanywhere.com`.
9. Reload the web app and test the live URL.

## Structure

- `properties/` - Scheme + Property models, home/search/detail/data-protection views
- `eligibility/` - EligibilityRule model (docs only), `rules.py` (the real logic), check view, 14 tests
- `templates/` - the five pages, all extending `base.html`
- `static/css/style.css` - dark theme, emerald accents, mobile breakpoints at 720px/400px

## The three rules (eligibility/rules.py)

- **NHF**: income 100,000-300,000, NHF contributions >= 6 months, age <= 60
- **LagosHOMS**: income 100,000-300,000, equity >= 30% of the property's price, DTI <= 0.40
- **Rent-to-Own**: income 100,000-300,000, Lagos residency >= 2 years, no prior homeownership

No `eval()`, no dynamic parsing - plain Python conditionals in pure functions.
