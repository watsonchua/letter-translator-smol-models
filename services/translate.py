from services.client import jigsaw_client

# zh for chinese, en for english
def translate_text(text, target_language, current_language):
    try:
        translated_text_response = jigsaw_client.translate({"text": text, "target_language": target_language, "current_language": current_language })
        translated_text_dict = translated_text_response.json()

    except Exception as e:
        print(f"Translation failed because of {str(e)} Returning original text.")
        return text

    return translated_text_dict["translated_text"]