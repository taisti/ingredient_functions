from abc import abstractmethod
from dataclasses import dataclass
from more_itertools import ichunked
from re import escape
from typing import Dict, Iterable, List, Union


@dataclass(frozen=True)
class BasePrompt:

    @abstractmethod
    def create(self) -> str:
        """Create the prompt."""

    @abstractmethod
    def generate(self) -> Iterable[dict]:
        """Yield multiple inputs for prompts."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Current prompt version."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}_{self.version}"


@dataclass(frozen=True)
class ListingPrompt(BasePrompt):
    """Generates prompts as below.

    "List `amount_to_list` `classifier_word` of `prompt_phrases[i]`:`start_text`"

    Example: List 10 ingredients of cake:\\n1.
    """
    classifier_word: str
    amount_to_list: str = "10"
    start_text: str = "\n1."

    def create(self, prompt_phrase: str) -> str:
        return f"List {self.amount_to_list} {self.classifier_word} of {prompt_phrase}:{self.start_text}"

    def generate(self, prompt_phrases: List[str]) -> Iterable[dict]:
        for prompt_phrase in prompt_phrases:
            yield {"prompt_phrase": prompt_phrase}

    @property
    def version(self) -> str:
        return "v1"


@dataclass(frozen=True)
class DescribingPrompt(BasePrompt):
    """Generates prompts as below.

    "Describe `classifier_word` in a list:
    1. `items_to_describe[i][0] from key_of:items_to_describe[i]`
    2. `items_to_describe[i][1] from key_of:items_to_describe[i]` ...
    "

    Example: Describe functions of ingredients of cake in a list:
        1. flour...
    """
    classifier_word: str
    amount_to_list: str = "10"
    start_text: str = "\n1."
    add_one_word: bool = True

    def create(self, prompt_phrase: str, items_to_describe: List[str]) -> str:
        if self.add_one_word:
            header = f"Describe {self.classifier_word} in a list in one word:"
        else:
            header = f"Describe {self.classifier_word} in a list:"

        item_list = "\n".join(
            [f"{i}. {item} from {prompt_phrase}" for i, item in enumerate(items_to_describe, start=1)]
        )

        return f"{header}\n{item_list}{self.start_text}"

    def generate(self, prompt_phrases_dict: Dict[str, List[str]]) -> Iterable[dict]:
        amount_to_list = self._convert_to_int()
        for prompt_phrase, items_seq in prompt_phrases_dict.items():
            for items in ichunked(items_seq, n=amount_to_list):
                yield {"prompt_phrase": prompt_phrase, "items_to_describe": list(items)}

    def _convert_to_int(self) -> int:
        try:
            return int(self.amount_to_list)
        except ValueError:
            return 10

    @property
    def version(self) -> str:
        return "v1"
