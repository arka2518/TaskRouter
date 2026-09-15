"""Sarvam AI provider adapter for general-purpose tasks."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI, TooManyRequestsError
from sarvamai.core.api_error import ApiError

from config import (
    BASE_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    get_max_retries,
    get_max_tokens,
    get_model_id,
)
from error import ProviderError, retry_call

# Resolve .env from the project directory so standalone provider tests work
# regardless of the caller's current working directory.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

_client: SarvamAI | None = None

SYSTEM_PROMPT = """You are a capable general-purpose AI assistant. Answer questions clearly and accurately
across a wide range of topics. Give useful, practical responses, explain important reasoning, and acknowledge
uncertainty when the available information is incomplete."""

class _RetryableSarvamServerError(Exception):
    """Internal marker for retryable Sarvam 5xx API failures."""

def _get_client() -> SarvamAI:
    """Return a lazily created, shared Sarvam AI client."""
    global _client

    if _client is None:
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            raise ProviderError("SARVAM_API_KEY is not configured.", provider="sarvam")

        _client = SarvamAI(
            api_subscription_key=api_key,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    return _client

def _request(prompt: str):
    """Call Sarvam and mark server errors as retryable for retry_call()."""
    try:
        return _get_client().chat.completions(
            model=get_model_id("sarvam"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=get_max_tokens("sarvam"),
            reasoning_effort=None,
        )
    except ApiError as exc:
        if getattr(exc, "status_code", None) is not None and exc.status_code >= 500:
            raise _RetryableSarvamServerError(str(exc)) from exc
        raise


def generate(prompt: str) -> str:
    """Generate a general-purpose response for ``prompt``."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ProviderError("Prompt must be a non-empty string.", provider="sarvam")

    try:
        response = retry_call(
            lambda: _request(prompt),
            retryable_exceptions=(TooManyRequestsError, _RetryableSarvamServerError),
            max_retries=get_max_retries("sarvam"),
            base_backoff=BASE_BACKOFF_SECONDS,
            max_backoff=MAX_BACKOFF_SECONDS,
        )
    except ProviderError as exc:
        raise ProviderError(str(exc), provider="sarvam") from exc

    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise ProviderError(
            "Sarvam returned an invalid response.", provider="sarvam"
        ) from exc

    if not isinstance(text, str) or not text.strip():
        raise ProviderError("Sarvam returned an empty response.", provider="sarvam")

    return text.strip()
