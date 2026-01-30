"""
Test script for the Context Enrichment Agent.

This script tests the enrichment pipeline using sample data from the Data folder.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.context_enrichment import get_context_enrichment_agent
from models.request import EnrichmentRequest, PatientData, ProviderData, Medication, VitalSigns, LabResult


def load_sample_data():
    """Load sample patient data from Data folder."""
    data_path = Path(__file__).parent.parent / "Data"
    
    with open(data_path / "patients_ehr.json") as f:
        patients_data = json.load(f)
    
    with open(data_path / "scenarios.json") as f:
        scenarios_data = json.load(f)
    
    return patients_data, scenarios_data


def create_test_request(patient: dict, scenario: dict) -> EnrichmentRequest:
    """Create an EnrichmentRequest from patient and scenario data."""
    
    # Convert medications
    medications = []
    for med in patient.get("Medications", [])[:5]:  # Limit to 5 recent
        medications.append(Medication(
            name=med.get("name", ""),
            dose=med.get("dose", ""),
            status=med.get("status"),
            time=med.get("time"),
        ))
    
    # Get most recent vitals
    vitals_list = patient.get("Vitals", [])
    recent_vitals = None
    if vitals_list:
        v = vitals_list[-1]
        recent_vitals = VitalSigns(
            time=v.get("time"),
            Temp_C=v.get("Temp_C"),
            HR=v.get("HR"),
            RR=v.get("RR"),
            BP_sys=v.get("BP_sys"),
            BP_dia=v.get("BP_dia"),
            SpO2=v.get("SpO2"),
        )
    
    # Convert recent labs
    recent_labs = []
    for lab in patient.get("Labs", [])[-5:]:  # Last 5 labs
        recent_labs.append(LabResult(
            time=lab.get("time"),
            name=lab.get("name", ""),
            value=lab.get("value", 0),
            unit=lab.get("unit", ""),
            flag=lab.get("flag"),
        ))
    
    # Create patient data
    patient_data = PatientData(
        patient_id=patient.get("PatientID", ""),
        name=patient.get("PatientName"),
        age=patient.get("Age"),
        gender=patient.get("Gender"),
        room=patient.get("Room"),
        mrn=patient.get("MRN"),
        primary_diagnosis=patient.get("PrimaryDiagnosis"),
        active_problems=patient.get("ActiveProblems", []),
        allergies=patient.get("Allergies", []),
        code_status=patient.get("CodeStatus"),
        isolation=patient.get("Isolation"),
        lines_drains=patient.get("LinesDrains", []),
        current_medications=medications,
        recent_vitals=recent_vitals,
        recent_labs=recent_labs,
    )
    
    # Create provider data
    recorded_by = scenario.get("RecordedBy", {})
    provider_data = ProviderData(
        staff_id=recorded_by.get("StaffID", "N001"),
        name=recorded_by.get("Name", "Test Nurse"),
        role=scenario.get("IncomingRole", "RN"),
    )
    
    # Create request
    return EnrichmentRequest(
        session_id=f"TEST-{patient.get('PatientID', 'P001')}",
        patient=patient_data,
        provider=provider_data,
        transcript=scenario.get("Transcript", ""),
    )


async def test_enrichment():
    """Test the enrichment pipeline."""
    print("=" * 60)
    print("MedXP Context Enrichment Agent - Test")
    print("=" * 60)
    
    # Load sample data
    print("\n[1] Loading sample data...")
    patients_data, scenarios_data = load_sample_data()
    
    patients = patients_data.get("Patients", [])
    scenarios = scenarios_data.get("Scenarios", [])
    
    print(f"    Loaded {len(patients)} patients")
    print(f"    Loaded {len(scenarios)} scenarios")
    
    # Get agent
    print("\n[2] Initializing enrichment agent...")
    agent = get_context_enrichment_agent()
    print("    Agent initialized successfully")
    
    # Test with first patient and matching scenario
    print("\n[3] Testing enrichment with sample patient...")
    
    if patients and scenarios:
        patient = patients[0]  # Maria Chen
        # Find matching scenario
        matching_scenarios = [s for s in scenarios if s.get("PatientID") == patient.get("PatientID")]
        scenario = matching_scenarios[0] if matching_scenarios else scenarios[0]
        
        print(f"\n    Patient: {patient.get('PatientName')}")
        print(f"    Diagnosis: {patient.get('PrimaryDiagnosis')}")
        print(f"    Active Problems: {', '.join(patient.get('ActiveProblems', []))}")
        
        # Create request
        request = create_test_request(patient, scenario)
        
        # Run enrichment
        print("\n[4] Running enrichment pipeline...")
        response = await agent.enrich(request)
        
        # Print results
        print("\n" + "=" * 60)
        print("ENRICHMENT RESULTS")
        print("=" * 60)
        
        print(f"\n📋 Session ID: {response.session_id}")
        print(f"⏱️  Processing Time: {response.metadata.processing_time_ms}ms")
        print(f"📚 Sources Consulted: {', '.join(response.metadata.sources_consulted)}")
        
        print(f"\n--- Patient Summary ---")
        print(f"Key Diagnoses: {response.patient_summary.key_diagnoses}")
        print(f"Risk Factors: {response.patient_summary.risk_factors}")
        if response.patient_summary.critical_values:
            print(f"Critical Values: {[f'{cv.name}={cv.value}' for cv in response.patient_summary.critical_values]}")
        
        print(f"\n--- Relevant SOPs ({len(response.relevant_sops)}) ---")
        for sop in response.relevant_sops[:3]:
            print(f"  • [{sop.sop_id}] {sop.title}")
            print(f"    Relevance: {sop.relevance_reason}")
        
        print(f"\n--- Applicable Policies ({len(response.applicable_policies)}) ---")
        for policy in response.applicable_policies[:3]:
            print(f"  • [{policy.policy_id}] {policy.title}")
        
        print(f"\n--- Treatment Guidelines ({len(response.treatment_guidelines)}) ---")
        for guideline in response.treatment_guidelines[:3]:
            print(f"  • [{guideline.guideline_id}] {guideline.title}")
            print(f"    Source: {guideline.source}")
        
        print(f"\n--- Warnings ({len(response.warnings)}) ---")
        for warning in response.warnings:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(warning.severity, "⚪")
            print(f"  {severity_icon} [{warning.severity.upper()}] {warning.type}")
            print(f"    {warning.message}")
            if warning.action_required:
                print(f"    Action: {warning.action_required}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # Return response for further inspection
        return response
    else:
        print("ERROR: No sample data available")
        return None


if __name__ == "__main__":
    result = asyncio.run(test_enrichment())
