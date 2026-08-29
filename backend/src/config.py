"""Global Environment & System Settings for NetPulse AI Telemetry Engine."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration from local .env
load_dotenv()

# System Root & Data Directory Locations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CASES_CSV = DATA_DIR / "cases.csv"
EVIDENCE_DIR = DATA_DIR / "evidence"

# OpenRouter & LLM Service Credentials
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Telemetry Inference Engine Hyperparameters
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))