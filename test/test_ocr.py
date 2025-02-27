from jigsawstack import JigsawStack
from dotenv import load_dotenv, find_dotenv
import os

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")


jigsawstack = JigsawStack(api_key=os.environ["JIGSAWSTACK_API_KEY"])

result = jigsawstack.vision.vocr({"url": "https://smol-hackathon.s3.ap-southeast-1.amazonaws.com/maths-2.png", "prompt" : ["Describe the image"]})
print(result)
# print(result['context']['sections'][0]['text'])


