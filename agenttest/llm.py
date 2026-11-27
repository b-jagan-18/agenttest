"""One place to talk to the LLM, so the rest of the code never touches API details."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads GEMINI_API_KEY and GEMINI_MODEL from the .env file

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Create the client once and reuse it. (If it gets garbage-collected,
    the library closes its connection and later calls fail.)"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "paste-your-key-here":
        raise SystemExit(
            "No API key found. Copy .env.example to .env and paste your Gemini key into it."
        )
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=60_000,  # ms: give up on a single hung request after 60s
            # Retry busy/rate-limited/server errors with growing waits (1s, 2s, 4s...).
            retry_options=types.HttpRetryOptions(
                attempts=5, initial_delay=1.0, max_delay=30.0,
                http_status_codes=[408, 429, 500, 502, 503, 504],
            ),
        ),
    )


def ask(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send one prompt, get one text reply. No memory between calls."""
    response = get_client().models.generate_content(model=model, contents=prompt)
    return response.text or ""  # .text is None if the reply was blocked or empty
