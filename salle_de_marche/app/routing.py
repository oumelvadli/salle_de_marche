# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/alert_group/', consumers.AlertConsumer.as_asgi()),
]
