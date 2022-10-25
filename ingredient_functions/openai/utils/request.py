from openai import Completion

from ingredient_functions.openai.utils.constants import DEFAULT_MODEL


def ask_prompt(prompt: str, model: str = DEFAULT_MODEL) -> str:
    return Completion.create(
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=model,
    )["choices"][0]["text"].strip(" \n")
