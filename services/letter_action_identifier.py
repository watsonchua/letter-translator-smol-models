from services.client import groq_client, jigsaw_client
from jigsawstack import JigsawStackError


# user_language = "Chinese"

action_extraction_system_prompt =  """
You are a letter reader. Imagine that you are helping someone read a letter.
Read the letter and do the following:
1. Determine if there are any actions needed from the recipient. 
2. If there is no action needed from the recipient, summarise the content in one sentence and prepend it with [INFO].
3. If there are actions needed from the recipient, list down the actions in point forms consisely.

Here are some additional instructions:
- If there is payment to be made, include the amount in the action sentence.
- If there is a deadline, include the deadline in the action sentence.
- If the outstanding balance is 0, do not include the payment in the action sentence.
- GIRO is a payment method in Singapore. If the letter mentions that payment will be deducted via GIRO, take it that payment has been made and there is no action needed.

IMPORTANT:
Give your response in English. Do not add any other preambles or anything else to your response.
"""

chat_system_prompt_template =  """
You are a question and answer assistant for a letter. 
Given the content of the letter, the user's query, and the chat history between you and the user in a different language.
Do the following:
1. Answer the user's query using the content of the letter, and the chat history. Always answer only with the content of the letter.
2. If you don't know, say "I don't know".

IMPORTANT:
Give your response in English. Do not add any other preambles or anything else to your response.

This is the content of the letter:
{context}
"""

action_extraction_user_prompt_template = """
This is the content of the letter:
{letter_content}
"""

letter_extraction_prompts = ["Extract the content of this letter."]

def extract_content(url_to_filepath):
    try:
        ocr_response = jigsaw_client.vision.vocr({"url": url_to_filepath, "prompts" : letter_extraction_prompts})
        letter_text = ocr_response["context"]
    except KeyError as e:
        print(e)
        return None
    except JigsawStackError as e:
        print(f"An error occurred during uploading: {e}")
        return None      

    return letter_text
    

def identify_letter_action(letter_text):    
    model_response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": action_extraction_system_prompt},
            {"role": "user", "content": action_extraction_user_prompt_template.format(letter_content=letter_text)},
        ],
        temperature=0.1,
        max_completion_tokens=512,
        top_p=1,
        # stream=True,
        stream=False,
        stop=None,
    )
    print(letter_text)
    print(model_response)
    model_response_text = model_response.choices[0].message.content
    return model_response_text


def respond_to_query(letter_text, chat_history):
    # Prepare the messages list including system prompt and chat history
    messages = [
        {"role": "system", "content": chat_system_prompt_template.format(context=letter_text)}
    ]
    
    # Add chat history to messages
    messages += chat_history
        
    model_response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=messages,
        temperature=0.1,
        max_completion_tokens=512,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    model_response_text = model_response.choices[0].message.content
    print(model_response_text)
    return model_response_text
