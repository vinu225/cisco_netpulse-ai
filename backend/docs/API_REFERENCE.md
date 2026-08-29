# NetPulse AI - REST API & Telemetry Reference

Base Server URL: `http://localhost:8000`

---

## Interactive Web User Interfaces

| Route Path | HTTP Method | System View Description |
| :--- | :--- | :--- |
| `/` | `GET` | Telemetry System Overview & Real-Time Engine Dashboard |
| `/diagnose` | `GET` | AI Incident Diagnostic Console & Verification Workbench |
| `/cases` | `GET` | Known Fault Matrix Matrix & Multi-Parameter Query UI |
| `/review` | `GET` | Human-in-the-Loop Verification Audit Log Page |
| `/dashboard` | `GET` | System Performance Analytics & Chart.js Visualizations |

---

## API Endpoints Reference

### 1. Engine Health & Status
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "NetPulse AI Telemetry Core",
  "engine": "Cisco Diagnostic Model v2.5"
}
```

---

### 2. Real-Time System Metrics & Latency
```http
GET /api/system/metrics
```
**Response:**
```json
{
  "engine_status": "ONLINE",
  "active_cases_loaded": 32,
  "total_reviews_logged": 5,
  "accuracy_score": "96.4%",
  "active_nodes_monitored": 128,
  "rule_checks_enabled": 10,
  "latency_ms": 142
}
```

---

### 3. Multi-Parameter Case Search
```http
GET /api/cases/search?q=VLAN&concept=VLAN&severity=High
```
**Response:**
```json
[
  {
    "case_id": 5,
    "title": "Missing VLAN",
    "concept": "VLAN",
    "severity": "High",
    "osi_layer": "Layer 2"
  }
]
```

---

### 4. Fetch All Scenarios
```http
GET /api/cases
```
**Response:**
```json
[
  {
    "case_id": 1,
    "title": "Wrong IP Address",
    "concept": "IP Addressing",
    "severity": "Medium",
    "osi_layer": "Layer 3"
  }
]
```

---

### 5. Execute AI Telemetry Diagnosis
```http
POST /api/diagnose
Content-Type: application/json

{
  "case_id": 1,
  "evidence_text": "[ipconfig]\nIPv4 Address: 192.168.2.10\nSubnet Mask: 255.255.255.0\nDefault Gateway: 0.0.0.0"
}
```
**Response:**
```json
{
  "success": true,
  "diagnosis": {
    "predicted_fault": "Wrong IP Address",
    "confidence": 0.95,
    "reasoning_summary": "Host IP address 192.168.2.10 is configured on incorrect network subnet.",
    "evidence_used": ["ipconfig"],
    "recommended_fix": "Change PC IP address to 192.168.1.X",
    "commands": [
      "interface FastEthernet0/1",
      "ip address 192.168.1.10 255.255.255.0"
    ],
    "needs_more_evidence": false,
    "risk_score": 35,
    "impact_radius": "Local Host"
  },
  "rule_results": [
    {
      "check": "wrong_subnet_mask",
      "status": "FAIL",
      "message": "Subnet mask misconfiguration detected",
      "severity": "HIGH"
    }
  ]
}
```

---

### 6. Log Engineer Verification Audit
```http
POST /api/review
Content-Type: application/json

{
  "case_id": 1,
  "decision": "Accepted",
  "notes": "Verified configuration against Packet Tracer lab"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Review logged"
}
```

---

### 7. WebSocket Live Telemetry Feed
```
WS /ws
```
Sends live JSON broadcast payloads whenever a diagnosis or human audit review is executed.