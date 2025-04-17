from functools import wraps
import logging
import os
import time
from typing import Any, Callable, Optional, TypeVar

from utils.excpetions import RateLimitException

logger = logging.getLogger(__name__)

def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Environment variable '{key}' is not set")
    return value

T = TypeVar("T")

def with_exponential_backoff(
    max_retries: int = 5, base_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = base_delay
            last_exception: Optional[RateLimitException] = None

            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except RateLimitException as e:
                    last_exception = e
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}): {e}"
                        f"in {func.__name__}. Retrying in {delay:.2f}s..."
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}.")
                        last_exception = RateLimitException(f"Max retries exceeded for {func.__name__}.")

            assert last_exception is not None, "Loop finished without success or RateLimitException"

            raise last_exception

        return wrapper
    return decorator