"""Response models for the Context Enrichment Agent API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CriticalValue(BaseModel):
    """A critical lab or vital sign value."""

    name: str
    value: float
    unit: str
    flag: str  # H (high), L (low), C (critical)
    reference_range: Optional[str] = None


class PatientSummary(BaseModel):
    """Summary of patient's key clinical information."""

    key_diagnoses: list[str] = Field(default_factory=list, description="Key diagnoses")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")
    critical_values: list[CriticalValue] = Field(
        default_factory=list, description="Critical lab/vital values"
    )


class RelevantSOP(BaseModel):
    """A relevant Standard Operating Procedure."""

    sop_id: str = Field(..., description="SOP identifier")
    title: str = Field(..., description="SOP title")
    relevance_reason: str = Field(..., description="Why this SOP is relevant")
    key_steps: list[str] = Field(default_factory=list, description="Key steps to follow")
    priority: Optional[str] = Field(None, description="Priority level")


class ApplicablePolicy(BaseModel):
    """An applicable hospital policy."""

    policy_id: str = Field(..., description="Policy identifier")
    title: str = Field(..., description="Policy title")
    requirement: str = Field(..., description="Policy requirement summary")
    compliance_status: Optional[str] = Field(
        None, description="Current compliance status if known"
    )


class TreatmentGuideline(BaseModel):
    """A relevant treatment guideline."""

    guideline_id: str = Field(..., description="Guideline identifier")
    source: str = Field(..., description="Guideline source (e.g., NCCN, hospital protocol)")
    title: str = Field(..., description="Guideline title")
    recommendation: str = Field(..., description="Key recommendation")
    evidence_level: Optional[str] = Field(None, description="Evidence level if available")


class Warning(BaseModel):
    """A clinical warning or alert."""

    type: str = Field(
        ...,
        description="Warning type (drug_interaction, contraindication, critical_value, allergy, etc.)",
    )
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    message: str = Field(..., description="Human-readable warning message")
    evidence: Optional[str] = Field(None, description="Supporting evidence or context")
    action_required: Optional[str] = Field(None, description="Recommended action")


class EnrichmentMetadata(BaseModel):
    """Metadata about the enrichment process."""

    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    sources_consulted: list[str] = Field(
        default_factory=list, description="Knowledge sources consulted"
    )
    llm_calls: int = Field(default=0, description="Number of LLM API calls made")
    enrichment_version: str = Field(default="1.0", description="Enrichment agent version")


class EnrichmentResponse(BaseModel):
    """Response model for context enrichment."""

    session_id: str = Field(..., description="Session identifier from request")
    enriched_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of enrichment"
    )
    patient_summary: PatientSummary = Field(..., description="Patient clinical summary")
    relevant_sops: list[RelevantSOP] = Field(
        default_factory=list, description="Relevant SOPs for this case"
    )
    applicable_policies: list[ApplicablePolicy] = Field(
        default_factory=list, description="Applicable hospital policies"
    )
    treatment_guidelines: list[TreatmentGuideline] = Field(
        default_factory=list, description="Relevant treatment guidelines"
    )
    warnings: list[Warning] = Field(
        default_factory=list, description="Clinical warnings and alerts"
    )
    metadata: EnrichmentMetadata = Field(..., description="Enrichment process metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "S001",
                "enriched_at": "2026-01-30T10:00:05",
                "patient_summary": {
                    "key_diagnoses": ["Stage IIIB NSCLC", "Neutropenia", "Hemoptysis"],
                    "risk_factors": [
                        "On anticoagulation with hemoptysis",
                        "Hypoxia risk",
                        "Neutropenic - infection risk",
                    ],
                    "critical_values": [],
                },
                "relevant_sops": [
                    {
                        "sop_id": "SOP-AC-001",
                        "title": "Anticoagulation Management with Active Bleeding",
                        "relevance_reason": "Patient on Enoxaparin with hemoptysis",
                        "key_steps": [
                            "Hold anticoagulation",
                            "Notify physician",
                            "Monitor for bleeding",
                        ],
                    }
                ],
                "warnings": [
                    {
                        "type": "contraindication",
                        "severity": "high",
                        "message": "Patient on Enoxaparin with active hemoptysis - review anticoagulation",
                        "action_required": "Consult physician about holding anticoagulation",
                    }
                ],
                "metadata": {
                    "processing_time_ms": 150,
                    "sources_consulted": ["nsclc_sops", "hospital_policies", "nsclc_guidelines"],
                    "llm_calls": 1,
                },
            }
        }
