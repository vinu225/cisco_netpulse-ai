# NetPulse AI Troubleshooting & Operational Diagnostics

## Common Operational Scenarios & Solutions

### 1. OpenRouter API Key Missing
**Symptom**: `ValueError: OPENROUTER_API_KEY environment variable is unconfigured`  
**Solution**:
1. Copy `.env.example` to `.env` in `backend/`.
2. Add your OpenRouter API key: `OPENROUTER_API_KEY=sk-or-v1-...`

---

### 2. FastAPI Web Server Import Error
**Symptom**: `ModuleNotFoundError: No module named 'src'`  
**Solution**:
Execute commands from `backend/` working directory with `PYTHONPATH`:
```powershell
$env:PYTHONPATH="."; python main.py
```

---

### 3. OpenRouter Rate Limit / Model Failover
**Symptom**: `HTTP 429 Rate Limit Exceeded`  
**Solution**:
NetPulse AI automatically fails over across the model catalog (`google/gemma-2-9b-it:free`, `meta-llama/llama-3.2-3b-instruct:free`, `microsoft/phi-3-mini-128k-instruct:free`).

---

### 4. WebSocket Disconnection in Cyber UI
**Symptom**: Real-time status badge shows `Engine Reconnecting`  
**Solution**:
Ensure FastAPI server process is active on `http://127.0.0.1:8000`.