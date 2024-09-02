from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from os import getenv
import pydub
import soundfile as sf
import speech_recognition as sr
import io
import requests



# Access token for your WhatsApp business account app
whatsapp_token = getenv("WHATSAPP_TOKEN")

# Verify Token defined when configuring the webhook
verify_token = getenv("FACEBOOK_VERIFY_TOKEN")

# Message log dictionary to enable conversation over multiple messages
message_log_dict = {}


# language for speech to text recoginition
# TODO: detect this automatically based on the user's language
LANGUGAGE = "en-US"


class WhatsAppApiView(APIView):
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

    # 2. Create
    def post(self, request, *args, **kwargs):
            # Parse Request body in json format
            body = request.data
            print(f"request body: {body}")

            try:
                # info on WhatsApp text message payload:
                # https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
                if body.get("object"):
                    if (
                        body.get("entry")
                        and body["entry"][0].get("changes")
                        and body["entry"][0]["changes"][0].get("value")
                        and body["entry"][0]["changes"][0]["value"].get("messages")
                        and body["entry"][0]["changes"][0]["value"]["messages"][0]
                    ):
                        handle_whatsapp_message(body)
                    return Response("ok", 200)
                else:
                    # if the request is not a WhatsApp API event, return an error
                    return (
                        Response("Not a WhatsApp API event", 404)
                    )
            # catch all other errors and return an internal server error
            except Exception as e:
                print(f"unknown error: {e}")
                return Response(str(e), 500)
                

def handle_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
    elif message["type"] == "audio":
        audio_id = message["audio"]["id"]
        message_body = handle_audio_message(audio_id)
    response = "Done" #make_openai_request(message_body, message["from"])
    print("1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
    send_whatsapp_message(body, response)       
        
def handle_audio_message(audio_id):
    audio_url = get_media_url(audio_id)
    audio_bytes = download_media_file(audio_url)
    audio_data = convert_audio_bytes(audio_bytes)
    audio_text = recognize_audio(audio_data)
    message = (
    "Please summarize the following message in its original language "
    f"as a list of bullet-points: {audio_text}"
    )
    return message 

def convert_audio_bytes(audio_bytes):
    ogg_audio = pydub.AudioSegment.from_ogg(io.BytesIO(audio_bytes))
    ogg_audio = ogg_audio.set_sample_width(4)
    wav_bytes = ogg_audio.export(format="wav").read()
    audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="int32")
    sample_width = audio_data.dtype.itemsize
    print(f"audio sample_rate:{sample_rate}, sample_width:{sample_width}")
    audio = sr.AudioData(audio_data, sample_rate, sample_width)
    return audio  

def send_whatsapp_message(body, message):
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = "373379749199948" #value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }
    print("222222222222222222222222222222222222222222222222222222222222222222222222222222222222222")
    url = "https://graph.facebook.com/v20.0/" + phone_number_id + "/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp message response: {response.json()}")
    response.raise_for_status()          
   
   
def make_openai_request(message, from_number):
    try:
        message_log = update_message_log(message, from_number, "user")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_log,
            temperature=0.7,
        )
        response_message = response.choices[0].message.content
        print(f"openai response: {response_message}")
        update_message_log(response_message, from_number, "assistant")
    except Exception as e:
        print(f"openai error: {e}")
        response_message = "Sorry, the OpenAI API is currently overloaded or offline. Please try again later."
        remove_last_message_from_log(from_number)
    return response_message   


# get the media url from the media id
def get_media_url(media_id):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    url = f"https://graph.facebook.com/v16.0/{media_id}/"
    response = requests.get(url, headers=headers)
    print(f"media id response: {response.json()}")
    return response.json()["url"]


# download the media file from the media url
def download_media_file(media_url):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    response = requests.get(media_url, headers=headers)
    print(f"first 10 digits of the media file: {response.content[:10]}")
    return response.content


# convert ogg audio bytes to audio data which speechrecognition library can process
def convert_audio_bytes(audio_bytes):
    ogg_audio = pydub.AudioSegment.from_ogg(io.BytesIO(audio_bytes))
    ogg_audio = ogg_audio.set_sample_width(4)
    wav_bytes = ogg_audio.export(format="wav").read()
    audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="int32")
    sample_width = audio_data.dtype.itemsize
    print(f"audio sample_rate:{sample_rate}, sample_width:{sample_width}")
    audio = sr.AudioData(audio_data, sample_rate, sample_width)
    return audio


# run speech recognition on the audio data
def recognize_audio(audio_bytes):
    recognizer = sr.Recognizer()
    audio_text = recognizer.recognize_google(audio_bytes, language=LANGUGAGE)
    return audio_text


# handle audio messages
def handle_audio_message(audio_id):
    audio_url = get_media_url(audio_id)
    audio_bytes = download_media_file(audio_url)
    audio_data = convert_audio_bytes(audio_bytes)
    audio_text = recognize_audio(audio_data)
    message = (
        "Please summarize the following message in its original language "
        f"as a list of bullet-points: {audio_text}"
    )
    return message


# send the response as a WhatsApp message back to the user
# def send_whatsapp_message(body, message):
#     value = body["entry"][0]["changes"][0]["value"]
#     phone_number_id = value["metadata"]["phone_number_id"]
#     from_number = value["messages"][0]["from"]
#     headers = {
#         "Authorization": f"Bearer {whatsapp_token}",
#         "Content-Type": "application/json",
#     }
#     url = "https://graph.facebook.com/v15.0/" + phone_number_id + "/messages"
#     data = {
#         "messaging_product": "whatsapp",
#         "to": from_number,
#         "type": "text",
#         "text": {"body": message},
#     }
#     response = requests.post(url, json=data, headers=headers)
#     print(f"whatsapp message response: {response.json()}")
#     response.raise_for_status()


# create a message log for each phone number and return the current message log
def update_message_log(message, phone_number, role):
    initial_log = {
        "role": "system",
        "content": "You are a helpful assistant named WhatsBot.",
    }
    if phone_number not in message_log_dict:
        message_log_dict[phone_number] = [initial_log]
        message_log = {"role": role, "content": message}
        message_log_dict[phone_number].append(message_log)
        return message_log_dict[phone_number]


# remove last message from log if OpenAI request fails
def remove_last_message_from_log(phone_number):
    message_log_dict[phone_number].pop()

   