from services.client import jigsaw_client
from jigsawstack import JigsawStackError

def extract_content(url_to_filepath, prompt_list):
    try:
        ocr_response = jigsaw_client.vision.vocr({"url": url_to_filepath, "prompts" : prompt_list})
        response_text = ocr_response["context"]
    except KeyError as e:
        print(e)
        return None
    except JigsawStackError as e:
        print(f"An error occurred during uploading: {e}")
        return None      

    return response_text