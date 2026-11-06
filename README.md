# Affordable Housing Finder and Eligibility System

National Diploma project - Lagos State University, Ojo.
Django + SQLite. Five public pages, no public accounts. Live at https://affordablehousing.pythonanywhere.com

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser   # for /admin/ (rule management)

DJANGO_DEBUG=1 python manage.py runserver     # Windows: set DJANGO_DEBUG=1
```

DEBUG is OFF unless `DJANGO_DEBUG=1` is set, so production is safe by default.

## Tests

```bash
python manage.py test eligibility
```

Covers every threshold on both sides (all comparisons are inclusive), invalid
input, database-loaded rules (versions, effective dates, inactive rules),
the income-gap message, and the main views.

## How eligibility works

Eligibility thresholds are stored in the database (`EligibilityRule`) and
executed by the engine - there is no second, hard-coded copy. Edit them in
Django Admin at `/admin/`:

- To change a threshold, ADD a new rule for the scheme with a later
  *effective from* date. The latest active rule that is not in the future is
  used; older versions stay as history.
- A blank parameter means that criterion is not applied.
- All comparisons are inclusive: a value exactly equal to a minimum or
  maximum qualifies.
- The criteria text shown to users is generated from the stored values, so
  the documentation always matches what is executed.

Initial (version 1) rules, all **project-defined assumptions** unless stated
in the rule's source note:

| Scheme | Rule |
|---|---|
| NHF | income 100,000 to 300,000, at least 6 months of NHF contributions (this one follows FMBN's published loan conditions), age 60 or under |
| LagosHOMS | income 343,000 or more, equity of at least 30% of **that property's** price (checked per property), debt-to-income ratio 0.40 or less |
| Rent-to-Own | income 100,000 to 300,000, at least 2 years of Lagos residency, no prior homeownership |

No scheme covers monthly income below 100,000 or from 300,001 to 342,999. The
results page says so ("No scheme currently covers this income band"); the
bands are computed from the stored rules.

## Data handling

The system minimises data, stores no identifiers, and processes inputs
transiently. Age, income and the other answers are personal information and
are processed; they are held in a server-side session record (database) keyed
by a random id in a secure, HttpOnly cookie, for up to one hour. No name,
email, phone number or location is collected. Run
`python manage.py clearsessions` daily to delete expired records. Hosting logs
may record IP addresses, and fonts/some images load from Google Fonts and
Unsplash.

## Deploy on PythonAnywhere (update steps)

1. Upload/replace the changed files, then `pip install -r requirements.txt` (adds Pillow).
2. `python manage.py makemigrations && python manage.py migrate && python manage.py seed_data`
3. `python manage.py createsuperuser`, then `python manage.py collectstatic`
4. Web tab, static files: add `/media/` -> `.../affordable_housing/media`
5. Scheduled task (daily): `cd ~/affordable_housing && ~/.virtualenvs/ahes-venv/bin/python manage.py clearsessions`
6. Reload the web app.

## Structure

- `properties/` - Scheme, Property (image upload, indexed area and price), views, admin
- `eligibility/` - `rules.py` (pure logic), `engine.py` (loads rules from the database), `models.py` (EligibilityRule), `forms.py`, `views.py`, `admin.py`, `tests.py`
- `templates/` - the five pages plus a shared disclaimer
- `static/` - CSS and JS
