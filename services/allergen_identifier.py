from services.ocr import extract_content
from services.client import groq_client

system_prompt =  """
You are an allergen detector. Given a list of ingredients and the a list of a user's allergens, find the allergens in the ingredient list and inform the user if any allergens are present. If no allergens are present, inform the user that no allergens were found.

Take note of the following:
1. The allergens and ingredients list are in English. Ignore any non-English text.
2. Do not check just for the allergens, also check for other associated allergens that might trigger the user based on the allergen list.
"""

user_prompt_template = """
These are the user's allergens:
{user_allergens}


This is the ingredient list:
{ingredient_list}
"""

def identify_allergens(allergen_list, ingredient_text):
    allergen_prompt = user_prompt_template.format(user_allergens="\n-".join(allergen_list), ingredient_list=ingredient_text)
    print(allergen_prompt)
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": allergen_prompt},
        ],
        temperature=0.1,
        max_completion_tokens=1024,
        top_p=1,
        # stream=True,
        stream=False,
        stop=None
    )

    print(response)
    identified_allergens = response.choices[0].message.content
    return identified_allergens

# for chunk in completion:
#     print(chunk.choices[0].delta.content or "", end="")
