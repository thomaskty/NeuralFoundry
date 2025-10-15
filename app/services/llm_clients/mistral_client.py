from typing import Optional
from mistralai import Mistral
import os
from fastapi.concurrency import run_in_threadpool
from app.core.config import settings


class LLMClient:
    """
    Thin wrapper around mistralai client.
    The mistralai client is used synchronously, so we call it inside run_in_threadpool
    to avoid blocking the event loop.
    """

    def __init__(self, default_model: str = "mistral-tiny"):

        if not settings.MISTRAL_API_KEY:
            raise RuntimeError("MISTRAL_API_KEY is not set in environment variables")
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)

        self.model=default_model

    def _complete_sync(self, user_message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Synchronous call to mistralai client.chat.complete
        Returns assistant text.
        """
        messages = [{"role": "user", "content": user_message}]
        model_to_use = model or self.model
        resp = self.client.chat.complete(
            model=model_to_use,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 512),
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            presence_penalty=kwargs.get("presence_penalty", 0),
            frequency_penalty=kwargs.get("frequency_penalty", 0),
        )
        # safe extraction
        try:
            return resp.choices[0].message.content
        except Exception as e:
            # expose a readable error if parsing failed
            raise RuntimeError(f"Unexpected Mistral response shape: {e} | raw: {resp}")

    async def generate_reply(self, user_message: str, model: Optional[str] = None, **kwargs) -> str:
        # run the blocking call in a threadpool
        return await run_in_threadpool(self._complete_sync, user_message, model, **kwargs)
