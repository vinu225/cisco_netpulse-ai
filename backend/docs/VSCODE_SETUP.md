# NetPulse AI - VS Code Development Environment Setup

## Recommended Extensions
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Jinja (`samuelcolvin.jinjahtml`)

---

## `.vscode/settings.json` Configuration

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true
}
```

---

## `.vscode/launch.json` Debugging Configurations

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "NetPulse FastAPI Server",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "NetPulse Telemetry CLI",
      "type": "python",
      "request": "launch",
      "module": "main_cli",
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Pytest Suite",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests", "-v"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```