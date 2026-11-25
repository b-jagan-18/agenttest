"""Day 1, step 1: your first LLM call.

Run:  python scripts/hello_llm.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agenttest.llm import DEFAULT_MODEL, ask

print(f"Asking {DEFAULT_MODEL}...\n")
print(ask("In two sentences, explain what a chatbot regression test is."))
