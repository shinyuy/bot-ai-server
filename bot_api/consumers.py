import json
import assemblyai as aai
from channels.generic.websocket import AsyncWebsocketConsumer
from os import getenv
import assemblyai as aai
import aiohttp
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel
import asyncio
import numpy as np
from time import time
import subprocess
  


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
                headers={"authorization": getenv('ASSEMBLY_AI_API_KEY')},
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


BYTES_PER_SEC = 32000  # Example value; adjust based on your setup

async def start_ffmpeg_decoder():
    """
    Starts the ffmpeg process to decode incoming audio chunks.
    """
    return await asyncio.create_subprocess_exec(
        "ffmpeg", "-f", "webm", "-i", "pipe:0", "-f", "s16le", "-ar", "16000", "-ac", "1", "pipe:1",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

class TranscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connection opened.")
        self.ffmpeg_process = await start_ffmpeg_decoder()
        self.pcm_buffer = bytearray()
        self.stdout_reader_task = asyncio.create_task(self.ffmpeg_stdout_reader())
        self.full_transcription = ""

    async def disconnect(self, close_code):
        print("WebSocket connection closed.")
        # Clean up ffmpeg process and reader task
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
            except:
                pass
            self.stdout_reader_task.cancel()
            try:
                self.ffmpeg_process.stdout.close()
            except:
                pass
            self.ffmpeg_process.wait()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Pass received audio data to ffmpeg stdin
            try:
                self.ffmpeg_process.stdin.write(bytes_data)
                self.ffmpeg_process.stdin.flush()
            except Exception as e:
                print(f"Error writing to ffmpeg stdin: {e}")

    async def ffmpeg_stdout_reader(self):
        """
        Reads decoded PCM data from ffmpeg stdout, processes it, and sends transcription results.
        """
        loop = asyncio.get_event_loop()
        beg = time()

        while True:
            try:
                elapsed_time = int(time() - beg)
                beg = time()
                chunk = await loop.run_in_executor(None, self.ffmpeg_process.stdout.read, BYTES_PER_SEC * elapsed_time)
                if not chunk:
                    chunk = await loop.run_in_executor(None, self.ffmpeg_process.stdout.read, 4096)
                    if not chunk:
                        print("FFmpeg stdout closed.")
                        break

                self.pcm_buffer.extend(chunk)

                if len(self.pcm_buffer) >= BYTES_PER_SEC:
                    # Convert int16 -> float32
                    pcm_array = np.frombuffer(self.pcm_buffer, dtype=np.int16).astype(np.float32) / 32768.0
                    self.pcm_buffer = bytearray()

                    # Process PCM data (transcription logic)
                    transcription = "Sample Transcription Text"  # Replace with actual transcription logic
                    self.full_transcription += transcription

                    # Send transcription result back to the frontend
                    await self.send(text_data=json.dumps({
                        "transcription": transcription,
                        "buffer": self.full_transcription
                    }))

            except Exception as e:
                print(f"Exception in ffmpeg_stdout_reader: {e}")
                break

        print("Exiting ffmpeg_stdout_reader...")


    
    
    
    
    
    
    
    
    
    # async def connect(self):
    #     # Initialize Faster-Whisper model
    #     self.model = WhisperModel("large-v2", device="cpu")
    #     await self.accept()

    # async def disconnect(self, close_code):
    #     pass

    # async def receive(self, text_data=None, bytes_data=None):
    #     if bytes_data:
    #         try:
    #             # Convert received binary data to a NumPy array
    #             audio_data = np.frombuffer(bytes_data, dtype=np.int16).astype(np.float32) / 32768.0

    #             # Use Faster-Whisper to transcribe audio
    #             segments, _ = self.model.transcribe(audio_data)

    #             # Combine transcription results into a single string
    #             transcription = " ".join(segment.text for segment in segments)

    #             # Send transcription back to the frontend
    #             await self.send(text_data=json.dumps({"text": transcription}))

    #         except Exception as e:
    #             # Handle any errors and send error message to the frontend
    #             await self.send(text_data=json.dumps({"error": str(e)}))
        
        
        
        # if bytes_data:
        #     # Process audio data chunk
        #     segments, _ = self.model.transcribe(bytes_data, beam_size=5)
        #     for segment in segments:
        #         await self.send(json.dumps({
        #             "start": segment.start,
        #             "end": segment.end,
        #             "text": segment.text
        #         }))
