"""Request models for the Context Enrichment Agent API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Medication(BaseModel):
    """Medication information."""

    name: str
    dose: str
    status: Optional[str] = None
    time: Optional[datetime] = None


class VitalSigns(BaseModel):
    """Vital signs measurement."""

    time: Optional[datetime] = None
    temp_c: Optional[float] = Field(None, alias="Temp_C")
    hr: Optional[int] = Field(None, alias="HR")
    rr: Optional[int] = Field(None, alias="RR")
    bp_sys: Optional[int] = Field(None, alias="BP_sys")
    bp_dia: Optional[int] = Field(None, alias="BP_dia")
    spo2: Optional[int] = Field(None, alias="SpO2")

    class Config:
        populate_by_name = True


class LabResult(BaseModel):
    """Laboratory result."""

    time: Optional[datetime] = None
    name: str
    value: float
    unit: str
    flag: Optional[str] = None  # N (normal), H (high), L (low)


class PatientData(BaseModel):
    """Patient information for context enrichment."""

    patient_id: str = Field(..., description="Unique patient identifier")
    name: Optional[str] = Field(None, description="Patient name")
    age: Optional[int] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    room: Optional[str] = Field(None, description="Room number")
    mrn: Optional[str] = Field(None, description="Medical record number")
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    active_problems: list[str] = Field(default_factory=list, description="Active medical problems")
    allergies: list[str] = Field(default_factory=list, description="Known allergies")
    code_status: Optional[str] = Field(None, description="Code status (Full Code, DNR, etc.)")
    isolation: Optional[str] = Field(None, description="Isolation precautions")
    lines_drains: list[str] = Field(default_factory=list, description="Lines and drains")
    current_medications: list[Medication] = Field(
        default_factory=list, description="Current medications"
    )
    recent_vitals: Optional[VitalSigns] = Field(None, description="Most recent vital signs")
    recent_labs: list[LabResult] = Field(default_factory=list, description="Recent lab results")


class ProviderData(BaseModel):
    """Healthcare provider information."""

    staff_id: str = Field(..., description="Staff identifier")
    name: Optional[str] = Field(None, description="Provider name")
    role: Optional[str] = Field(None, description="Role (Nurse, Doctor, Resident, etc.)")


class EnrichmentRequest(BaseModel):
    """Request model for context enrichment."""

    session_id: str = Field(..., description="Unique session identifier")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now, description="Session timestamp"
    )
    patient: PatientData = Field(..., description="Patient data")
    provider: ProviderData = Field(..., description="Healthcare provider data")
    transcript: str = Field(..., description="Session transcript text")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "S001",
                "timestamp": "2026-01-30T10:00:00",
                "patient": {
                    "patient_id": "P001",
                    "name": "Maria Chen",
                    "age": 62,
                    "gender": "Female",
                    "primary_diagnosis": "Stage IIIB non-small cell lung cancer (NSCLC)",
                    "active_problems": ["Hemoptysis", "Neutropenia", "Hypoxia"],
                    "allergies": ["NKDA"],
                    "code_status": "Full Code",
                    "current_medications": [
                        {"name": "Enoxaparin", "dose": "40 mg SQ daily", "status": "active"}
                    ],
                },
                "provider": {
                    "staff_id": "N03",
                    "name": "Nurse Priya Nair",
                    "role": "RN",
                },
                "transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB NSCLC...",
            }
        }
