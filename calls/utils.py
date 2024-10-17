from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from google.cloud import speech_v1p1beta1 as speech, texttospeech
import json


class VoiceCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        audio_base64 = data['audio']

        # Decode the audio file
        audio_content = base64.b64decode(audio_base64)

        # Process the audio - Convert speech to text
        text = self.speech_to_text(audio_content)

        # Process text with chatbot (dummy response here)
        chatbot_response = f"Hello, you said: {text}"

        # Convert chatbot response to speech
        audio_response = self.text_to_speech(chatbot_response)

        # Send back audio response to frontend
        await self.send(text_data=json.dumps({
            'audio': base64.b64encode(audio_response).decode('utf-8')
        }))

def speech_to_text(audio_content):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript



def text_to_speech(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content
