"""OpenRouter discussion provider adapter using ChatGPT."""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import (APIConnectionError, APITimeoutError, InternalServerError, OpenAI, RateLimitError)
from config import (
    BASE_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    get_max_retries,
    get_max_tokens,
    get_model_id,
)
from error import ProviderError, retry_call

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

_client: OpenAI | None = None

SYSTEM_PROMPT = """You are a thoughtful discussion assistant. Help the user explore ideas, clarify reasoning, challenge
assumptions, never hallucinate, never guess, compare perspectives, and arrive at practical conclusions. Be clear, balanced,
and conversational. Do not claim certainty when the available information is uncertain."""

def _get_client() -> OpenAI:
    """Return a lazily created, shared OpenRouter client."""
    global _client

    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ProviderError("OPENROUTER_API_KEY is not configured.", provider="chatgpt")

        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=0,
        )
    return _client

def generate(prompt: str) -> str:
    """Generate a discussion-oriented ChatGPT response for ``prompt``.
    Providers do not print or terminate the application. They return text on
    success and raise ProviderError on failure for brain.py to handle."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ProviderError("Prompt must be a non-empty string.", provider="chatgpt")

    try:
        response = retry_call(
            lambda: _get_client().chat.completions.create(
                model=get_model_id("chatgpt"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=get_max_tokens("chatgpt"),
            ),
            retryable_exceptions=(
                RateLimitError,
                InternalServerError,
                APIConnectionError,
                APITimeoutError,
            ),
            max_retries=get_max_retries("chatgpt"),
            base_backoff=BASE_BACKOFF_SECONDS,
            max_backoff=MAX_BACKOFF_SECONDS,
        )
    except ProviderError as exc:
        raise ProviderError(str(exc), provider="chatgpt") from exc

    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise ProviderError(
            "ChatGPT returned an invalid response.", provider="chatgpt"
        ) from exc

    if not isinstance(text, str) or not text.strip():
        raise ProviderError(
            "ChatGPT returned an empty response.", provider="chatgpt"
        )
    return text.strip()
