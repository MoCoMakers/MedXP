"""Run from project root: python3 -m malpractice_agent.demo"""
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from malpractice_agent.agents.clinical_logic import (
    MalpracticeAgentSystem,
    MINIMAX_BASE_URL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

api_key = os.environ.get("MINIMAX_API_KEY")
if not api_key:
    raise SystemExit(
        "MINIMAX_API_KEY is not set. Add it to .env in the project root or export it."
    )

scenarios_path = Path(__file__).resolve().parent.parent / "Data" / "scenarios.json"
with open(scenarios_path, encoding="utf-8") as f:
    scenarios = json.load(f)

patient = scenarios["P001"]
transcript = patient["Scenarios"][0]["Transcript"]

print("Input (first lines) for run_analysis:")
print("-" * 60)
for line in transcript.splitlines()[:5]:
    print(line)
print("-" * 60)

agent = MalpracticeAgentSystem(
    api_key=api_key,
    base_url=MINIMAX_BASE_URL,
    model="MiniMax-M2.1",  # or "MiniMax-M2.1-lightning", "MiniMax-M2"
)
output_dir = Path(__file__).resolve().parent / "output"
report = agent.run_analysis(raw_transcript=transcript, output_dir=output_dir)

report_path = output_dir / "synthesized_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

print(report.model_dump_json(indent=2))
print(f"\nOutputs saved to {output_dir}/")
print(f"  - scribe.txt, pharmacist.txt, watchdog.txt, risk_officer.txt")
print(f"  - synthesized_report.json")