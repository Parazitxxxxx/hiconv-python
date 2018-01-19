# About
This is implementation of simple invitations sending mechanism on Django framework.
Project use a simple auth and django forms for invite new users.
For run this example you need use the Docker or local env based on Python v3.5

# How to run project

## Using Docker
```
docker-compose build
docker-compose up
```

## Using local env
```
pip install -r requirements.txt

DJANGO_SETTINGS_MODULE=invitations.settings.dev ./invitations/manage.py migrate --noinput

DJANGO_SETTINGS_MODULE=invitations.settings.dev python ./invitations/manage.py inituser

DJANGO_SETTINGS_MODULE=invitations.settings.dev python ./invitations/manage.py runserver 0.0.0.0:8000
````

# Use project
Then you can open your localhost with 8000 port in web browser:

`http://localhost:8000/`
