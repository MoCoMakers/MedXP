"""Context Enrichment Agent - orchestrates the enrichment pipeline."""

import time
from datetime import datetime
from typing import Optional

from models.request import EnrichmentRequest
from models.response import (
    ApplicablePolicy,
    CriticalValue,
    EnrichmentMetadata,
    EnrichmentResponse,
    PatientSummary,
    RelevantSOP,
    TreatmentGuideline,
    Warning,
)
from services.knowledge_retriever import get_knowledge_retriever, RetrievalResult
from services.llm_client import get_llm_client


class ContextEnrichmentAgent:
    """
    Agent that enriches session context with relevant medical knowledge.

    Pipeline:
    1. Parse and validate input
    2. Extract key entities from patient data and transcript
    3. Retrieve relevant SOPs, policies, and guidelines
    4. Generate patient summary with risk factors
    5. Check for warnings (drug interactions, contraindications, critical values)
    6. Assemble enriched output
    """

    def __init__(self):
        self.knowledge_retriever = get_knowledge_retriever()
        self.llm_client = get_llm_client()

    async def enrich(self, request: EnrichmentRequest) -> EnrichmentResponse:
        """
        Main enrichment pipeline.

        Args:
            request: EnrichmentRequest with patient, provider, and transcript data

        Returns:
            EnrichmentResponse with enriched context
        """
        start_time = time.time()
        llm_calls = 0
        sources_consulted = []

        # Convert patient data to dict for processing
        patient_dict = request.patient.model_dump()

        # 1. Retrieve relevant knowledge
        retrieval_results = self.knowledge_retriever.retrieve_all(
            patient_dict, request.transcript
        )

        # Track sources
        if retrieval_results["sops"]:
            sources_consulted.append("nsclc_sops")
        if retrieval_results["policies"]:
            sources_consulted.append("hospital_policies")
        if retrieval_results["guidelines"]:
            sources_consulted.append("nsclc_guidelines")

        # 2. Generate patient summary
        patient_summary = await self._generate_patient_summary(
            patient_dict, request.transcript, retrieval_results
        )
        llm_calls += 1

        # 3. Convert SOPs to response format
        relevant_sops = self._format_sops(retrieval_results["sops"])

        # 4. Convert policies to response format
        applicable_policies = self._format_policies(retrieval_results["policies"])

        # 5. Convert guidelines to response format
        treatment_guidelines = self._format_guidelines(retrieval_results["guidelines"])

        # 6. Generate warnings
        warnings = await self._generate_warnings(
            patient_dict, request.transcript, retrieval_results
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Build metadata
        metadata = EnrichmentMetadata(
            processing_time_ms=processing_time_ms,
            sources_consulted=sources_consulted,
            llm_calls=llm_calls,
            enrichment_version="1.0",
        )

        return EnrichmentResponse(
            session_id=request.session_id,
            enriched_at=datetime.now(),
            patient_summary=patient_summary,
            relevant_sops=relevant_sops,
            applicable_policies=applicable_policies,
            treatment_guidelines=treatment_guidelines,
            warnings=warnings,
            metadata=metadata,
        )

    async def _generate_patient_summary(
        self,
        patient_dict: dict,
        transcript: str,
        retrieval_results: dict,
    ) -> PatientSummary:
        """Generate patient clinical summary."""
        # Extract key diagnoses
        key_diagnoses = []
        if dx := patient_dict.get("primary_diagnosis"):
            key_diagnoses.append(dx)
        key_diagnoses.extend(patient_dict.get("active_problems", [])[:5])

        # Use LLM to identify risk factors
        llm_result = await self.llm_client.summarize_patient_context(
            patient_dict, transcript
        )
        risk_factors = llm_result.get("risk_factors", [])

        # Check for critical values
        critical_values = self._check_critical_values(patient_dict)

        return PatientSummary(
            key_diagnoses=key_diagnoses,
            risk_factors=risk_factors,
            critical_values=critical_values,
        )

    def _check_critical_values(self, patient_dict: dict) -> list[CriticalValue]:
        """Check labs and vitals for critical values."""
        critical_values = []

        # Critical lab thresholds
        critical_thresholds = {
            "K": {"low": 2.5, "high": 6.5, "unit": "mmol/L"},
            "Na": {"low": 120, "high": 160, "unit": "mmol/L"},
            "Hgb": {"low": 7.0, "high": None, "unit": "g/dL"},
            "WBC": {"low": 0.5, "high": 30.0, "unit": "K/uL"},
            "Plt": {"low": 20.0, "high": None, "unit": "K/uL"},
            "Lactate": {"low": None, "high": 4.0, "unit": "mmol/L"},
            "Cr": {"low": None, "high": 4.0, "unit": "mg/dL"},
            "Troponin": {"low": None, "high": 0.5, "unit": "ng/mL"},
        }

        for lab in patient_dict.get("recent_labs", []):
            if not isinstance(lab, dict):
                continue

            name = lab.get("name")
            value = lab.get("value")
            unit = lab.get("unit", "")

            if name in critical_thresholds and value is not None:
                thresholds = critical_thresholds[name]
                flag = None

                if thresholds.get("low") and value < thresholds["low"]:
                    flag = "L"
                elif thresholds.get("high") and value > thresholds["high"]:
                    flag = "H"

                if flag:
                    critical_values.append(
                        CriticalValue(
                            name=name,
                            value=value,
                            unit=unit or thresholds["unit"],
                            flag=flag,
                            reference_range=f"{thresholds.get('low', 'N/A')}-{thresholds.get('high', 'N/A')}",
                        )
                    )

        # Check vitals
        vitals = patient_dict.get("recent_vitals")
        if vitals and isinstance(vitals, dict):
            # Check SpO2
            spo2 = vitals.get("spo2") or vitals.get("SpO2")
            if spo2 and spo2 < 90:
                critical_values.append(
                    CriticalValue(
                        name="SpO2",
                        value=float(spo2),
                        unit="%",
                        flag="L",
                        reference_range=">92%",
                    )
                )

            # Check temperature
            temp = vitals.get("temp_c") or vitals.get("Temp_C")
            if temp and temp >= 38.5:
                critical_values.append(
                    CriticalValue(
                        name="Temperature",
                        value=float(temp),
                        unit="°C",
                        flag="H",
                        reference_range="36.5-38.0°C",
                    )
                )

        return critical_values

    def _format_sops(self, sop_results: list[RetrievalResult]) -> list[RelevantSOP]:
        """Format SOP retrieval results for response."""
        formatted = []
        for result in sop_results:
            content = result.content
            formatted.append(
                RelevantSOP(
                    sop_id=result.item_id,
                    title=result.title,
                    relevance_reason=", ".join(result.matched_keywords[:3]),
                    key_steps=content.get("steps", [])[:5],
                    priority=content.get("priority", "medium"),
                )
            )
        return formatted

    def _format_policies(
        self, policy_results: list[RetrievalResult]
    ) -> list[ApplicablePolicy]:
        """Format policy retrieval results for response."""
        formatted = []
        for result in policy_results:
            content = result.content
            formatted.append(
                ApplicablePolicy(
                    policy_id=result.item_id,
                    title=result.title,
                    requirement=content.get("requirement", ""),
                    compliance_status=None,  # Could be determined by checking criteria
                )
            )
        return formatted

    def _format_guidelines(
        self, guideline_results: list[RetrievalResult]
    ) -> list[TreatmentGuideline]:
        """Format guideline retrieval results for response."""
        formatted = []
        for result in guideline_results:
            content = result.content
            recommendation = content.get("recommendation", "")

            # For stage-based guidelines, try to get relevant stage info
            if "stages" in content:
                stages = content["stages"]
                # Default to most advanced stage info as most relevant for NSCLC
                if "Stage IV" in stages:
                    recommendation = stages["Stage IV"].get("recommendation", recommendation)
                elif "Stage III" in stages:
                    recommendation = stages["Stage III"].get("recommendation", recommendation)

            formatted.append(
                TreatmentGuideline(
                    guideline_id=result.item_id,
                    source=content.get("source", "Clinical Guidelines"),
                    title=result.title,
                    recommendation=recommendation,
                    evidence_level=content.get("evidence_level"),
                )
            )
        return formatted

    async def _generate_warnings(
        self,
        patient_dict: dict,
        transcript: str,
        retrieval_results: dict,
    ) -> list[Warning]:
        """Generate clinical warnings based on patient data and context."""
        warnings = []

        # Get patient context
        context = self.knowledge_retriever.extract_patient_context(patient_dict, transcript)

        # 1. Check for bleeding + anticoagulation
        medications = [
            m.get("name", "").lower() if isinstance(m, dict) else str(m).lower()
            for m in patient_dict.get("current_medications", [])
        ]
        anticoagulants = ["enoxaparin", "heparin", "warfarin", "rivaroxaban", "apixaban"]
        on_anticoagulation = any(ac in med for med in medications for ac in anticoagulants)

        if on_anticoagulation:
            active_problems = [p.lower() for p in patient_dict.get("active_problems", [])]
            if any("hemoptysis" in p or "bleeding" in p for p in active_problems):
                warnings.append(
                    Warning(
                        type="contraindication",
                        severity="high",
                        message="Patient on anticoagulation with active hemoptysis - review need for anticoagulation",
                        evidence="Active bleeding is a contraindication to anticoagulation",
                        action_required="Consult physician about holding anticoagulation",
                    )
                )

        # 2. Check for neutropenia + fever
        if any("neutropenia" in p.lower() for p in patient_dict.get("active_problems", [])):
            vitals = patient_dict.get("recent_vitals", {})
            temp = vitals.get("temp_c") or vitals.get("Temp_C") if vitals else None
            if temp and temp >= 38.0:
                warnings.append(
                    Warning(
                        type="clinical_alert",
                        severity="critical",
                        message="Neutropenic fever - requires immediate evaluation and antibiotics",
                        evidence=f"Temperature {temp}°C in neutropenic patient",
                        action_required="Blood cultures and broad-spectrum antibiotics within 60 minutes",
                    )
                )

        # 3. Check for hypoxia
        vitals = patient_dict.get("recent_vitals", {})
        spo2 = vitals.get("spo2") or vitals.get("SpO2") if vitals else None
        if spo2 and spo2 < 92:
            warnings.append(
                Warning(
                    type="clinical_alert",
                    severity="high",
                    message=f"Hypoxia detected (SpO2 {spo2}%) - assess respiratory status",
                    evidence="SpO2 below target threshold",
                    action_required="Titrate oxygen, assess work of breathing, consider chest imaging",
                )
            )

        # 4. Check for allergy concerns
        allergies = [a.lower() for a in patient_dict.get("allergies", [])]
        if any("penicillin" in a for a in allergies):
            if any("piperacillin" in med or "ampicillin" in med for med in medications):
                warnings.append(
                    Warning(
                        type="allergy",
                        severity="high",
                        message="Patient has penicillin allergy - verify beta-lactam safety",
                        evidence="Penicillin allergy documented",
                        action_required="Confirm reaction type and appropriateness of current antibiotics",
                    )
                )

        # 5. Check code status documentation
        code_status = patient_dict.get("code_status")
        if not code_status or code_status.lower() == "unknown":
            warnings.append(
                Warning(
                    type="documentation",
                    severity="medium",
                    message="Code status not clearly documented",
                    evidence="Code status field missing or unknown",
                    action_required="Verify and document code status with patient/family",
                )
            )

        # 6. Check for opioid + sedative combination
        opioids = ["morphine", "hydromorphone", "oxycodone", "fentanyl"]
        sedatives = ["lorazepam", "diazepam", "midazolam", "alprazolam"]
        has_opioid = any(op in med for med in medications for op in opioids)
        has_sedative = any(sed in med for med in medications for sed in sedatives)

        if has_opioid and has_sedative:
            warnings.append(
                Warning(
                    type="drug_interaction",
                    severity="medium",
                    message="Concurrent opioid and benzodiazepine use - monitor for respiratory depression",
                    evidence="Both drug classes present in medication list",
                    action_required="Monitor respiratory rate and sedation level",
                )
            )

        # 7. Add warnings from high-priority retrieved SOPs
        for sop in retrieval_results.get("sops", [])[:2]:
            if sop.content.get("priority") == "high":
                warnings.append(
                    Warning(
                        type="protocol_trigger",
                        severity="medium",
                        message=f"Relevant protocol triggered: {sop.title}",
                        evidence=", ".join(sop.matched_keywords[:3]),
                        action_required=f"Review SOP {sop.item_id} and ensure compliance",
                    )
                )

        return warnings


# Singleton instance
_agent: Optional[ContextEnrichmentAgent] = None


def get_context_enrichment_agent() -> ContextEnrichmentAgent:
    """Get or create the context enrichment agent singleton."""
    global _agent
    if _agent is None:
        _agent = ContextEnrichmentAgent()
    return _agent
