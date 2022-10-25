from ingredient_functions.openai.engine import PromptEngine
from ingredient_functions.openai.prompt import DescribingPrompt, ListingPrompt


engine = PromptEngine("test-session")

# Model API - Listing Prompt
prompt = ListingPrompt(classifier_word="ingredients")
out = engine.prompt(prompt, prompt_kwargs={"prompt_phrases": ["cake", "spaghetti"]})

# Some processing to connect both prompts
prompt_phrases_dict = {}
groups = out.groupby("prompt_phrase")
for group_key in groups.groups.keys():
    group = groups.get_group(group_key)
    prompt_phrases_dict[group_key] = group["value"].tolist()

# Model API - Describing Prompt
prompt_2 = DescribingPrompt(classifier_word="purpose of ingredients")
out_2 = engine.prompt(prompt_2, prompt_kwargs={"prompt_phrases_dict": prompt_phrases_dict})
print(out_2)
