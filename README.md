# SecureScope

**Healthcare Network Exposure, Threat Detection & Incident Response Platform**
*Discover Exposure. Detect Threats. Respond Faster.*

SecureScope is a defensive-only cybersecurity training dashboard built around a single
fictional scenario — **Problem 4: "The Helpful Caller at the Community Hospital."**
It is a working prototype, not a static mockup: a real FastAPI + PostgreSQL backend
drives a React/Vite/Tailwind SOC-style dashboard.

> ⚠️ **This is a defensive training tool.** It performs no exploitation, credential
> theft, phishing, or destructive actions. See [Security Limitations](#security-limitations).

---

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────┐        ┌──────────────┐
│  Frontend (React)     │ HTTP  │  Backend (FastAPI)         │  SQL  │  PostgreSQL  │
│  Vite + Tailwind      │──────▶│  scanner / risk engine /   │──────▶│              │
│  SOC dashboard         │◀──────│  detection / correlation /│◀──────│              │
│  :5173                │       │  audit — :8000             │       │  :5432       │
└─────────────────────┘        └──────────────────────────┘        └──────────────┘
```

Backend modules map directly to Problem 4's requirements:

| Module | File | Responsibility |
|---|---|---|
| Scanner | `app/services/scanner.py` | Safe, non-destructive TCP connect against a fixed whitelisted port set |
| Risk engine | `app/services/risk_engine.py` | Static, auditable service → risk/reason/controls mapping |
| Knowledge base | `app/services/knowledge_base.py` | The 4 MITRE-mapped attack techniques + permanent defense recommendations |
| Detection engine | `app/services/detection_engine.py` | 4 rule-based detections (no ML) |
| Correlation engine | `app/services/correlation_engine.py` | Chains related events into a single incident |
| Audit | `app/services/audit.py` | Writes every state-changing action to `audit_logs` |

## Problem-statement mapping

| Problem 4 requirement | Where it's implemented |
|---|---|
| Assess a URL/IP, identify reachable services | Target Assessment card → `POST /api/scan` → `scanner.py` |
| Distinguish open service / exposure / vulnerability | `finding_type` on each `Finding` (never fabricates "confirmed vulnerability") |
| Risk + security significance per exposure | Network Exposure table, expandable risk detail |
| Attack technique explanation (Impersonation, Account Discovery, Web Protocols, Exfiltration Over C2) | Threat & Attack Techniques accordion, seeded from `knowledge_base.py` |
| Monitor defensive security events | Security Events SOC table, `POST /api/test-events` |
| Detect suspicious auth/access/config/endpoint/transfer behavior | `detection_engine.py` Rules 1–4 |
| Incident timeline | Interactive Incident Timeline component |
| Immediate containment recommendations | Incident Response panel — every action is labeled "Simulate Response" |
| Permanent defensive recommendations | Permanent Security Controls, grouped by category |
| Preserve/display evidence | Evidence / Audit Log table, backed by `audit_logs` |
| Hospital-specific business impact | "Why This Matters" panel (Patient Records, Clinical Scheduling, Admin Systems, Identity) |

If a feature in the codebase can't be traced to a row in this table, it doesn't belong —
that was the build rule throughout.

## Installation

### Prerequisites
- Docker + Docker Compose (recommended), **or**
- Python 3.11+, Node 20+, PostgreSQL 16 (manual setup)

### Quick start (Docker)
```bash
git clone <this-repo>
cd securescope
cp .env.example .env
docker compose up --build
```
- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173
- Postgres: localhost:5432 (user/pass/db: `securescope`)

The backend container automatically runs `python -m app.seed` on startup, loading the
Problem 4 demo dataset (target, services, findings, attack techniques, defense
recommendations, and the 6-event scenario timeline) so the dashboard is fully populated
without needing a live target.

### Manual development setup

**Database**
```bash
# using local Postgres
createuser securescope --pwprompt
createdb -O securescope securescope
```

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://securescope:securescope@localhost:5432/securescope
python -m app.seed          # seed demo data
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## Demo mode

Two independent "no live target required" paths:

1. **Target Assessment → "Demo mode" checkbox** (checked by default): the scanner
   skips live network I/O and returns the fixed Problem 4 exposure profile
   (ports 22/53/443/3389) against a documentation-range IP (`203.0.113.10`, RFC 5737).
2. **Security Events → "Load demo scenario"**: ingests the 6-event Problem 4 timeline
   (08:10 → 15:00) via `POST /api/test-events`, then **"Run correlation"** triggers the
   detection/correlation engine to generate a correlated incident end-to-end.

This lets you run the entire [Final Demo Flow](#final-demo-flow) with zero external
dependencies.

## API documentation

Interactive OpenAPI docs are auto-generated by FastAPI at `http://localhost:8000/docs`.

Key endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/scan?demo=true` | Start a target assessment |
| GET | `/api/scans/{scan_id}` | Fetch scan result |
| GET | `/api/services`, `/api/findings` | Exposure + risk data |
| GET | `/api/attack-techniques` | Threat knowledge base |
| POST | `/api/test-events` | Ingest a controlled/demo security event |
| GET | `/api/events` | List security events |
| POST | `/api/incidents/correlate` | Run detection + correlation engine |
| GET | `/api/incidents`, `/api/incidents/{id}` | Incident list / detail |
| PATCH | `/api/incidents/{id}/status` | Move an incident through its lifecycle |
| POST | `/api/response-actions` | Record a simulated containment action |
| GET | `/api/defenses` | Permanent security improvement plan |
| GET | `/api/audit-logs` | Evidence / audit trail |

## Security limitations

This tool is intentionally restricted. It does **not**:
- Execute arbitrary shell commands or build subprocess calls from user input.
- Perform banner grabbing, exploitation, credential theft, or brute forcing.
- Scan any ports beyond a small, hardcoded whitelist (22, 53, 443, 3389).
- Perform any live "response" — every containment action is recorded as
  **simulated** and never touches a real host, account, or credential.
- Store or reference real patient data — all demo data is fictional.

Target input is validated against a strict hostname/IPv4 pattern before any network
call. Backend error handling never surfaces stack traces to the client. Write-heavy
endpoints (`/api/scan`, `/api/test-events`) are rate-limited in-process.

## Testing

```bash
cd backend
pip install -r requirements.txt pytest httpx
pytest
```
See `tests/` for target-validation, risk-engine, and detection-engine unit tests.

## Final demo flow

1. Open SecureScope → dashboard loads with "System Operational."
2. Enter `healthcare.example.org`, keep Demo mode checked → Start Assessment.
3. Review discovered services and expand a finding's risk detail.
4. Open the Threat & Attack Techniques accordion.
5. Click **Load demo scenario** to ingest the 6-event Problem 4 timeline.
6. Click **Run correlation** to generate a correlated incident.
7. Review the Incident Timeline (click an event for detail) and the generated incident
   in Incident Response.
8. Click a few "Simulate Response" containment actions.
9. Review Permanent Security Controls.
10. Move the incident to **Contained** then **Resolved**.
11. Review the Evidence / Audit Log for the full trail of what happened.

## Project structure

```
securescope/
├── backend/          FastAPI app (scanner, risk/detection/correlation engines, REST API)
├── frontend/          React/Vite/Tailwind SOC dashboard
├── database/          (schema lives in backend/app/models.py via SQLAlchemy)
├── docs/              additional documentation
├── tests/             backend unit tests
├── docker-compose.yml
└── .env.example
```
