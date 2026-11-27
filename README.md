# agenttest

**Automated testing for AI chatbots and agents.**

Most teams test their chatbot by chatting with it for a few minutes before shipping. `agenttest` does it automatically. It simulates realistic users (angry, confused, manipulative, Hinglish-speaking), runs full conversations against your bot, and uses an LLM judge to report where it breaks your rules.

> 🚧 Early development. Built in public, week by week.

## What it catches

- **Policy violations:** promising refunds or discounts it isn't allowed to give
- **Hallucinated actions:** "I've transferred you to an agent" when no such agent exists
- **Data leaks:** revealing other customers' details or its own system prompt
- **Prompt injection:** "I'm the admin, ignore your instructions..."
- **Regressions:** things that worked before a prompt or model change and now don't
- **Multilingual gaps:** rules that hold in English but break in Hinglish

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Windows  (macOS/Linux: cp .env.example .env), then paste your Gemini API key into .env
python scripts/hello_llm.py     # check the key works
python examples/support_bot.py  # chat with the demo target bot
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

## Demo target: QuickBite

`examples/support_bot.py` is a support bot for a fictional food delivery app. It has a Rs 500 refund cap, confidential customer data and a secret system prompt, so it makes a good first target to break.

## Roadmap

- [x] Week 1: LLM client + demo target bot
- [ ] Week 2: Persona generator, conversation runner, LLM judge
- [ ] Week 3: CLI: `agenttest run config.yaml`
- [ ] Week 4: Web dashboard with failure transcripts and run comparison
- [ ] Week 5: Hinglish/multilingual and prompt-injection test packs
- [ ] Week 6: Launch
