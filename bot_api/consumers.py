import json
import assemblyai as aai
from channels.generic.websocket import AsyncWebsocketConsumer
from os import getenv
import assemblyai as aai
import aiohttp
  

aai.settings.api_key = "70213737add14c1b9b8827a59a59617b"
ASSEMBLYAI_API_KEY = "70213737add14c1b9b8827a59a59617b"

class TwilioMediaStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection initiation from Twilio.
        """
        await self.accept()   
        print("WebSocket connection accepted from Twilio.")

         # Connect to AssemblyAI WebSocket
        try:
            self.session = aiohttp.ClientSession()
            self.assemblyai_ws = await self.session.ws_connect(
                "wss://api.assemblyai.com/v2/realtime/ws",
                headers={"authorization": ASSEMBLYAI_API_KEY},
            )
            print("Connected to AssemblyAI WebSocket.")
        except Exception as e:
            print(f"Error connecting to AssemblyAI: {e}")
            await self.close()
            return

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if self.assemblyai_ws:
            await self.assemblyai_ws.close()
        print(f"Disconnected: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        
        
        try:
            # Handle bytes_data received from Twilio
            if bytes_data:
                # Decode the bytes_data from Twilio
                twilio_message = json.loads(bytes_data.decode("utf-8"))
                print("Received Twilio message:", twilio_message)  # Debugging log

            # Check if the message contains media data
            if "media" in twilio_message:
                audio_chunk = twilio_message["media"]["payload"]
                print("Audio chunk received:", audio_chunk)  # Debugging log

                # Forward the audio chunk to AssemblyAI
                if self.assemblyai_ws:
                    await self.assemblyai_ws.send_json({"audio_data": audio_chunk})
                    print("Sent audio chunk to AssemblyAI.")
            else:
                print("No media data in Twilio message.")

            # Handle transcription results from AssemblyAI
            if self.assemblyai_ws:
                async for msg in self.assemblyai_ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        transcription_data = json.loads(msg.data)
                        print("Received transcription:", transcription_data.get("text"))
                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        print(f"AssemblyAI WebSocket closed with code: {msg.data}")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"AssemblyAI WebSocket error: {msg.data}")
                    break

        except Exception as e:
            print(f"Error during processing: {e}")



# uvicorn bot_api.asgi:application --host 0.0.0.0 --port 8000 --workers 4