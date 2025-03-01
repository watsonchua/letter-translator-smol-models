from dotenv import load_dotenv, find_dotenv
import os
from groq import Groq

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")

groq_client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

