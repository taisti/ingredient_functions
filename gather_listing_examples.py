import json
import time
from ingredient_functions.engine import PromptEngine
from ingredient_functions.prompt import ListingPrompt


with open("./data/1000_przepisow.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)["items"]

engine = PromptEngine("data/listing_exploration")
prompt = ListingPrompt(classifier_word="ingredients")


for recipe in recipes:
    time.sleep(3)
    out = engine.prompt(prompt, prompt_kwargs={"prompt_phrases": [recipe["title"]]})