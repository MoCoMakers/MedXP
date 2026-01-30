"""Knowledge retriever service for fetching relevant SOPs, policies, and guidelines."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from config.settings import settings


@dataclass
class RetrievalResult:
    """Result from knowledge retrieval."""

    item_id: str
    title: str
    source: str  # 'sop', 'policy', 'guideline'
    relevance_score: float
    matched_keywords: list[str]
    content: dict


@dataclass
class PatientContext:
    """Extracted context from patient data for matching."""

    diagnoses: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    symptoms: list[str] = field(default_factory=list)
    labs: dict[str, float] = field(default_factory=dict)
    vitals: dict[str, float] = field(default_factory=dict)
    age: Optional[int] = None
    code_status: Optional[str] = None
    isolation: Optional[str] = None


class KnowledgeRetriever:
    """Retrieves relevant knowledge from JSON-based knowledge bases."""

    def __init__(self):
        self.sops: dict = {}
        self.policies: dict = {}
        self.guidelines: dict = {}
        self._load_knowledge_bases()

    def _load_knowledge_bases(self) -> None:
        """Load all knowledge bases from JSON files."""
        try:
            if settings.sops_path.exists():
                with open(settings.sops_path) as f:
                    self.sops = json.load(f)
            if settings.policies_path.exists():
                with open(settings.policies_path) as f:
                    self.policies = json.load(f)
            if settings.guidelines_path.exists():
                with open(settings.guidelines_path) as f:
                    self.guidelines = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading knowledge base: {e}")

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        return re.sub(r"[^a-z0-9\s]", "", text.lower())

    def _extract_keywords_from_text(self, text: str) -> set[str]:
        """Extract keywords from text for matching."""
        normalized = self._normalize_text(text)
        # Split into words and filter short words
        words = {w for w in normalized.split() if len(w) > 2}
        return words

    def extract_patient_context(self, patient_data: dict, transcript: str) -> PatientContext:
        """Extract matching context from patient data and transcript."""
        context = PatientContext()

        # Extract diagnoses
        if primary_dx := patient_data.get("primary_diagnosis"):
            context.diagnoses.append(primary_dx.lower())
        context.diagnoses.extend([p.lower() for p in patient_data.get("active_problems", [])])

        # Extract medications
        for med in patient_data.get("current_medications", []):
            if isinstance(med, dict):
                context.medications.append(med.get("name", "").lower())
            else:
                context.medications.append(str(med).lower())

        # Extract labs
        for lab in patient_data.get("recent_labs", []):
            if isinstance(lab, dict) and "name" in lab and "value" in lab:
                context.labs[lab["name"]] = lab["value"]

        # Extract vitals
        if vitals := patient_data.get("recent_vitals"):
            if isinstance(vitals, dict):
                for key, value in vitals.items():
                    if isinstance(value, (int, float)) and key not in ["time"]:
                        # Normalize key names
                        normalized_key = key.replace("_", "").replace("C", "")
                        context.vitals[normalized_key] = value

        # Extract other context
        context.age = patient_data.get("age")
        context.code_status = patient_data.get("code_status")
        context.isolation = patient_data.get("isolation")

        # Extract symptoms from transcript
        symptom_keywords = [
            "pain", "fever", "cough", "dyspnea", "shortness of breath", "bleeding",
            "hemoptysis", "nausea", "vomiting", "confusion", "delirium", "anxiety",
            "hypoxia", "tachycardia", "hypotension"
        ]
        transcript_lower = transcript.lower()
        context.symptoms = [s for s in symptom_keywords if s in transcript_lower]

        return context

    def _calculate_keyword_score(
        self, item_keywords: list[str], context: PatientContext, transcript: str
    ) -> tuple[float, list[str]]:
        """Calculate relevance score based on keyword matching."""
        score = 0.0
        matched = []

        # Create search text from context
        search_terms = set()
        search_terms.update(self._extract_keywords_from_text(" ".join(context.diagnoses)))
        search_terms.update(self._extract_keywords_from_text(" ".join(context.medications)))
        search_terms.update(self._extract_keywords_from_text(" ".join(context.symptoms)))
        search_terms.update(self._extract_keywords_from_text(transcript))

        # Match against item keywords
        for keyword in item_keywords:
            keyword_lower = keyword.lower()
            keyword_words = self._extract_keywords_from_text(keyword_lower)

            # Exact keyword match in diagnoses (highest weight)
            if any(keyword_lower in dx for dx in context.diagnoses):
                score += 10.0
                matched.append(f"diagnosis:{keyword}")
                continue

            # Medication match
            if any(keyword_lower in med for med in context.medications):
                score += 5.0
                matched.append(f"medication:{keyword}")
                continue

            # Symptom match
            if any(keyword_lower in sym for sym in context.symptoms):
                score += 5.0
                matched.append(f"symptom:{keyword}")
                continue

            # Partial word match in search terms
            if keyword_words & search_terms:
                score += 3.0
                matched.append(f"keyword:{keyword}")

        return score, matched

    def _check_trigger_conditions(
        self, triggers: dict, context: PatientContext
    ) -> tuple[float, list[str]]:
        """Check if trigger conditions are met."""
        score = 0.0
        matched = []

        # Check lab triggers
        if lab_triggers := triggers.get("labs"):
            for lab_name, condition in lab_triggers.items():
                if lab_name in context.labs:
                    value = context.labs[lab_name]
                    threshold = condition.get("threshold")
                    operator = condition.get("operator", "gt")

                    triggered = False
                    if operator == "lt" and threshold and value < threshold:
                        triggered = True
                    elif operator == "gt" and threshold and value > threshold:
                        triggered = True
                    elif operator == "eq" and threshold and value == threshold:
                        triggered = True

                    if triggered:
                        score += 8.0
                        matched.append(f"lab_trigger:{lab_name}={value}")

        # Check vital triggers
        if vital_triggers := triggers.get("vitals"):
            for vital_name, condition in vital_triggers.items():
                # Normalize vital name for comparison
                vital_key = vital_name.replace("_", "").replace("C", "")
                if vital_key in context.vitals:
                    value = context.vitals[vital_key]
                    threshold = condition.get("threshold")
                    operator = condition.get("operator", "gt")

                    triggered = False
                    if operator == "lt" and threshold and value < threshold:
                        triggered = True
                    elif operator == "gt" and threshold and value > threshold:
                        triggered = True

                    if triggered:
                        score += 7.0
                        matched.append(f"vital_trigger:{vital_name}={value}")

        # Check diagnosis triggers
        if dx_triggers := triggers.get("diagnoses"):
            for dx in dx_triggers:
                if any(dx.lower() in patient_dx for patient_dx in context.diagnoses):
                    score += 10.0
                    matched.append(f"diagnosis_trigger:{dx}")

        # Check medication triggers
        if med_triggers := triggers.get("medications"):
            for med in med_triggers:
                if any(med.lower() in patient_med for patient_med in context.medications):
                    score += 6.0
                    matched.append(f"medication_trigger:{med}")

        return score, matched

    def retrieve_sops(
        self, context: PatientContext, transcript: str, top_k: int = None
    ) -> list[RetrievalResult]:
        """Retrieve relevant SOPs based on patient context."""
        top_k = top_k or settings.retrieval_top_k
        results = []

        for sop in self.sops.get("sops", []):
            # Calculate keyword score
            keyword_score, keyword_matches = self._calculate_keyword_score(
                sop.get("keywords", []), context, transcript
            )

            # Check trigger conditions
            trigger_score, trigger_matches = self._check_trigger_conditions(
                sop.get("triggers", {}), context
            )

            total_score = keyword_score + trigger_score
            all_matches = keyword_matches + trigger_matches

            if total_score > settings.relevance_threshold:
                results.append(
                    RetrievalResult(
                        item_id=sop["sop_id"],
                        title=sop["title"],
                        source="sop",
                        relevance_score=total_score,
                        matched_keywords=all_matches,
                        content=sop,
                    )
                )

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def retrieve_policies(
        self, context: PatientContext, transcript: str, top_k: int = None
    ) -> list[RetrievalResult]:
        """Retrieve relevant hospital policies based on patient context."""
        top_k = top_k or settings.retrieval_top_k
        results = []

        for policy in self.policies.get("policies", []):
            # Calculate keyword score
            keyword_score, keyword_matches = self._calculate_keyword_score(
                policy.get("keywords", []), context, transcript
            )

            # Check trigger conditions
            trigger_score, trigger_matches = self._check_trigger_conditions(
                policy.get("triggers", {}), context
            )

            total_score = keyword_score + trigger_score
            all_matches = keyword_matches + trigger_matches

            if total_score > settings.relevance_threshold:
                results.append(
                    RetrievalResult(
                        item_id=policy["policy_id"],
                        title=policy["title"],
                        source="policy",
                        relevance_score=total_score,
                        matched_keywords=all_matches,
                        content=policy,
                    )
                )

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def retrieve_guidelines(
        self, context: PatientContext, transcript: str, top_k: int = None
    ) -> list[RetrievalResult]:
        """Retrieve relevant medical guidelines based on patient context."""
        top_k = top_k or settings.retrieval_top_k
        results = []

        for guideline in self.guidelines.get("guidelines", []):
            # Calculate keyword score
            keyword_score, keyword_matches = self._calculate_keyword_score(
                guideline.get("keywords", []), context, transcript
            )

            total_score = keyword_score
            all_matches = keyword_matches

            if total_score > settings.relevance_threshold:
                results.append(
                    RetrievalResult(
                        item_id=guideline["guideline_id"],
                        title=guideline["title"],
                        source="guideline",
                        relevance_score=total_score,
                        matched_keywords=all_matches,
                        content=guideline,
                    )
                )

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def retrieve_all(
        self, patient_data: dict, transcript: str, top_k_per_source: int = None
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve relevant items from all knowledge sources."""
        context = self.extract_patient_context(patient_data, transcript)
        top_k = top_k_per_source or settings.retrieval_top_k

        return {
            "sops": self.retrieve_sops(context, transcript, top_k),
            "policies": self.retrieve_policies(context, transcript, top_k),
            "guidelines": self.retrieve_guidelines(context, transcript, top_k),
        }


# Singleton instance
_retriever: Optional[KnowledgeRetriever] = None


def get_knowledge_retriever() -> KnowledgeRetriever:
    """Get or create the knowledge retriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeRetriever()
    return _retriever
