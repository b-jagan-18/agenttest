"""Day 2: generate test personas and let them chat with the QuickBite bot.

Run:  python scripts/day2_run.py            (3 personas)
      python scripts/day2_run.py 5          (5 personas)

Transcripts are printed and saved to runs/<timestamp>.json.
Day 3 adds the LLM judge that reads them and reports rule violations.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

from agenttest.personas import generate_personas
from agenttest.runner import run_conversation, save_transcripts
from support_bot import BOT_DESCRIPTION, SupportBot


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"Generating {n} personas...\n")
    personas = generate_personas(BOT_DESCRIPTION, n=n)

    transcripts = []
    for i, persona in enumerate(personas, 1):
        print(f"[{i}/{len(personas)}] Chatting as {persona.name} (tests: {persona.attacks_rule})...")
        t = run_conversation(persona, SupportBot)
        transcripts.append(t)
        print(t.pretty(), "\n")

    print(f"Saved to {save_transcripts(transcripts, ROOT / 'runs')}")


if __name__ == "__main__":
    main()
