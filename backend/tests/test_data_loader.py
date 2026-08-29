"""Unit test suite verifying dataset loading and schema validation for NetPulse AI Engine."""

import pytest
from src.data_loader import load_cases, get_case, get_cases_by_concept, get_cases_by_title, validate_dataset
from src.models import Case


def test_load_cases_structure():
    """Verify load_cases returns valid list of Case models."""
    dataset = load_cases()
    assert len(dataset) >= 30, "Dataset should contain at least 30 telemetry scenarios"
    assert all(isinstance(item, Case) for item in dataset)
    assert all(item.case_id > 0 for item in dataset)


def test_get_case_lookup():
    """Verify single case retrieval by numeric ID."""
    target_case = get_case(1)
    assert target_case is not None, "Case ID 1 should exist in dataset"
    assert target_case.case_id == 1
    assert "Wrong IP" in target_case.title
    
    # Non-existent ID lookup
    assert get_case(9999) is None, "Non-existent case ID should return None"


def test_get_cases_by_concept_filter():
    """Verify filter logic matching concepts."""
    dhcp_scenarios = get_cases_by_concept("DHCP")
    assert len(dhcp_scenarios) >= 4, "Should find multiple DHCP scenarios"
    assert all("dhcp" in c.concept.lower() for c in dhcp_scenarios)


def test_get_cases_by_title_filter():
    """Verify title substring search filter."""
    matched_cases = get_cases_by_title("Wrong")
    assert len(matched_cases) >= 1
    assert any("wrong" in c.title.lower() for c in matched_cases)


def test_validate_dataset_audit():
    """Verify comprehensive dataset health validation report."""
    audit_report = validate_dataset()
    assert "total_cases" in audit_report
    assert "status" in audit_report
    assert audit_report["total_cases"] >= 30
    assert audit_report["required_columns"] is True
    assert audit_report["duplicate_ids"] is True
    assert audit_report["missing_titles"] is True
    assert audit_report["missing_concepts"] is True
    assert audit_report["missing_severities"] is True