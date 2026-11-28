"""Day 3: the LLM judge reads saved transcripts and reports rule violations.

Run:  python scripts/day3_judge.py                    (judges the newest file in runs/)
      python scripts/day3_judge.py runs/<file>.json   (judges a specific run)

Judging uses one LLM call per conversation, so it is cheap to re-run.
The report is printed and saved next to the run as <file>.report.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

from agenttest.judge import judge_transcript
from agenttest.runner import load_transcripts
from support_bot import BOT_DESCRIPTION


def pick_run_file() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    runs = sorted(p for p in (ROOT / "runs").glob("*.json") if not p.name.endswith(".report.json"))
    if not runs:
        raise SystemExit("No runs found. Run python scripts/day2_run.py first.")
    return runs[-1]


def main():
    run_file = pick_run_file()
    transcripts = load_transcripts(run_file)
    print(f"Judging {run_file.name} ({len(transcripts)} conversations)\n")

    report, failed = [], 0
    for t in transcripts:
        name = t.persona.name
        if not any(turn["role"] == "bot" for turn in t.turns):
            print(f"SKIP  {name}: no bot replies to judge ({t.error[:60] or 'empty'})\n")
            report.append({"persona": name, "skipped": True})
            continue
        try:
            verdict = judge_transcript(t, BOT_DESCRIPTION)
        except Exception as e:
            print(f"ERROR {name}: judge failed: {str(e)[:120]}\n")
            report.append({"persona": name, "error": str(e)})
            continue

        failed += not verdict.passed
        print(f"{'PASS' if verdict.passed else 'FAIL'}  {name}  (tested: {t.persona.attacks_rule})")
        print(f"      {verdict.summary}")
        for v in verdict.violations:
            print(f"      - [{v.severity.upper()}] {v.category} at bot msg {v.turn}: {v.rule}")
            print(f"        \"{v.quote}\"")
            print(f"        {v.explanation}")
        print()
        report.append({"persona": name, **verdict.model_dump()})

    judged = sum(1 for r in report if "passed" in r)
    print(f"Result: {judged - failed}/{judged} conversations passed")
    out = run_file.with_name(run_file.stem + ".report.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report saved to {out}")


if __name__ == "__main__":
    main()
