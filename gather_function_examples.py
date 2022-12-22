import json
import time
from ingredient_functions.engine import PromptEngine
from ingredient_functions.prompt import ListingPrompt, DescribingPrompt
from ingredient_functions.prompt.storage import DiskStorage


prompt = ListingPrompt(classifier_word="ingredients")
storage = DiskStorage("data/listing_exploration")
df_ingredients = storage.get(group=str(prompt))


prompt_phrases_dict = {}
groups = df_ingredients.groupby("prompt_phrase")
for group_key in groups.groups.keys():
    group = groups.get_group(group_key)
    prompt_phrases_dict[group_key] = group["value"].tolist()


prompt_2 = DescribingPrompt(classifier_word="purpose of ingredients")
engine = PromptEngine("data/function_exploration")


for recipe, ingredients in prompt_phrases_dict.items():
    time.sleep(3)
    out = engine.prompt(prompt_2, prompt_kwargs={"prompt_phrases_dict": {recipe: ingredients}})