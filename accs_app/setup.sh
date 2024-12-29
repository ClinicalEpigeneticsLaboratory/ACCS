#!/bin/bash
echo "----- Collect static files ------ "
python manage.py collectstatic --noinput

echo "----------- Apply migrations --------- "
python manage.py makemigrations
python manage.py migrate

echo "----------- Add superuser --------- "
python manage.py createsuperuser --no-input

echo "----------- Add superuser --------- "
python -m gunicorn 'accs_app.wsgi' --bind=0.0.0.0:8000 --timeout 60 --workers=2
