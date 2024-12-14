from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import speech_to_text, text_to_speech
from data_store.vector import vectorize, vector2text, get_chat_completion, get_embeddings
from data_store.models import DataStore
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from pgvector.django import CosineDistance
from rest_framework import status
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Say, Start, Stream
from twilio.rest import Client
from os import getenv

WEBSOCKET_URL = "https://da52-154-72-160-1.ngrok-free.app"

account_sid = getenv("TWILIO_ACCOUNT_SID")
auth_token = getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)


class TwilioCallWebhooksApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Returns TwiML to Twilio to start a media stream to your webhook.
        """
        response = VoiceResponse()
        start = Start()
        response.say("Your call is being streamed for real-time transcription.")
        start.stream(name='Calls', url="wss://da52-154-72-160-1.ngrok-free.app/ws/calls/")
        response.append(start)
        response.say('The stream has started.')
        # return HttpResponse(str(response), content_type="text/xml")
        return HttpResponse(str(response), content_type="text/xml")
        
        