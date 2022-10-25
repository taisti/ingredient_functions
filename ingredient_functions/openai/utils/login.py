import os


class OpenAILogin:
    def __init__(self):
        self._key_name = "OPENAI_API_KEY"
        if self._key_name not in os.environ:
            raise RuntimeError(f"Add {self._key_name} to the Env. Try `export {self._key_name}=sk-...")
