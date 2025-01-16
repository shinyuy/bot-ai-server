"""
ASGI config for bot_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_api.settings')

# application = get_asgi_application()




# asgi.py  

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from .consumers import TwilioMediaStreamConsumer, TranscriptionConsumer
   
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_api.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([  
            path("ws/calls/", TwilioMediaStreamConsumer.as_asgi()),  # WebSocket route
            path('ws/transcribe/', TranscriptionConsumer.as_asgi()),
        ])
    ),
})

