"""Anthropic client construction plus a small retry/backoff wrapper.

Kept dependency-light: the only third-party import is the `anthropic` SDK, and it
is imported lazily so `--help` and schema validation work without the SDK or an
API key present.
"""

from __future__ import annotations

import os
import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class MissingAPIKeyError(RuntimeError):
    """Raised when ANTHROPIC_API_KEY is required but not set."""


def build_client() -> "object":
    """Construct an Anthropic client, failing clearly if the key is absent.

    Returns an ``anthropic.Anthropic`` instance. The return type is left loose so
    this module imports without the SDK installed.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise MissingAPIKeyError(
            "ANTHROPIC_API_KEY is not set.\n"
            "The eval harness calls the Anthropic API to run and grade skills.\n"
            "Export a key before running, e.g.:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
        )
    import anthropic  # lazy import

    return anthropic.Anthropic()


def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> T:
    """Call ``fn`` with exponential backoff on transient API errors.

    Retries rate limits (429), server errors (>=500), and connection errors.
    Client errors (4xx other than 429) are raised immediately — retrying them
    never helps. The SDK already retries internally; this wraps whole eval calls
    so a transient blip doesn't abort a long run.
    """
    import anthropic  # lazy import

    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except anthropic.RateLimitError as exc:
            last_exc = exc
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                last_exc = exc
            else:
                raise
        except anthropic.APIConnectionError as exc:
            last_exc = exc

        if attempt < max_attempts - 1:
            delay = min(base_delay * (2**attempt) + random.uniform(0, 1), max_delay)
            time.sleep(delay)

    assert last_exc is not None  # loop ran at least once
    raise last_exc
