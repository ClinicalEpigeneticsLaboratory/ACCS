#### Run locally
```
python -m pip install poetry
python -m poetry install

# Start celery
poetry run python -m celery -A accs_app worker --loglevel=info --concurrency=2 --pool=eventlet

# Start app
poetry run python manage.py runserver
```

#### Run locally using Docker
First create .env file comprising environmental variables:

```
DEBUG=boolean
SECRET_KEY=str
DJANGO_SUPERUSER_PASSWORD=str
DJANGO_SUPERUSER_USERNAME=str
DJANGO_SUPERUSER_EMAIL=str

#POSTGRES
DB_HOST=postgres
DB_USER=str
DB_PASS=str
DB_NAME=str
DB_PORT=int

#RABBITMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=str
RABBITMQ_PASS=str
RABBITMQ_PORT=int

#CLIENT
CLIENT_PORT=int
```

Then to start services, including: database, rabbitmq and django app:

```
docker-compose up
```
