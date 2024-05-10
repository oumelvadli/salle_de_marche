#!/bin/bash

set -e 

source /env/bin/activate

if [$1 == 'gunicorn']; then 
    exec gunicorn salle_de_marche.wsgi.py:application -b 0.0.0.0:8000 
else 
    exec python manage.py runserver 0.0.0.0:8000
fi 
export PATH="salle_de_marche/venv/Scriptscelery.exe:$PATH"
