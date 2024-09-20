from django.http import JsonResponse
import json
from rest_framework.views import APIView
import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from os import getenv
from data_store.vector import vectorize, vector2text, get_chat_completion, get_embeddings
from pgvector.django import CosineDistance
from data_store.models import DataStore

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
            verify_token = getenv('FACEBOOK_VERIFY_TOKEN')
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
    FACEBOOK_PAGE_ACCESS_TOKEN = getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    response_from_ai = make_ai_request(message_text, recipient_id)

    message_data = {
        'recipient': {'id': recipient_id},
        'message': {'text': response_from_ai}
    }
    requests.post(
            f'https://graph.facebook.com/v11.0/me/messages?access_token={FACEBOOK_PAGE_ACCESS_TOKEN}',
            json=message_data
    )


def make_ai_request(message, from_number):
    # query = vectorize(message, 'question')
    query = get_embeddings(message)
    result = ''
    print(query)
    print(result)
    try:
        answers = DataStore.objects.filter(company_website="https://boookit.io")
        print(answers)
        answers_with_distance = answers.annotate(
            distance=CosineDistance("embedding", query)
            ).order_by("distance")[:3]
        for answer in answers_with_distance:  
            if answer.company_website == "https://boookit.io":
                answer_text =  answer.content
                result = result + " " + answer_text
        print(result)        
        res = get_chat_completion(message, result)   
        print(res)   
        return res  
    except DataStore.DoesNotExist:
        return "Sorry, I don't have a response to your query"  
    
    