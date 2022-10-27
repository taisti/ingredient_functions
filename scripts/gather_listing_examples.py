import json
from ingredient_functions.openai.engine import PromptEngine
from ingredient_functions.openai.prompt import ListingPrompt


with open("./data/1000_przepisow.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)["items"][924:]

engine = PromptEngine("data/listing_exploration")
prompt = ListingPrompt(classifier_word="ingredients")

for recipe in recipes:
    out = engine.prompt(prompt, prompt_kwargs={"prompt_phrases": [recipe["title"]]})