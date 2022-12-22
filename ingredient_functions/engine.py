from enum import Enum
from openai import Completion
from typing import List, Optional
from itertools import repeat

import pandas as pd

from ingredient_functions.prompt.answer_parser import ListParser
from ingredient_functions.prompt.storage import DiskStorage
from ingredient_functions.prompt.template import BasePrompt, DescribingPrompt, ListingPrompt
from ingredient_functions.utils.login import OpenAILogin


class Model(Enum):
    DAVINCI = "text-davinci-003"
    CURIE = "text-curie-001"
    BABBAGE = "text-babbage-001"
    ADA = "text-ada-001"


class PromptEngine:
    """Prompts the OpenAI API with proper timings and slowdowns.

    Args:
        session_id (str): Unique identifier of your prompting. It will create a file based on this ID.
            If given the same ID, it will append the data to any previous runs with this ID.
        remove_repeats (bool): Should the repeats be removed from returns. DOES NOT WORK. #TODO

    For other arguments check: https://beta.openai.com/docs/api-reference/completions
    """

    def __init__(
        self,
        session_id: str,
        remove_repeats: bool = True,
        model: Model = Model.DAVINCI,
        temperature: float = 0.9,
        max_tokens: int = 512,
        n_completions: int = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> None:
        self._session_id = session_id
        self._remove_repeats = remove_repeats
        self._model = model.value
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._n_completions = n_completions
        self._frequency_penalty = frequency_penalty
        self._presence_penalty = presence_penalty

        self._login = OpenAILogin()  # TODO
        self._answer_parser = ListParser()
        self._openai = Completion()
        self._storage = DiskStorage(session_id=session_id)

    @property
    def storage(self):
        return self._storage

    def prompt(self, prompt: BasePrompt, prompt_kwargs: dict = {}, desired_amount: Optional[int] = 100):
        """Prompts the API based on the given args.

        Args:
            prompt: Created prompt. Check `prompt_exploration/prompt/template.py`
            prompt_kwargs: arguments for prompt's `generate` method
            desired_amount: amount of data to be parsed in rows. Mind that one prompt might return more
                than 1 row depending on arguments of it. If None, just keeps prompting if possible.
        """
        group = str(prompt)

        for prompt_arguments in prompt.generate(**prompt_kwargs):
            response = self._ask_prompt(prompt.create(**prompt_arguments))
            for reponse_choice in response["choices"]:
                list_answer = self._answer_parser(reponse_choice["text"])
                dataframe = self._convert_to_pandas(list_answer, prompt=prompt, prompt_arguments=prompt_arguments)

                if not dataframe.empty:
                    self._storage.store(dataframe, group=group)
                else:
                    # TODO
                    pass

            # if desired_amount is not None and len(self._storage) >= desired_amount:
                # break

        # TODO: logging
        print(f"\n\nPrompting finished. Gathered {len(self._storage.get(group=group))} examples!\n\n")

        return self._storage.get(group=group)

    def _ask_prompt(self, prompt: str):
        # TODO: Rate limit seems to not propagate back
        response = self._openai.create(
            prompt=prompt,
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            n=self._n_completions,
            frequency_penalty=self._frequency_penalty,
            presence_penalty=self._presence_penalty,
        )
        return response

    def _convert_to_pandas(self, list_answer: List[str], prompt: BasePrompt, prompt_arguments: dict) -> pd.DataFrame:
        if isinstance(prompt, ListingPrompt):
            length = len(list_answer)
            prompt_phrase = prompt_arguments["prompt_phrase"]

            if length > 0:
                return pd.DataFrame({
                    "value": list_answer,
                    "prompt_phrase": repeat(prompt_phrase, length),
                    "classifier_word": repeat(prompt.classifier_word, length),
                    "amount_to_list": repeat(prompt.amount_to_list, length),
                    "start_text": repeat(prompt.start_text, length),
                })

        elif isinstance(prompt, DescribingPrompt):
            length = len(list_answer)
            prompt_phrase = prompt_arguments["prompt_phrase"]
            items_to_describe = prompt_arguments["items_to_describe"]

            if length > 0 and len(items_to_describe) == length:
                return pd.DataFrame({
                    "value": list_answer,
                    "prompt_phrase": repeat(prompt_phrase, length),
                    "items_to_describe": items_to_describe,
                    "classifier_word": repeat(prompt.classifier_word, length),
                    "amount_to_list": repeat(prompt.amount_to_list, length),
                    "start_text": repeat(prompt.start_text, length),
                    "add_one_word": repeat(prompt.add_one_word, length),
                })

        else:
            raise RuntimeError("Could not recognise prompt.")

        return pd.DataFrame([])  # Return empty in case of conversion errors
