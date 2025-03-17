from jigsawstack import JigsawStack
from dotenv import load_dotenv, find_dotenv
import os

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")


jigsawstack = JigsawStack(api_key=os.environ["JIGSAWSTACK_API_KEY"])

result = jigsawstack.vision.vocr(
    {
        "url": "path_to_your_image.jpg",
        "prompt" : ["Extract the content of the letter."]
    }
)

print(result)