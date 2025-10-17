# app/services/llm_clients/ollama_client.py
from typing import Optional
import httpx
from fastapi.concurrency import run_in_threadpool
from app.core.config import settings


class LLMClient:
    """
    Wrapper around Ollama API for local LLM inference.
    Install Ollama from https://ollama.ai and run: ollama pull llama3.1
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
        self.model = settings.DEFAULT_LLM_MODEL

    def _complete_sync(self, user_message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Synchronous call to Ollama API.
        """
        model_to_use = model or self.model

        payload = {
            "model": model_to_use,
            "prompt": user_message,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_tokens", 512),
            }
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")

    async def generate_reply(self, user_message: str, model: Optional[str] = None, **kwargs) -> str:
        return await run_in_threadpool(self._complete_sync, user_message, model, **kwargs)