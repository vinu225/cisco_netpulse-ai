# NetPulse AI Testing & Quality Assurance Specifications

## Test Suite Architecture

```
backend/tests/
├── test_data_loader.py    # Dataset loading & schema integrity tests
├── test_diagnosis.py      # Candidate concept keyword filtering & Pydantic schema validation
└── test_evaluator.py      # Fuzzy fault string comparison tests
```

---

## Executing Unit Tests

### Execute Entire Test Suite
```powershell
cd backend
$env:PYTHONPATH="."; pytest tests/ -v
```

### File-Specific Testing
```powershell
pytest tests/test_data_loader.py -v
pytest tests/test_diagnosis.py -v
pytest tests/test_evaluator.py -v
```

### Targeted Single Test Execution
```powershell
pytest tests/test_diagnosis.py::test_filter_candidate_cases_dhcp_keyword -v
```

---

## Integration Verification Script

```powershell
python scripts/test_integration.py
```

Tests:
1. Static rule engine execution on telemetry input.
2. AI diagnosis inference pipeline.
3. Telemetry analytics dashboard rendering.

---

## Test Data Integrity & Schema Validation

| Benchmark Data File | Description |
| :--- | :--- |
| `data/cases.csv` | 32 Cisco Packet Tracer ground-truth fault scenarios |
| `data/evidence/case_XX.txt` | Structured CLI show output & ipconfig evidence logs |
| `data/human_review_log.md` | Human verification audit log |