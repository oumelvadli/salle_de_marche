from __future__ import absolute_import, unicode_literals

# Cela permettra de s'assurer que l'application est toujours importée lors du démarrage de Django
from .celery import app as celery_app

__all__ = ('celery_app',)
