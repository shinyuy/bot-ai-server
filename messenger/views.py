from django.http import JsonResponse
import json
from rest_framework.views import APIView
import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from os import getenv


class MessengerApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
         # Parse params from the webhook verification request
        if not request.query_params:  #or not request.query_params.get("hub.verify_token") or not request.query_params.get("hub.challenge"):
            return Response("Credentials not provided", status=status.HTTP_400_BAD_REQUEST)
        else:
            mode = request.query_params.get("hub.mode")
            token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")
            # Check if a token and mode were sent
            if mode and token:
                # Check the mode and token sent are correct
                if mode == "subscribe" and token == getenv("FACEBOOK_VERIFY_TOKEN"):
                    # Respond with 200 OK and challenge token from the request
                    print("WEBHOOK_VERIFIED")
                    return HttpResponse(challenge, content_type='text/plain')
                else:
                    # Responds with '403 Forbidden' if verify tokens do not match
                    print("VERIFICATION_FAILED")
                    return Response("Verification failed", 403)
            else:
                # Responds with '400 Bad Request' if verify tokens do not match
                print("MISSING_PARAMETER")
                return Response("Missing parameters", 400)
            # return Response(getenv("FACEBOOK_VERIFY_TOKEN"), status=status.HTTP_200_OK)

    
    
    def messenger_webhook(request):
        if request.method == 'GET':
            # Verify webhook
            verify_token = 'YOUR_VERIFY_TOKEN'
            if request.GET.get('hub.mode') == 'subscribe' and request.GET.get('hub.verify_token') == verify_token:
                return JsonResponse(int(request.GET.get('hub.challenge')), safe=False)
            else:
                return JsonResponse('Invalid verification token', status=403)

        if request.method == 'POST':
            # Handle incoming messages
            data = json.loads(request.body.decode('utf-8'))
            for entry in data.get('entry'):
                for messaging_event in entry.get('messaging'):
                    if 'message' in messaging_event:
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message']['text']

                        # Send a reply
                        reply_to_user(sender_id, message_text)

            return JsonResponse(status=200)

    def reply_to_user(recipient_id, message_text):
        PAGE_ACCESS_TOKEN = 'YOUR_PAGE_ACCESS_TOKEN'
        message_data = {
            'recipient': {'id': recipient_id},
            'message': {'text': f'You said: {message_text}'}
        }
        requests.post(
            f'https://graph.facebook.com/v11.0/me/messages?access_token={PAGE_ACCESS_TOKEN}',
            json=message_data
        )
