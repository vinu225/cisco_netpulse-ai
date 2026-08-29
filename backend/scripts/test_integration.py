"""Integration verification script for NetPulse AI Telemetry Pipeline."""

import sys
from pathlib import Path

# Add backend root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.evidence_parser import load_evidence
from src.diagnosis import diagnose, format_diagnosis
from src.rule_checker import run_rule_checker
from src.human_review import HumanReview
from src.dashboard import Dashboard

def run_integration_test():
    print("==================================================")
    print("NetPulse AI Engine Integration & Diagnostics Test")
    print("==================================================")

    # Test Case 1 telemetry load
    telemetry = load_evidence(1)
    if not telemetry:
        print("Error: Failed to load telemetry for Case #1")
        return

    print('\n[1] Deterministic Static Rule Check Audit:')
    rule_findings = run_rule_checker(telemetry)
    if rule_findings:
        for finding in rule_findings:
            print(f"  • [{finding.get('severity', 'HIGH')}] {finding['check']}: {finding['message']}")
    else:
        print("  • No static rule violations detected.")

    print('\n[2] AI Diagnostics Inference Pipeline:')
    diagnosis_output = diagnose(telemetry, 1)
    print(format_diagnosis(diagnosis_output))

    print('\n[3] Telemetry Analytics Dashboard Generation:')
    dash = Dashboard()
    output_path = dash.generate()
    print(f"  • Dashboard successfully generated at: {output_path}")

if __name__ == "__main__":
    run_integration_test()