#!/bin/bash

rm -rf whoYouApi/migrations
rm db.sqlite3
python manage.py migrate
python manage.py makemigrations whoYouApi
python manage.py migrate whoYouApi
python manage.py loaddata whoYouApi/fixtures/*.json