from services.groq_client import groq_client
from services.ocr import OCR

user_language = "Chinese"

action_extraction_system_prompt =  """
You are a letter reader. Imagine that you are helping someone read a letter in a foreign language.
Read the letter and do the following:
1. Determine if there are any actions needed from the recipient. 
2. If there is no action needed from the recipient, summarise the content in one sentence and prepend it with [INFO].
3. If there are actions needed from the recipient, list down each action in point forms with the format: "action by deadline" concisely. If there are no deadlines specified, just list the actions.
4. Translate the action or summary into the user's native language.
5. If there is no action needed, add that to the translation.

Here are some additional instructions:
- If there is payment to be made, include the amount in the action sentence.
- If there is a deadline, include the deadline in the action sentence.
- If the outstanding balance is 0, do not include the payment in the action sentence.
- GIRO is a payment method in Singapore. If the letter mentions that payment will be deducted via GIRO, take it that payment has been made and there is no action needed.

Return your answer in the following format.
Content: actions_needed_or_summary

Translation: translation_of_actions_needed_or_summary
"""

chat_system_prompt_template =  """
You are a question and answer assistant for a letter. 
Given the content of the letter, the user's query in {user_language}, and the chat history between you and the user in a different language.
Do the following:
1. Translate the user's query into the language of the letter.
2. Answer the user's query using the content of the letter, and the chat history. Always answer only with the content of the letter.
3. If you don't know, say I don't know in {user_language}.
4. Translate your answer into {user_language}.

Respond with the translated answer only. Do not add any other preambles or anything else to your response.

This is the content of the letter:
{context}
"""

action_extraction_user_prompt_template = """
The recipient's language is {user_language}.

This is the content of the letter:
{letter_content}
"""

letter_extraction_prompts = ["Extract the content of this letter."]
ocr = OCR(prompts=letter_extraction_prompts)


def extract_content(letter_image, letter_filename):
    letter_text = ocr.parse(letter_image, letter_filename)
    if letter_text is None:
        return "There was an error parsing the image."
    return letter_text

def identify_letter_action(letter_text):    
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": action_extraction_system_prompt},
            {"role": "user", "content": action_extraction_user_prompt_template.format(letter_content=letter_text, user_language=user_language)},
        ],
        temperature=0.1,
        max_completion_tokens=512,
        top_p=1,
        # stream=True,
        stream=False,
        stop=None
    )
    print(letter_text)
    print(response)
    model_response = response.choices[0].message.content
    return model_response


def respond_to_query(letter_text, chat_history):
    # Prepare the messages list including system prompt and chat history
    messages = [
        {"role": "system", "content": chat_system_prompt_template.format(context=letter_text, user_language=user_language)}
    ]
    
    # Add chat history to messages
    # for message in chat_history:
    #     messages.append({"role": message["role"], "content": message["content"]})
    messages += chat_history
    
    # Add the current query from user
    # messages.append({"role": "user", "content": f"Letter content: {letter_text}\n\nMy question: {query}"})
    
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=messages,
        temperature=0.1,
        max_completion_tokens=512,
        top_p=1,
        stream=False,
        stop=None
    )
    
    model_response = response.choices[0].message.content
    return model_response
