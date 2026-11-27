"""One place to talk to the LLM, so the rest of the code never touches API details."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai

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
    return genai.Client(api_key=api_key)


def ask(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send one prompt, get one text reply. No memory between calls."""
    response = get_client().models.generate_content(model=model, contents=prompt)
    return response.text or ""  # .text is None if the reply was blocked or empty
