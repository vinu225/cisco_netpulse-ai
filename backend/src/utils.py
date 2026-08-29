"""Utility helpers and logging system setup for NetPulse AI Console."""

import logging
import sys
from typing import List


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured system logging handlers and formatters."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
    
    # Silence verbose third-party HTTP transport loggers
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def print_menu() -> None:
    """Print terminal interactive menu banner."""
    print("\n" + "=" * 45)
    print("NetPulse AI - Cisco Diagnostic Workstation")
    print("=" * 45)
    print("1. List All Network Cases")
    print("2. Run Interactive AI Telemetry Diagnosis")
    print("3. Audit Dataset Integrity")
    print("4. Benchmark Diagnostic Model Accuracy")
    print("5. Exit System Console")
    print()


def print_cases(cases: List[Any]) -> None:
    """Print a clean formatted tabular summary of network cases."""
    print(f"\n{'ID':<4} | {'Fault Title':<35} | {'Concept Taxonomy':<30} | {'Severity'}")
    print("-" * 85)
    for case_item in cases:
        short_title = case_item.title[:34] if len(case_item.title) > 34 else case_item.title
        short_concept = case_item.concept[:29] if len(case_item.concept) > 29 else case_item.concept
        print(f"{case_item.case_id:<4} | {short_title:<35} | {short_concept:<30} | {case_item.severity}")


def get_multiline_input(prompt: str) -> str:
    """Collect multi-line CLI text input until an empty newline is submitted."""
    print(prompt)
    print("(Submit an empty blank line when finished entering telemetry text)")
    collected_lines = []
    while True:
        try:
            user_line = input()
            if not user_line.strip():
                break
            collected_lines.append(user_line)
        except (EOFError, KeyboardInterrupt):
            break
    return "\n".join(collected_lines)