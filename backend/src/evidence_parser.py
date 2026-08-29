"""Telemetry evidence parser and log normalizer for NetPulse AI Engine."""

from pathlib import Path
from typing import Optional, Dict
from src.config import EVIDENCE_DIR
from src.models import Evidence


def load_evidence(case_id: int) -> Optional[Evidence]:
    """Retrieve telemetry log file for specified case ID."""
    target_path = EVIDENCE_DIR / f"case_{case_id:02d}.txt"
    if not target_path.exists():
        return None
    
    file_raw_text = target_path.read_text(encoding="utf-8")
    return parse_evidence_file(file_raw_text, case_id)


def parse_evidence_file(content: str, case_id: int) -> Evidence:
    """Parse raw multiline text logs into a structured Evidence model instance."""
    evidence_obj = Evidence(case_id=case_id)
    
    section_map: Dict[str, str] = {
        "user_description": "user_description",
        "ping_results": "ping_results",
        "ipconfig": "ipconfig",
        "show_ip_interface_brief": "show_ip_interface_brief",
        "show_running_config": "show_running_config",
        "show_vlan_brief": "show_vlan_brief",
        "show_interfaces_trunk": "show_interfaces_trunk",
        "show_ip_route": "show_ip_route",
        "show_access_lists": "show_access_lists",
        "show_ip_nat_translations": "show_ip_nat_translations",
        "other_cli_output": "other_cli_output",
    }
    
    active_attr: Optional[str] = None
    accumulated_lines: list[str] = []
    
    for raw_line in content.splitlines():
        line_clean = raw_line.strip().lower()
        matched_attr: Optional[str] = None
        
        for section_key, attr_name in section_map.items():
            if line_clean.startswith(f"[{section_key}]") or line_clean.startswith(f"=== {section_key} ==="):
                matched_attr = attr_name
                break
                
        if matched_attr is not None:
            if active_attr and accumulated_lines:
                setattr(evidence_obj, active_attr, "\n".join(accumulated_lines).strip())
            active_attr = matched_attr
            accumulated_lines = []
        else:
            accumulated_lines.append(raw_line)
            
    if active_attr and accumulated_lines:
        setattr(evidence_obj, active_attr, "\n".join(accumulated_lines).strip())
        
    return evidence_obj


def create_placeholder_evidence(case_id: int) -> None:
    """Generate default placeholder telemetry text file if missing."""
    file_path = EVIDENCE_DIR / f"case_{case_id:02d}.txt"
    if file_path.exists():
        return
        
    placeholder_template = """[user_description]
EVIDENCE NOT COLLECTED YET

[ping_results]
EVIDENCE NOT COLLECTED YET

[ipconfig]
EVIDENCE NOT COLLECTED YET

[show_ip_interface_brief]
EVIDENCE NOT COLLECTED YET

[show_running_config]
EVIDENCE NOT COLLECTED YET

[show_vlan_brief]
EVIDENCE NOT COLLECTED YET

[show_interfaces_trunk]
EVIDENCE NOT COLLECTED YET

[show_ip_route]
EVIDENCE NOT COLLECTED YET

[show_access_lists]
EVIDENCE NOT COLLECTED YET

[show_ip_nat_translations]
EVIDENCE NOT COLLECTED YET

[other_cli_output]
EVIDENCE NOT COLLECTED YET
"""
    file_path.write_text(placeholder_template, encoding="utf-8")


def create_all_placeholders() -> None:
    """Ensure placeholder evidence files exist across all cases."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    for cid in range(1, 35):
        create_placeholder_evidence(cid)


def normalize_evidence(evidence: Evidence) -> str:
    """Format structured evidence into normalized telemetry string for AI prompting."""
    blocks = []
    dict_payload = evidence.to_dict()
    
    for field_name, text_val in dict_payload.items():
        if text_val and text_val.strip():
            header_title = field_name.replace("_", " ").title()
            blocks.append(f"=== {header_title} ===\n{text_val.strip()}\n")
            
    return "\n".join(blocks) if blocks else "No evidence provided."