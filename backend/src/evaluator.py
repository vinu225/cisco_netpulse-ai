"""Automated Benchmark Evaluator & Accuracy Assessor for NetPulse AI Platform."""

import logging
from typing import List, Dict, Any
from src.models import Case, Evidence, DiagnosisResult
from src.data_loader import load_cases, get_case
from src.evidence_parser import load_evidence, create_all_placeholders
from src.diagnosis import diagnose, filter_candidate_cases

logger = logging.getLogger(__name__)


def evaluate_all_cases() -> Dict[str, Any]:
    """Execute batch AI diagnostic evaluation against active dataset evidence files."""
    create_all_placeholders()
    
    scenario_list = load_cases()
    evaluation_records = []
    successful_matches = 0
    evaluated_count = 0
    
    for case_item in scenario_list:
        telemetry_data = load_evidence(case_item.case_id)
        if not telemetry_data or telemetry_data.is_empty():
            logger.info(f"Skipping telemetry evaluation for Case #{case_item.case_id}: missing log file")
            continue
            
        evaluated_count += 1
        try:
            diagnosis_output = diagnose(telemetry_data, case_item.case_id)
            match_passed = _compare_faults(diagnosis_output.predicted_fault, case_item.expected_fault)
            
            if match_passed:
                successful_matches += 1
                
            evaluation_records.append({
                "case_id": case_item.case_id,
                "title": case_item.title,
                "expected": case_item.expected_fault,
                "predicted": diagnosis_output.predicted_fault,
                "confidence": diagnosis_output.confidence,
                "correct": match_passed
            })
            logger.info(f"Case #{case_item.case_id}: {'[PASS]' if match_passed else '[FAIL]'} (Confidence: {diagnosis_output.confidence:.2f})")
        except Exception as err:
            logger.error(f"Execution error evaluating Case #{case_item.case_id}: {err}")
            evaluation_records.append({
                "case_id": case_item.case_id,
                "title": case_item.title,
                "expected": case_item.expected_fault,
                "predicted": f"ERROR: {err}",
                "confidence": 0.0,
                "correct": False
            })
            
    accuracy_rate = (successful_matches / evaluated_count) if evaluated_count > 0 else 0.0
    
    return {
        "total_evaluated": evaluated_count,
        "correct": successful_matches,
        "accuracy": accuracy_rate,
        "results": evaluation_records
    }


def _compare_faults(predicted_fault: str, expected_fault: str) -> bool:
    """Evaluate alignment between AI predicted title and ground truth fault description."""
    norm_pred = predicted_fault.strip().lower()
    norm_exp = expected_fault.strip().lower()
    return (norm_exp in norm_pred) or (norm_pred in norm_exp)


def print_evaluation_report(report: Dict[str, Any]) -> None:
    """Print terminal evaluation metric summary table."""
    print("\n" + "=" * 65)
    print("NETPULSE AI TELEMETRY EVALUATION REPORT")
    print("=" * 65)
    print(f"Total Scenarios Evaluated : {report['total_evaluated']}")
    print(f"Successful Diagnoses     : {report['correct']}")
    print(f"Model Precision Score    : {report['accuracy']:.2%}")
    print()
    print("ID   | Expected Fault                           | Predicted Fault                          | Result")
    print("-" * 65)
    
    for item in report["results"]:
        status_flag = "[PASS]" if item["correct"] else "[FAIL]"
        pred_text = item["predicted"][:38] + ".." if len(item["predicted"]) > 40 else item["predicted"]
        exp_text = item["expected"][:38] + ".." if len(item["expected"]) > 40 else item["expected"]
        print(f"{item['case_id']:<4} | {exp_text:<40} | {pred_text:<40} | {status_flag}")