# your_app/routing.py

from django.urls import re_path
from .consumers import VoiceCallConsumer

websocket_urlpatterns = [
    re_path(r'ws/calls/$', VoiceCallConsumer.as_asgi()),
]
