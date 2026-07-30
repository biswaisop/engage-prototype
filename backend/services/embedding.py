import requests
import numpy as np
from typing import List

class HFEmbeddingFunction:
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.url = f"https://router.huggingface.co/hf-inference/models/{model_name}/pipeline/feature-extraction"

    def _embed(self, texts: List[str]):
        payload = texts[0] if len(texts) == 1 else texts

        response = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"inputs": payload}
        )
        if response.status_code != 200:
            print("HF error body:", response.text)
        response.raise_for_status()

        result = response.json()
        if len(texts) == 1:
            result = [result]

        return np.array(result)  # <-- key fix

    def __call__(self, input: List[str]):
        return self._embed(input)

    def embed_query(self, input: str):
        return self._embed([input])[0]

    def embed_documents(self, input: List[str]):
        return self._embed(input)

    def name(self) -> str:
        return "huggingface-custom"