import asyncio
import os
import sys
import pyaudio
from google import genai
from google.genai import types
import dotenv

dotenv.load_dotenv()
# --- Configuration ---
# It is best to set this in your terminal: $env:GOOGLE_API_KEY = "key"
API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_ID = "gemini-2.5-flash-native-audio-preview-12-2025"

if not API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1)

# Audio Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000    # Gemini expects 16kHz input
RECEIVE_SAMPLE_RATE = 24000 # Gemini sends 24kHz output
CHUNK_SIZE = 512            # Smaller chunks reduce latency

# Initialize the GenAI Client with v1alpha for Live features
client = genai.Client(
    api_key=API_KEY, 
    http_options={'api_version': 'v1alpha'}
)

async def run_audio_dialog():
    audio_interface = pyaudio.PyAudio()
    
    # Setup Microphone
    mic_stream = audio_interface.open(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=SEND_SAMPLE_RATE,
        input=True, 
        frames_per_buffer=CHUNK_SIZE
    )
    
    # Setup Speakers
    speaker_stream = audio_interface.open(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=RECEIVE_SAMPLE_RATE,
        output=True, 
        frames_per_buffer=CHUNK_SIZE
    )

    # Live API Config for Native Audio
    config = {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": "Puck"}
            }
        }
    }

    print(f"--- Starting Session with {MODEL_ID} ---")
    
    try:
        async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
            print("Connected! Speak into your microphone...")

            async def send_mic_audio():
                """Reads from mic and pushes to the websocket."""
                try:
                    while True:
                        # Read raw bytes from mic
                        data = await asyncio.to_thread(mic_stream.read, CHUNK_SIZE, exception_on_overflow=False)
                        await session.send_realtime_input(
                            audio=types.Blob(data=data, mime_type='audio/pcm;rate=16000')
                        )
                except Exception as e:
                    print(f"Mic Error: {e}")

            async def receive_model_audio():
                """Receives audio responses and plays them through speakers."""
                try:
                    async for message in session.receive():
                        if message.server_content and message.server_content.model_turn:
                            parts = message.server_content.model_turn.parts
                            for part in parts:
                                if part.inline_data:
                                    # Play the raw PCM data immediately
                                    await asyncio.to_thread(speaker_stream.write, part.inline_data.data)
                except Exception as e:
                    print(f"Speaker Error: {e}")

            # Execute both directions simultaneously
            await asyncio.gather(send_mic_audio(), receive_model_audio())

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        # Cleanup hardware resources
        mic_stream.stop_stream()
        mic_stream.close()
        speaker_stream.stop_stream()
        speaker_stream.close()
        audio_interface.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(run_audio_dialog())
    except KeyboardInterrupt:
        print("\nSession ended by user.")
