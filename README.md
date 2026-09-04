# FDA FAERS Signal Disproportionality

> **Domain:** Pharmacovigilance & Drug Safety Signal Detection
> **Reference Guidelines & Standards:** `WHO-UMC & FDA FAERS Signal Detection`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

FDA FAERS Signal Disproportionality is a pharmacovigilance signal detection system that analyzes the FDA Adverse Event Reporting System (FAERS) data using proven disproportionality methods:

- **Proportional Reporting Ratio (PRR)**: Measures the proportion of reports for a specific adverse event with a drug compared to all drugs.
- **Reporting Odds Ratio (ROR)**: Alternative measure using odds ratios for signal detection.
- **Bayesian Information Component (IC)**: Bayesian confidence propagation neural network approach.

The system provides a multi-worker agent architecture that evaluates task payloads against domain-specific thresholds, generates alerts with urgency classifications, and maintains a tamper-evident HMAC-SHA256 audit trail.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with WHO-UMC & FDA FAERS Signal Detection formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated clinical action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection with Zero-PHI outbound protection.
- **Multi-Worker Agent Architecture**: Specialized workers (InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker) for comprehensive signal evaluation.

---

## 💻 Installation

```bash
pip install -e .
```

### Dependencies
- Python >= 3.9
- FastAPI & uvicorn (for REST API server)
- Pydantic v2 (for data validation)
- pytest (for testing)

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (max 128 chars)
- `--target`: Entity or patient key identifier (max 128 chars)
- `--primary`: Primary measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--critical`: Emergency escalation flag (boolean)
- `--status`: Status code or phenotype descriptor (max 64 chars)

### Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task / case identifier | Required |
| `target_identifier` | string | Entity or target identifier | Required |
| `primary_metric` | float | Primary domain measurement or score | Required |
| `secondary_metric` | float | Secondary kinetic or confidence score | Optional (default: 0.0) |
| `is_critical_flag` | boolean | Emergency escalation flag | Optional (default: false) |
| `status_descriptor` | string | Status code or phenotype descriptor | Optional (default: "NOMINAL") |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB patterns, and patient identifiers from outbound data.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Requires `AUDIT_SECRET_KEY` environment variable (min 16 characters).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables

| Variable | Required | Description |
|:---------|:---------|:------------|
| `AUDIT_SECRET_KEY` | Yes (for production) | Secret key for HMAC-SHA256 audit trail (min 16 chars) |
| `MODEL_PROVIDER` | No | LLM provider: `mock`, `ollama`, `claude`, `openai` (default: mock) |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 100
```

Run the security audit via CI:

```bash
python -c "from agents.base import AuditLogger; assert AuditLogger.verify_integrity(); print('Security Audit Passed!')"
```

---

## 🐳 Container Deployment

```bash
docker build -t fda-faers-signal-disproportionality .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key-here fda-faers-signal-disproportionality
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secure-key-here docker-compose up
```

---

## 📁 Project Structure

```
fda-faers-signal-disproportionality/
├── agents/                  # Enterprise agent architecture
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, HMAC audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM client factory
│   ├── metrics.py          # Prometheus metrics collector
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry broadcaster
├── faers_sentinel/         # Frontier disproportionality engine
│   ├── models.py           # Data models
│   ├── engine.py           # Core algorithmic engine
│   ├── agents.py           # Coordinator and sub-agents
│   ├── cli.py              # Frontier CLI
│   └── server.py           # Frontier FastAPI server
├── tests/                  # Test suite
├── web/index.html          # Operations console UI
├── cli.py                  # Main CLI entry point
├── enrichment.py           # Feature enrichment engines
├── simulator.py            # High-throughput simulation
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container build
└── docker-compose.yml      # Container orchestration
```
