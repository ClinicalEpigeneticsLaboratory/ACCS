#!/bin/bash
echo "----- Start celery ------ "
python3.10 -m celery --app=accs_app.celery worker --pool=eventlet --logfile="celery.log" --autoscale=3,1 -E &

echo "----- Collect static files ------ "
python3.10 manage.py collectstatic --noinput

echo "----------- Apply migrations --------- "
python3.10 manage.py makemigrations
python3.10 manage.py migrate

echo "----------- Add superuser --------- "
python3.10 manage.py createsuperuser --no-input

echo "----------- Add superuser --------- "
if [[ -n "$SSL_CERT" && -n "$SSL_KEY" ]]; then
  echo "Running gunicorn with cert/key files"
  python3.10 -m gunicorn 'accs_app.wsgi' --bind=0.0.0.0:8000 --certfile=/etc/ssl/certs/$SSL_CERT --keyfile=/etc/ssl/certs/$SSL_KEY

else
  echo "Files cert/key not available"
  python3.10 -m gunicorn 'accs_app.wsgi' --bind=0.0.0.0:8000
fi
