echo "----- Start celery ------ "
python3.10 -m celery --app=accs_app.celery worker --pool=prefork --logfile="celery.log" --autoscale=3,1 &

echo "----- Collect static files ------ "
python3.10 manage.py collectstatic --noinput

echo "----------- Apply migrations --------- "
python3.10 manage.py makemigrations
python3.10 manage.py migrate

echo "----------- Add superuser --------- "
python3.10 manage.py createsuperuser --no-input

echo "----------- Start app --------- "
python3.10 -m gunicorn 'accs_app.wsgi' --bind=0.0.0.0:8000
