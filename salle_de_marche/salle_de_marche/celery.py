
from celery import Celery
import os
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salle_de_marche.settings')

app = Celery('salle_de_marche')

# Configuration pour utiliser Redis comme broker et backend
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'
app.autodiscover_tasks()




app.conf.update(
    timezone='Africa/Nouakchott',
    beat_schedule={
        'download_and_inject_every_day_at_specific_timee': {
            'task': 'app.tasks.download_and_inject',
            'schedule': crontab(hour=16, minute=6),  # Assurez-vous que c'est l'heure correcte
            # 'args': (16, 16)


        },
    }
)

