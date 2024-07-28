cd accs_app/ || exit

echo "----- R cache ------ "
Rscript sesame_requirements.R

echo "----- Start celery ------ "
python3.10 -m celery -A accs_app worker --detach --loglevel=info --concurrency=2

echo "----- Collect static files ------ "
python3.10 manage.py collectstatic --noinput

echo "----------- Apply migrations --------- "
python3.10 manage.py makemigrations
python3.10 manage.py migrate

echo "----------- Add superuser --------- "
python3.10 manage.py createsuperuser --no-input

echo "----------- Start app --------- "
python3.10 py
