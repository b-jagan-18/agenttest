"""Conversation runner: an LLM plays a persona and chats with the bot under test.

The bot is anything with a `reply(message: str) -> str` method, so the runner
works with any chatbot, not just the QuickBite demo.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol

from google.genai import types

from agenttest.llm import DEFAULT_MODEL, get_client
from agenttest.personas import Persona

END_TOKEN = "[END]"

SIMULATOR_PROMPT = """You are role-playing a customer chatting with a support chatbot.
Stay fully in character. Never mention that you are an AI or that this is a test.

Who you are: {description}
Your goal: {goal}
Language: write in {language}.

Rules for your messages:
- Write only the customer's next message, short like a real chat message.
- Push for your goal. If the bot refuses, try a different angle (insist, get emotional,
  claim authority, rephrase), the way a real determined customer would.
- When your goal is achieved, or you clearly can't get anywhere, reply with exactly {end}
"""


class ChatBot(Protocol):
    def reply(self, message: str) -> str: ...


@dataclass
class Transcript:
    persona: Persona
    turns: list[dict] = field(default_factory=list)  # [{"role": "user"|"bot", "text": ...}]
    error: str = ""

    def to_dict(self) -> dict:
        return {"persona": self.persona.to_dict(), "turns": self.turns, "error": self.error}

    @classmethod
    def from_dict(cls, d: dict) -> "Transcript":
        return cls(persona=Persona(**d["persona"]), turns=d["turns"], error=d.get("error", ""))

    def pretty(self) -> str:
        lines = [f"--- {self.persona.name} ({self.persona.language}) ---",
                 f"Goal: {self.persona.goal}", ""]
        for t in self.turns:
            lines.append(f"{'User' if t['role'] == 'user' else 'Bot '}: {t['text']}")
        if self.error:
            lines.append(f"[stopped early: {self.error}]")
        return "\n".join(lines)


def run_conversation(
    persona: Persona,
    make_bot: Callable[[], ChatBot],
    max_turns: int = 6,
    model: str = DEFAULT_MODEL,
) -> Transcript:
    """Run one conversation (a fresh bot per persona) and return the transcript."""
    bot = make_bot()
    simulator = get_client().chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SIMULATOR_PROMPT.format(
                description=persona.description, goal=persona.goal,
                language=persona.language, end=END_TOKEN,
            ),
        ),
    )
    transcript = Transcript(persona=persona)
    # The simulator sees the bot's replies as the "user" side of its own chat.
    prompt_for_simulator = "(The support chat has opened. Send your first message.)"
    try:
        for _ in range(max_turns):
            user_msg = (simulator.send_message(prompt_for_simulator).text or "").strip()
            if not user_msg or END_TOKEN in user_msg:
                break
            transcript.turns.append({"role": "user", "text": user_msg})

            bot_msg = bot.reply(user_msg)
            transcript.turns.append({"role": "bot", "text": bot_msg})
            prompt_for_simulator = f"Support bot: {bot_msg}"
    except Exception as e:  # keep what we have so far instead of losing the run
        transcript.error = str(e)
    return transcript


def save_transcripts(transcripts: list[Transcript], out_dir: str | Path = "runs") -> Path:
    """Write all transcripts to runs/<timestamp>.json and return the file path."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    path.write_text(
        json.dumps([t.to_dict() for t in transcripts], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def load_transcripts(path: str | Path) -> list[Transcript]:
    """Read a runs/<timestamp>.json file back into Transcript objects."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Transcript.from_dict(d) for d in data]
