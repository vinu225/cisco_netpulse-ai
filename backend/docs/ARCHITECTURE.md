# NetPulse AI Architecture Specifications

## System Architecture & Component Design

NetPulse AI is a **next-generation network intelligence platform** for Cisco Packet Tracer labs combining:
- **Phase-1 Deterministic Rule Engine** (Instant static configuration inspection)
- **Multi-Stage AI Telemetry Engine** (OpenRouter LLM inference with automated fallback model sequence)
- **Dynamic Risk & Blast Radius Calculator** (Quantitative risk scoring from 0 to 100)
- **Cyber Glassmorphic UI & Real-Time Broadcast** (WebSockets, dark mode design system, Chart.js metrics)
- **Human-in-the-Loop Audit Logger** (Persistent verification audit workflow)

---

## Technical Data Flow Pipeline

```
┌─────────────────────────────────────────┐
│ Cisco Packet Tracer / Real Device Logs  │  (CLI Show Outputs, Ping Results, Subnet Masks)
└────────────────────┬────────────────────┘
                     │ Manual / Simulated Log Ingestion
                     ▼
┌─────────────────────────────────────────┐
│     NetPulse Telemetry Ingestion        │  data/evidence/case_XX.txt
│      (Structured CLI Block Parser)      │  [user_description], [ipconfig], [show_running_config]
└────────────────────┬────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   NETPULSE AI DIAGNOSTIC ENGINE                        │
├────────────────────────────────────────────────────────────────────────┤
│  1. PHASE-1 RULE ENGINE (Deterministic Verification)                  │
│     ├─ 10 Inspection Rules: Subnet Mask, Gateway, Interface State, etc.│
│     └─ Output: Rule Findings & Violation Alerts                        │
│                                                                        │
│  2. TELEMETRY KEYWORD & CONCEPT FILTER                                 │
│     ├─ Maps raw telemetry tokens → 32 NetPulse fault categories        │
│     └─ Output: Scoped Scenario Candidates                              │
│                                                                        │
│  3. DYNAMIC PROMPT BUILDER                                             │
│     ├─ System Instructions + Output Format JSON Schema                 │
│     ├─ User Telemetry Logs + Scoped Candidate Matrix                   │
│     └─ Output: Enforced Context Prompt Payload                         │
│                                                                        │
│  4. OPENROUTER INFERENCE ENGINE & FALLBACK CHAIN                       │
│     ├─ Primary: OpenRouter Auto Select / Gemma Models                  │
│     ├─ Fallback Catalog: Gemma-2, Llama-3.2, Phi-3                      │
│     ├─ Response Validation: Enforced JSON Object Parsing               │
│     └─ Output: DiagnosisResult Payload                                 │
│                                                                        │
│  5. RISK & BLAST RADIUS CALCULATOR                                     │
│     ├─ Computes Risk Score (0-100) based on rules & confidence         │
│     └─ Scope Determination: Local Host | VLAN Scope | Router Subnet   │
│                                                                        │
│  6. ENGINEER VERIFICATION AUDIT WORKFLOW                               │
│     ├─ Status: Accepted / Edited / Rejected                            │
│     └─ Persistence: data/human_review_log.md                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Core System Modules (`backend/src/`)

### 1. Data Layer (`src/data_loader.py`)
- `load_cases()`: Loads dataset records from CSV file.
- `validate_dataset()`: Executes schema integrity checks on dataset file.
- `get_case(id)`: Single case lookup by ID.
- `get_cases_by_concept()` / `get_cases_by_title()`: Substring query filters.

### 2. Evidence Parser (`src/evidence_parser.py`)
- `parse_evidence_file()`: Converts raw CLI text into structured Evidence model.
- `load_evidence(case_id)`: Loads case telemetry file.
- `normalize_evidence()`: Formats evidence blocks for LLM prompt context.

### 3. Static Rule Checker (`src/rule_checker.py`)
Deterministic checks executed prior to AI inference:
| Inspection Rule | Target Violation Detected |
| :--- | :--- |
| `wrong_subnet_mask` | Non-standard mask configuration on subnet |
| `gateway_mismatch` | Default Gateway residing outside host subnet |
| `interface_down` | Port interface in 'administratively down' state |
| `missing_vlan` | Unconfigured or missing 802.1Q VLAN entry |
| `missing_route` | Unreachable destination network missing from routing table |
| `dhcp_pool_missing` | Missing DHCP pool or APIPA (169.254.x.x) autoconfiguration |
| `dhcp_wrong_network` | DHCP address scope configured for wrong subnet |
| `dhcp_wrong_gateway` | DHCP default-router option providing wrong gateway |
| `acl_blocking` | Access Control List explicit deny statement dropping traffic |
| `nat_missing` | Missing or incomplete IP NAT translation configuration |

### 4. Diagnostic Pipeline (`src/diagnosis.py`)
Orchestrates static rules, candidate concept filtering, AI inference, and dynamic risk scoring (`calc_risk`, `impact_radius`).

### 5. OpenRouter Client (`src/llm_client.py`)
Manages OpenAI API client instance connected to OpenRouter base URL with automatic fallback model selection and JSON response repair.

---

## Pydantic Data Models (`src/models.py`)

```python
class Case(BaseModel):
    case_id: int
    title: str
    topology: str
    symptom: str
    topology_note: str
    show_outputs: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: Severity  # Low | Medium | High
    urgency_level: Optional[str] = "Standard"
    tags: Optional[List[str]] = []

class DiagnosisResult(BaseModel):
    case_id: int
    predicted_fault: str
    confidence: float
    reasoning_summary: str
    evidence_used: List[str]
    recommended_fix: str
    commands: List[str]
    needs_more_evidence: bool
    risk_score: Optional[int] = 50
    impact_radius: Optional[str] = "Single Subnet"
```

---

## Technical Security & Responsible AI Controls
1. **Human Audit Mandatory**: Fix commands must be verified by a human network engineer before deployment.
2. **Deterministic Rules First**: Fast local rule execution prevents unnecessary API calls and catches static misconfigurations immediately.
3. **Environment Security**: OpenRouter API keys stored in local `.env` configuration.