from jigsawstack import JigsawStack
from dotenv import load_dotenv, find_dotenv
import os

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")


jigsawstack = JigsawStack(api_key=os.environ["JIGSAWSTACK_API_KEY"])
# bucket_name = "https://smol-hackathon.s3.ap-southeast-1.amazonaws.com/"
# # object_name = "maths-2.png"
# object_name = "scam1-2020.png"

# result = jigsawstack.vision.vocr(
#     {
#         "url": f"{bucket_name}{object_name}", 
#         "prompt" : ["Read the letter and summarise it in one sentence on the actions to be taken.", "Translate the results to Chinese"]
#         }
#     )
# print(result)
# # print(result['context']['sections'][0]['text'])

result = jigsawstack.vision.vocr(
    {
        "url": "https://api.telegram.org/file/bot7611287920:AAHlXWIvBuP0DpOlEdtIkCICE6xjge_FbhE/photos/file_18.jpg",
        "prompt" : ["Extract the content of the letter."]
    }
)

print(result)