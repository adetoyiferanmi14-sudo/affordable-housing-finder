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

python manage.py runserver
```

Visit http://127.0.0.1:8000/

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
