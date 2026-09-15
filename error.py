"""Shared error handling and retry logic for all providers."""
import time
import random
from typing import Callable, Type, Tuple, Any

class ProviderError(Exception):
    """Base exception raised by providers on non-retryable failures.
    All provider generate() methods should raise this (or a subclass) on failure
    so brain.py can catch a single exception type"""
    def __init__(self, message: str, provider: str | None = None):
        self.provider = provider
        super().__init__(message)

def is_retryable_error(exc: Exception, retryable_types: Tuple[Type[Exception], ...]) -> bool:
    """Check if an exception is in the retryable set for a given provider."""
    return isinstance(exc, retryable_types)

def retry_call(
    func: Callable[[], Any],
    retryable_exceptions: Tuple[Type[Exception], ...],
    max_retries: int = 3,
    base_backoff: float = 1.0,
    max_backoff: float = 30.0) -> Any:
    """Execute a function with exponential backoff retry on specified exceptions.
    Args:
        func: Zero-argument callable to execute.
        retryable_exceptions: Exception types that trigger a retry.
        max_retries: Maximum number of retry attempts (default 3).
        base_backoff: Initial backoff in seconds (default 1.0).
        max_backoff: Cap on backoff in seconds (default 30.0).
    Returns:
        The return value of func() on success.
    Raises:
        ProviderError: If all retries exhausted or a non-retryable exception occurs."""
    attempt = 0
    while True:
        try:
            return func()
        except retryable_exceptions as e:
            attempt += 1
            if attempt > max_retries:
                raise ProviderError(f"Max retries ({max_retries}) exceeded: {e}") from e

            # Exponential backoff with jitter
            backoff = min(base_backoff * (2 ** (attempt - 1)), max_backoff)
            jitter = random.uniform(0, backoff * 0.1)
            time.sleep(backoff + jitter)
        except Exception as e:
            # Non-retryable: wrap and raise immediately
            raise ProviderError(f"Provider error: {e}") from e