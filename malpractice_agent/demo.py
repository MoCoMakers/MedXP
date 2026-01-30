import json
import os
from pathlib import Path

from malpractice_agent.agents.clinical_logic import (
    MalpracticeAgentSystem,
    MINIMAX_BASE_URL,
)

agent = MalpracticeAgentSystem(
    api_key=os.environ["MINIMAX_API_KEY"],
    base_url=MINIMAX_BASE_URL,
    model="MiniMax-M2.1",  # or "MiniMax-M2.1-lightning", "MiniMax-M2"
)
report = agent.run_analysis(raw_transcript="...")

output_path = Path(__file__).resolve().parent / "synthesized_report.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

print(report.model_dump_json(indent=2))
print(f"\nReport saved to {output_path}")