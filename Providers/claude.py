"""OpenRouter coding provider adapter using Claude Sonnet."""
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

SYSTEM_PROMPT = """You are an expert coding assistant. Help the user design, understand, debug
and improve software. Provide clear, correct, maintainable solutions with practical explanations.
Consider edge cases, error handling, and security when they are relevant. Explain the codebase clearly
when the user asks about it.
Your first approach should be to ask and clarify the requirements and plan the approach before and approve the implementation from the user.
Do not claim certainty when the available information is uncertain."""

def _get_client() -> OpenAI:
    """Return a lazily created, shared OpenRouter client."""
    global _client

    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ProviderError("OPENROUTER_API_KEY is not configured.", provider="claude")

        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=0,
        )
    return _client


def generate(prompt: str) -> str:
    """Generate a coding-oriented response for ``prompt``."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ProviderError("Prompt must be a non-empty string.", provider="claude")

    try:
        response = retry_call(
            lambda: _get_client().chat.completions.create(
                model=get_model_id("claude"),
                max_tokens=get_max_tokens("claude"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            ),
            retryable_exceptions=(
                RateLimitError,
                InternalServerError,
                APIConnectionError,
                APITimeoutError,
            ),
            max_retries=get_max_retries("claude"),
            base_backoff=BASE_BACKOFF_SECONDS,
            max_backoff=MAX_BACKOFF_SECONDS,
        )
    except ProviderError as exc:
        raise ProviderError(str(exc), provider="claude") from exc

    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise ProviderError(
            "Claude returned an invalid response.", provider="claude"
        ) from exc

    if not isinstance(text, str) or not text.strip():
        raise ProviderError("Claude returned an empty response.", provider="claude")

    return text.strip()
