"""Unit test suite verifying candidate case keyword filtering and diagnostic model schemas for NetPulse AI Engine."""

import pytest
from src.diagnosis import filter_candidate_cases, diagnose
from src.data_loader import load_cases
from src.models import Evidence, DiagnosisResult
from src.evidence_parser import normalize_evidence


def test_filter_candidate_cases_dhcp_keyword():
    """Verify concept keyword matching for DHCP telemetry evidence."""
    all_scenarios = load_cases()
    telemetry = Evidence(
        case_id=14,
        ipconfig="IP Address: 192.168.10.5\nDefault Gateway: 192.168.10.254",
        show_running_config="ip dhcp pool LAN1\n network 192.168.10.0 255.255.255.0\n default-router 192.168.10.254"
    )
    candidate_matches = filter_candidate_cases(telemetry, all_scenarios)
    assert len(candidate_matches) > 0
    matched_concepts = [c.case.concept for c in candidate_matches]
    assert any("dhcp" in concept.lower() for concept in matched_concepts)


def test_filter_candidate_cases_vlan_keyword():
    """Verify concept keyword matching for VLAN switchport evidence."""
    all_scenarios = load_cases()
    telemetry = Evidence(
        case_id=5,
        show_vlan_brief="VLAN 20 active\nVLAN 10 missing from switch",
        show_running_config="interface FastEthernet0/1\n switchport access vlan 10"
    )
    candidate_matches = filter_candidate_cases(telemetry, all_scenarios)
    assert len(candidate_matches) > 0
    matched_concepts = [c.case.concept for c in candidate_matches]
    assert any("vlan" in concept.lower() for concept in matched_concepts)


def test_filter_candidate_cases_empty_fallback():
    """Verify fallback behavior when empty telemetry is submitted."""
    all_scenarios = load_cases()
    empty_telemetry = Evidence()
    candidate_matches = filter_candidate_cases(empty_telemetry, all_scenarios)
    assert len(candidate_matches) == len(all_scenarios)


def test_normalize_evidence_formatting():
    """Verify evidence normalization block formatting."""
    telemetry = Evidence(
        ipconfig="IPv4 Address: 10.0.1.5",
        ping_results="Ping 10.0.1.1: Request timed out"
    )
    formatted_str = normalize_evidence(telemetry)
    assert "IPv4 Address: 10.0.1.5" in formatted_str
    assert "Ping 10.0.1.1: Request timed out" in formatted_str


def test_diagnosis_result_pydantic_schema():
    """Verify DiagnosisResult schema validation and confidence bound constraints."""
    valid_result = DiagnosisResult(
        case_id=1,
        predicted_fault="Wrong IP Address",
        confidence=0.92,
        reasoning_summary="Host IP address resides on unrouted subnet",
        evidence_used=["ipconfig"],
        recommended_fix="Reconfigure IP address to 192.168.1.10/24",
        commands=["interface FastEthernet0/1", "ip address 192.168.1.10 255.255.255.0"],
        needs_more_evidence=False,
        risk_score=40,
        impact_radius="Local Host"
    )
    assert valid_result.confidence == 0.92
    assert valid_result.risk_score == 40
    assert valid_result.impact_radius == "Local Host"
    
    # Validation error on out-of-bound confidence (> 1.0)
    with pytest.raises(ValueError):
        DiagnosisResult(
            case_id=1,
            predicted_fault="Invalid Case",
            confidence=1.8,
            reasoning_summary="Out of bounds",
            evidence_used=[],
            recommended_fix="None",
            commands=[],
            needs_more_evidence=False
        )