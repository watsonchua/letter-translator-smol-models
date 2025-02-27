from groq import Groq
from dotenv import load_dotenv, find_dotenv
import os

env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")


# TODO: ask llm to extract this better?
ingredient_text = """
'Nutrition Facts Nutrition Facts/Datos de Nutrición\nNutrition Facts\n8 servings per container 8 servings per container/8 raciónes por envase\nServing size 1 cup (68g) Serving size/Tamaño por ración 1 cup / 1 taza (68g)\n8 servings per container\nServing size 1 cup (68g)\nAmount per serving Amount per serving / Cantidad por ración\nCalories Calories / Calorias\n370\nAmount per serving\nCalories\n370\n370\n% Daily Value* % Daily Value*/Valor Diario*\nTotal Fat 5g % Daily Value* Total Fat/Grasa Total 5g 7%\n7%\nSaturated Fat 1g 5% Total Fat 5g 7% Saturated Fat/Grasa Saturada 1g\n5%\nTrans Fat 0g Saturated Fat 1g 3% Trans Fat/Grasa Trans 0g\nCholesterol 0mg 0% Cholesterol/Colesterol 0mg\nTrans Fat 0g\n0%\nSodium 150mg 6% Sodium/Sodio 150mg 6%\nCholesterol 0mg 0%\nTotal Carbohydrate 48g Total Carbohydrate/Carbohidrato Total 48g\n15% 15%\n6%\nDietary Fiber 5g 14% Dietary Fiber/Fibra Dietética 5g\nSodium 150mg\n14%\nTotal Sugars 13g Total Sugars/Azúcares Total 13g\nTotal Carbohydrate 48g\n15%\nIncludes 10g Added Sugars 20% Includes 10g Added Sugars/Incluye 10g azúcares añadidos\nDietary Fiber 5g 14%\n20%\nProtein 12g Protein/Proteínas 12g\nTotal Sugars 13g\nIncludes 10g Added Sugars 20%\nVitamin A 10mcg 20% Vitamin D/Vitamina D 2mcg\n10%\nVitamin C 1mg 100% Calcium/Calcio 210mg\nProtein 12g\n20%\nVitamin D 1mcg 50% Vit. D 2mcg 10% . Calcium 210mg 20% Zinc 7mg\n50%\nVitamin E 2mcg 100% Biotin/Biotina 300mcg 100%\n·\nBiotin 300mcg 100% Zinc 7mg 50%\nRiboflavin 5mcg 75% · The % Daily Value (DV) tells u hr w much ar itrient in a serving of food contributes to a daily diet. 2,000 calories a day is\n* The % Daily Value (DV) tells you how much a nutrient\nused for general nutrition & LOCK\nFolic Acid 200mcg 60% in a serving of food contributes to a daily diet. 2,000\nEl % Valor Diario (VD) le indica cuánto un nutriente en una porción de alimentos contribuye a una dieta diaria. 2,000\nThiamin 2mcg 35% calorías al día se utiliza pacredito chalup general.\ncalories a day is used for general nutrition advice.\nVitamin B12 5mcg 100%\nZinc 7mg 50% Amount/serving % Daily Value* Amount/serving % Daily Value*\nNutrition\nBiotin 300mcg 100% * The % Daily Value\n25% Calcium 50mcg\nTotal Fat 1.2g 1% Total Carbohydrate 50g 24% (DV) tells you\nFacts\nPhosphorus 90mcg 90%\nSaturated Fat 0.2g 2% Dietary Fiber 4g 15%\nhow much a\nnutrient in a\nserving of food\nMagnesium 400mcg 100%\n18 servings per container Trans Fat 0.5g Total Sugars 5g\ncontributes to a\nChromium 75mcg 80%\nServing size Cholesterol 0mg Includes lg Added Sugars\n0% 2% calories a day is\ndaily diet. 2,000\nPotassium 5g 100% Sodium 180mg 8% Protein 22g nutrition advice.\n2 pices (48g)\nused for general\n· The % Daily Value (DV) tells you how much a nutrient\nin a serving of food contributes to a daily diet. 2,000\nCalories Vitamin D 2mcg 10% · Calcium 40mg 3% · Zinc 7mg 50% . Biotin 300mcg 100%\n160\ncalories a day is used for general nutrition advice.\n887577220\nper serving Folic Acid 200mcg 50% · Copper (as sulfate) 30mg 200%"""



system_prompt =  """
You are an allergen detector. Given a list of ingredients and the a list of a user's allergens, find the allergens in the ingredient list and inform the user if any allergens are present. If no allergens are present, inform the user that no allergens were found.

Take note of the following:
1. The allergens and ingredients list are in English. Ignore any non-English text.
2. Do not check just for the allergens, also check for other associated allergens that might trigger the user based on the allergen list.
"""

user_prompt_template = """
These are the user' allergens:
{user_allergens}


This is the ingredient list:
{ingredient_list}
"""


user_allergen_list = ["peanuts", "meat", "potato", "sugar"]

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)
completion = client.chat.completions.create(
    model="gemma2-9b-it",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_template.format(user_allergens="\n".join(user_allergen_list), ingredient_list=ingredient_text)},
    ],
    temperature=0.1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
