# your_app/consumers.py

import socketio
from django.core.asgi import get_asgi_application
import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_api.settings')

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, get_asgi_application())
  
class VoiceCallConsumer(AsyncWebsocketConsumer):
    @sio.event
    async def connect(sid, environ):
        print(f'Client connected: {sid}')
        await sio.emit('message', {'message': 'Connected successfully'}, to=sid)

    @sio.event
    async def disconnect(sid):
        print(f'Client disconnected: {sid}')

    @sio.event
    async def my_event(sid, data):
        print(f"Message from client {sid}: {data}")
        await sio.emit('response', {'data': 'Response from server'}, to=sid)