release: python manage.py makemigrations
release: python manage.py migrate
release: python manage.py loaddata data.json
web: gunicorn ProdLogs.wsgi