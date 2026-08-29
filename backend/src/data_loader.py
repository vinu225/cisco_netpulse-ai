"""Dataset loader and integrity validator for NetPulse AI telemetry benchmarks."""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.config import CASES_CSV
from src.models import Case, Severity


def load_cases() -> List[Case]:
    """Parse and load all troubleshooting scenarios from the target dataset CSV."""
    if not CASES_CSV.exists():
        return []
    
    data_frame = pd.read_csv(CASES_CSV)
    parsed_cases: List[Case] = []
    
    for idx, row_data in data_frame.iterrows():
        case_item = _row_to_case(row_data)
        if case_item is not None:
            parsed_cases.append(case_item)
            
    return parsed_cases


def _row_to_case(row: pd.Series) -> Optional[Case]:
    """Internal converter to transform pandas Series record into Pydantic Case model."""
    try:
        cid = int(row.iloc[0])
        fault_desc = str(row["expected_fault"]).strip() if pd.notna(row["expected_fault"]) else ""
        
        # Fallback parsing for special legacy case formatting
        if not fault_desc and cid == 11:
            raw_output = str(row["show_outputs"]) if pd.notna(row["show_outputs"]) else ""
            lowered = raw_output.lower()
            if "expected_fault:" in lowered:
                start_pos = lowered.find("expected_fault:") + len("expected_fault:")
                fault_desc = raw_output[start_pos:].strip()
        
        severity_label = str(row["severity"]).strip().capitalize() if pd.notna(row["severity"]) else "Medium"
        try:
            case_severity = Severity(severity_label)
        except ValueError:
            case_severity = Severity.MEDIUM
        
        return Case(
            case_id=cid,
            title=str(row["title"]).strip() if pd.notna(row["title"]) else f"Case {cid}",
            topology=str(row["topology"]).strip() if pd.notna(row["topology"]) else "",
            symptom=str(row["symptom"]).strip() if pd.notna(row["symptom"]) else "",
            topology_note=str(row["topology_note"]).strip() if pd.notna(row["topology_note"]) else "",
            show_outputs=str(row["show_outputs"]).strip() if pd.notna(row["show_outputs"]) else "",
            expected_fault=fault_desc,
            osi_layer=str(row["osi_layer"]).strip() if pd.notna(row["osi_layer"]) else "",
            concept=str(row["concept"]).strip() if pd.notna(row["concept"]) else "",
            severity=case_severity
        )
    except Exception as err:
        print(f"Warning: Failed to load case row index {row.iloc[0]}: {err}")
        return None


def get_case(case_id: int) -> Optional[Case]:
    """Locate a single case record by its unique numeric case ID."""
    all_records = load_cases()
    return next((record for record in all_records if record.case_id == case_id), None)


def get_cases_by_concept(concept: str) -> List[Case]:
    """Filter records matching concept query substring."""
    query = concept.strip().lower()
    return [item for item in load_cases() if query in item.concept.lower()]


def get_cases_by_title(title: str) -> List[Case]:
    """Filter records matching title query substring."""
    query = title.strip().lower()
    return [item for item in load_cases() if query in item.title.lower()]


def validate_dataset() -> Dict[str, Any]:
    """Execute structural audit on the dataset CSV and return validation statistics."""
    df = pd.read_csv(CASES_CSV)
    loaded_records = load_cases()
    
    validation_summary = {
        "total_cases": len(loaded_records),
        "required_columns": True,
        "duplicate_ids": True,
        "missing_titles": True,
        "missing_expected_faults": True,
        "missing_concepts": True,
        "missing_severities": True,
        "case_ids_range": True,
        "issues": []
    }
    
    expected_fields = ["case_id", "title", "topology", "symptom", "topology_note",
                       "show_outputs", "expected_fault", "osi_layer", "concept", "severity"]
    absent_fields = [f for f in expected_fields if f not in df.columns]
    if absent_fields:
        validation_summary["required_columns"] = False
        validation_summary["issues"].append(f"Missing CSV columns: {absent_fields}")
    
    id_list = [r.case_id for r in loaded_records]
    if len(id_list) != len(set(id_list)):
        validation_summary["duplicate_ids"] = False
        validation_summary["issues"].append("Detected duplicate case IDs in dataset")
    
    expected_range = set(range(1, len(loaded_records) + 1))
    if set(id_list) != expected_range and len(loaded_records) < 30:
        validation_summary["case_ids_range"] = False
        missing_ids = expected_range - set(id_list)
        validation_summary["issues"].append(f"Missing case IDs: {sorted(missing_ids)}")
    
    unnamed_cases = [r.case_id for r in loaded_records if not r.title]
    if unnamed_cases:
        validation_summary["missing_titles"] = False
        validation_summary["issues"].append(f"Cases missing title attribute: {unnamed_cases}")
        
    faultless_cases = [r.case_id for r in loaded_records if not r.expected_fault]
    if faultless_cases:
        validation_summary["missing_expected_faults"] = False
        validation_summary["issues"].append(f"Cases missing expected_fault attribute: {faultless_cases}")
        
    conceptless_cases = [r.case_id for r in loaded_records if not r.concept]
    if conceptless_cases:
        validation_summary["missing_concepts"] = False
        validation_summary["issues"].append(f"Cases missing concept classification: {conceptless_cases}")
        
    unassigned_severities = [r.case_id for r in loaded_records if not r.severity]
    if unassigned_severities:
        validation_summary["missing_severities"] = False
        validation_summary["issues"].append(f"Cases missing severity rating: {unassigned_severities}")
        
    is_valid = all([
        validation_summary["required_columns"],
        validation_summary["duplicate_ids"],
        validation_summary["missing_titles"],
        validation_summary["missing_expected_faults"],
        validation_summary["missing_concepts"],
        validation_summary["missing_severities"]
    ])
    validation_summary["status"] = "VALID" if is_valid else "INVALID"
    return validation_summary


def print_validation_report(report: Dict[str, Any]) -> None:
    """Print clean terminal diagnostic summary of dataset health."""
    print("\nNetPulse Dataset Validation Audit")
    print("=" * 45)
    print(f"Total Scenarios Loaded : {report['total_cases']}")
    print(f"Schema Structure       : {'PASS' if report['required_columns'] else 'FAIL'}")
    print(f"Unique Key ID Check    : {'PASS' if report['duplicate_ids'] else 'FAIL'}")
    print(f"Title Completeness     : {'PASS' if report['missing_titles'] else 'FAIL'}")
    print(f"Fault Label Presence   : {'PASS' if report['missing_expected_faults'] else 'FAIL'}")
    print(f"Concept Taxonomy Check : {'PASS' if report['missing_concepts'] else 'FAIL'}")
    print(f"Severity Check         : {'PASS' if report['missing_severities'] else 'FAIL'}")
    print(f"Overall Status         : [{report['status']}]")
    if report["issues"]:
        print("\nIdentified Data Anomalies:")
        for issue in report["issues"]:
            print(f"  • {issue}")