"""Standalone CSV dataset inspector script for NetPulse AI Engine."""

import sys
from pathlib import Path

# Add backend root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import CASES_CSV
from src.data_loader import validate_dataset, print_validation_report

def main():
    print(f"Inspecting target CSV file: {CASES_CSV}")
    if not CASES_CSV.exists():
        print("Error: Target dataset file does not exist!")
        return

    report = validate_dataset()
    print_validation_report(report)

if __name__ == "__main__":
    main()