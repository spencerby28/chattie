from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
load_dotenv()
def generate_speech(text):
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    audio = elevenlabs.text_to_speech.create_previews(voice_id="ie8fnMAIld30LflH5Nho", text=text)
    base64_audio = audio.previews[0].audio_base_64


    with open("output.mp3", "wb") as f:
        f.write(base64_audio)
    return base64_audio

generate_speech("Hello, how are you?")