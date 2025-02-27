
import os
from groq import Groq
from dotenv import load_dotenv, find_dotenv
import os

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# filename = os.path.dirname(__file__) + "/audio.m4a"
filename = "/mnt/c/Users/watso/Documents/Sound Recordings/cant_eat_meat.m4a"

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="distil-whisper-large-v3-en",
      response_format="verbose_json",
    )
    print(transcription.text)
      