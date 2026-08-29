"""Prompt engineering templates for NetPulse AI Telemetry & Diagnostic Engine."""

from typing import List
from src.models import Case, Evidence


SYSTEM_PROMPT = """You are NetPulse AI, an expert Cisco Network Diagnostics System. Your purpose is to analyze telemetry logs, CLI interface outputs, and ping diagnostic reports to identify the exact fault category.

CORE DIAGNOSTIC RULES:
1. Base your reasoning STRICTLY on the supplied evidence. Do not hallucinate unverified state.
2. Match the symptoms against ONE of the known fault scenarios listed.
3. Provide a concise technical explanation citing specific log artifacts.
4. Calculate an objective confidence metric between 0.00 and 1.00.
5. Detail actionable Cisco IOS remediation commands required to resolve the issue.
6. If evidence is ambiguous or incomplete, set needs_more_evidence=true.

REQUIRED JSON OUTPUT FORMAT (Strict JSON only, no markdown wrappers):
{
  "predicted_fault": "Title of predicted fault scenario",
  "confidence": 0.95,
  "reasoning_summary": "Detailed technical analysis citing specific CLI parameters",
  "evidence_used": ["Evidence log snippet 1", "Evidence log snippet 2"],
  "recommended_fix": "Clear step-by-step remediation procedure",
  "commands": ["configure terminal", "interface GigabitEthernet0/1", "no shutdown"],
  "needs_more_evidence": false
}"""


def build_case_list_prompt(cases: List[Case]) -> str:
    """Format candidate cases into structured prompt reference block."""
    prompt_lines = []
    for item in cases:
        prompt_lines.append(f"Case #{item.case_id}: {item.title}")
        prompt_lines.append(f"  Fault Profile : {item.expected_fault}")
        prompt_lines.append(f"  Networking Concept : {item.concept}")
        prompt_lines.append(f"  Severity Impact    : {item.severity}")
        prompt_lines.append("")
    return "\n".join(prompt_lines)


def build_diagnosis_prompt(evidence: Evidence, candidate_cases: List[Case]) -> str:
    """Assemble complete user diagnostic prompt payload for LLM inference."""
    raw_dict = evidence.to_dict()
    
    if raw_dict:
        sections = ["NETPULSE TELEMETRY EVIDENCE:"]
        for attr_key, attr_val in raw_dict.items():
            formatted_title = attr_key.replace("_", " ").upper()
            sections.append(f"\n[=== {formatted_title} ===]")
            sections.append(attr_val.strip())
        telemetry_block = "\n".join(sections)
    else:
        telemetry_block = "NETPULSE TELEMETRY EVIDENCE:\nNo telemetry logs provided."
    
    candidate_block = build_case_list_prompt(candidate_cases)
    
    return f"""{telemetry_block}

CANDIDATE NETWORK FAULT MATRIX:
{candidate_block}

Evaluate the telemetry logs above against the candidate matrix. Return ONLY the formatted JSON response."""


def build_evaluation_prompt(evidence: Evidence, candidate_cases: List[Case]) -> str:
    """Construct evaluation prompt payload."""
    return build_diagnosis_prompt(evidence, candidate_cases)