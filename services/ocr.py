from services.client import jigsaw_client
import json
from jigsawstack import JigsawStackError

def extract_content(url_to_filepath, prompt_list):
    try:
        ocr_response = jigsaw_client.vision.vocr({"url": url_to_filepath, "prompts" : prompt_list})
        # print(ocr_response.json())
        ocr_response_dict = ocr_response.json() 
        response_text = ocr_response_dict["context"]
    except KeyError as e:
        print(e)
        # return everything except the sections ,width, height
        response_text = json.loads({k:v for k,v in ocr_response_dict.items() if k not in ["sections", "width", "height", "success", "tags"]})

    except JigsawStackError as e:
        print(f"An error occurred during uploading: {e}")
        return None      

    return response_text