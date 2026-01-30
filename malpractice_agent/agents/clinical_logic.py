"""
Malpractice agent system using OpenAI or MiniMax (OpenAI-compatible) text API.

Usage:
  # OpenAI (default)
  agent = MalpracticeAgentSystem(api_key=os.environ["OPENAI_API_KEY"])

  # MiniMax text-openai-api
  agent = MalpracticeAgentSystem(
      api_key=os.environ["MINIMAX_API_KEY"],
      base_url=MINIMAX_BASE_URL,
      model="MiniMax-M2.1",  # or "MiniMax-M2.1-lightning", "MiniMax-M2"
  )
"""
import json
import logging
import re
from pathlib import Path
from typing import Literal

import openai
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

# MiniMax OpenAI-compatible API (https://api.minimax.io/v1)
MINIMAX_BASE_URL = "https://api.minimax.io/v1"
MINIMAX_DEFAULT_MODEL = "MiniMax-M2.1"


class OrchestratorReport(BaseModel):
    """Structured output from the lead orchestrator agent."""

    risk_level: Literal["Low", "Medium", "High", "Critical"]
    executive_summary: str = Field(..., description="At most 2 sentences")
    compliance_score: int = Field(..., ge=0, le=100)
    key_concerns: list[str] = Field(default_factory=list)
    recommended_action: str


def _extract_json(text: str) -> str:
    """Strip markdown code fence if present and return inner JSON string."""
    text = text.strip()
    if text.startswith("```"):
        # ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return text


class MalpracticeAgentSystem:
    def __init__(self, api_key, base_url=None, model=None):
        """
        Initialize the agent system.

        Args:
            api_key: API key (OpenAI key or MiniMax key).
            base_url: Optional. Set to MINIMAX_BASE_URL to use MiniMax text-openai-api.
            model: Optional. Model name (e.g. "gpt-4o" for OpenAI, "MiniMax-M2.1" for MiniMax).
        """
        if base_url is None:
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model or "gpt-4o"
            self._is_minimax = False
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.model = model or MINIMAX_DEFAULT_MODEL
            self._is_minimax = True
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict[str, str]:
        """Load prompts from config/system_prompts.md. Sections are delimited by ## NAME."""
        config_dir = Path(__file__).resolve().parent.parent / "config"
        path = config_dir / "system_prompts.md"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Split by ## HEADER; capture header name and content until next ##
        pattern = re.compile(r"^##\s+([A-Z_]+)\s*\n(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)
        prompts = {}
        for match in pattern.finditer(content):
            section_name = match.group(1).strip()
            body = match.group(2).strip()
            # SCRIBE_PROMPT -> scribe, PHARMACIST_PROMPT -> pharmacist, etc.
            key = section_name.replace("_PROMPT", "").lower()
            prompts[key] = body
        return prompts

    def run_analysis(self, raw_transcript, output_dir: Path | str | None = None):
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)

        def _save(role: str, content: str) -> None:
            if output_path:
                (output_path / f"{role}.txt").write_text(content, encoding="utf-8")

        logger.info("Starting analysis: cleaning transcript (scribe)")
        clean_transcript = self._call_agent("scribe", raw_transcript)
        _save("scribe", clean_transcript)

        logger.info("Running risk analyses: pharmacist, watchdog, risk_officer")
        pharm_report = self._call_agent("pharmacist", clean_transcript)
        _save("pharmacist", pharm_report)
        audit_report = self._call_agent("watchdog", clean_transcript)
        _save("watchdog", audit_report)
        risk_report = self._call_agent("risk_officer", clean_transcript)
        _save("risk_officer", risk_report)

        logger.info("Synthesizing reports (lead_orchestrator)")
        return self._synthesize(pharm_report, audit_report, risk_report)

    def _synthesize(
        self,
        pharm_report: str,
        audit_report: str,
        risk_report: str | None = None,
    ) -> OrchestratorReport:
        """Call the lead_orchestrator agent and parse response into OrchestratorReport."""
        sections = [
            "## Pharmacist Report",
            pharm_report,
            "",
            "## Watchdog (Compliance) Report",
            audit_report,
        ]
        if risk_report:
            sections.extend(["", "## Risk Officer Report", risk_report])
        content = "\n".join(sections)
        raw = self._call_agent("lead_orchestrator", content)
        logger.info("Parsing orchestrator JSON and validating")
        json_str = _extract_json(raw)
        data = json.loads(json_str)
        try:
            return OrchestratorReport.model_validate(data)
        except ValidationError as e:
            logger.exception(
                "Pydantic validation failed for orchestrator response: %s",
                e.errors(),
            )
            raise

    def _call_agent(self, agent_role, content):
        logger.info("Calling agent: %s (input length: %d chars)", agent_role, len(content))
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.prompts[agent_role]},
                {"role": "user", "content": content},
            ],
        }
        if self._is_minimax:
            # MiniMax M2.1: separate thinking into reasoning_details (optional)
            kwargs["extra_body"] = {"reasoning_split": True}
        response = self.client.chat.completions.create(**kwargs)
        msg = response.choices[0].message
        out = msg.content or ""
        logger.info("Completed agent: %s (output length: %d chars)", agent_role, len(out))
        return out
