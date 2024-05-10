from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salle_de_marche.settings')

app = Celery('salle_de_marche')
app = Celery('salle_de_marche', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


# Configuration pour utiliser Redis comme broker
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'


app.autodiscover_tasks()
