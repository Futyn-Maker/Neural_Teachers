import aiohttp

from loguru import logger

from config import HF_TOKEN, HF_MODEL


class Generator:
    def __init__(self, token=HF_TOKEN, model=HF_MODEL):
        self._session = None
        self._token = token
        self._model = model
        self._headers = {"Authorization": f"Bearer {self._token}"}
        self._api_url = "https://api-inference.huggingface.co"
        self._model_url = f"/models/{self._model}"


    async def init_generator(self):
        self._session = aiohttp.ClientSession(self._api_url,
                                              headers=self._headers)


    async def generate(self, prompt=""):
        data = {
            "inputs": f"Преподаватель говорит: {prompt}",
            "parameters": {"max_new_tokens": 150, "top_k": 50, "top_p": 0.95,
                       "do_sample": True},
            "options": {"wait_for_model": True, "use_cache": False}
        }

        logger.debug(f"Request to {self._api_url + self._model_url} with "
                     f"params: {data}")
        async with self._session.post(self._model_url, json=data) as resp:
            text = await resp.json()
        logger.debug(f"Response: {text}")

        quotes = text[0]["generated_text"].split("Преподаватель говорит:")
        if len(quotes) > 2:
            return quotes[1:-1]
        return quotes[1]
