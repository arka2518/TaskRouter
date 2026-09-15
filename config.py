"""Central configuration constants for TaskRoute."""

# Retry / timeout settings
# Coding gets more retry attempts because coding requests are usually longer
# and more valuable to complete. Discussion stays more responsive, while the
# general-purpose route gets a middle-ground retry budget.
CODING_MAX_RETRIES = 5
DISCUSSION_MAX_RETRIES = 3
GENERAL_MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
REQUEST_TIMEOUT_SECONDS = 60

# Token limits
# Claude and ChatGPT go through OpenRouter (provider-prefixed slug).
# Sarvam uses its own direct API — plain model ID, no prefix, separate key.
CODING_MAX_TOKENS = 1500
DISCUSSION_MAX_TOKENS = 2000
GENERAL_MAX_TOKENS = 2048

# Target provider model IDs.
# OpenRouter uses the provider-prefixed model slug.
MODEL_IDS = {
    "claude": "anthropic/claude-sonnet-4",
    "chatgpt": "openai/gpt-4o-mini",
    "sarvam": "sarvam-105b",
}


def get_model_id(provider: str) -> str:
    """Return the model ID for a given provider key."""
    try:
        return MODEL_IDS[provider]
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider}") from exc


def get_max_tokens(provider: str) -> int:
    """Return the output-token limit for a provider key."""
    token_limits = {
        "claude": CODING_MAX_TOKENS,
        "chatgpt": DISCUSSION_MAX_TOKENS,
        "sarvam": GENERAL_MAX_TOKENS,
    }
    try:
        return token_limits[provider]
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider}") from exc


def get_max_retries(provider: str) -> int:
    """Return the retry budget for a provider key."""
    retry_limits = {
        "claude": CODING_MAX_RETRIES,
        "chatgpt": DISCUSSION_MAX_RETRIES,
        "sarvam": GENERAL_MAX_RETRIES,
    }
    try:
        return retry_limits[provider]
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider}") from exc
