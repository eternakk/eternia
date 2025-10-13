# Eternia

Eternia is a sandboxed AI world-simulation stack that combines a modular Python core, a FastAPI control plane, and an optional React UI. It models companions, rituals, symbolic physics, and law-governed safety rails while exposing orchestration hooks, metrics, and optional quantum-inspired utilities.

## Core Capabilities
- Modular simulation runtime built around `EternaInterface`, `world_builder_modules`, and an alignment governor with checkpointing and PPO-based companion feedback.
- FastAPI service (`services/api/server.py`) exposing REST, WebSocket, and quantum endpoints with rate limiting, Prometheus metrics, and static asset serving.
- React/Vite frontend in `ui/` with Storybook, Cypress, and Vitest support for real-time dashboards and control interactions.
- Observability stack (Prometheus, Grafana, cAdvisor, Node Exporter) plus structured logging routed to `logs/` and metrics helpers in `modules/monitoring.py`.
- Extensive documentation under `docs/` covering architecture, onboarding, quantum features, and operational runbooks.

## Repository Map
- **Entry points** `main.py` (simulation loop), `navigator.py` (interactive CLI), `run_api.py` (FastAPI launcher).
- **Simulation core** `world_builder.py` and `world_builder_modules/` compose zones, physics, rituals, resonance, and optional quantum modifiers.
- **Services** `services/api/` (routers, auth, dependencies) and `modules/api_interface.py` providing command, state, and event bridges.
- **Platform modules** `modules/` (governor, monitoring, backup manager, DI container, quantum service, RL loop, tracing, validation).
- **Client & ops** `ui/` (React app), `monitoring/` (Prometheus/Grafana configs), `terraform/` (infrastructure), `scripts/` (automation helpers).
- **Artifacts** `artifacts/`, `data/`, and `logs/` are gitignored stores for secrets, checkpoints, and runtime output; use `cleanup_docs.sh` to keep docs/ data-free.

## Requirements
- Python 3.10+ (project guidance targets 3.12; Dockerfile currently pins python:3.10-slim).
- macOS or Linux recommended; Windows works via WSL2.
- Node.js 18+ for UI tooling (Vite/Storybook/Cypress) when working in `ui/`.
- Docker and docker-compose for container workflows, plus optional Terraform/Prometheus stacks.

## Backend Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install --upgrade pip`
3. `pip install -r requirements.txt`
4. Export environment: `export ETERNIA_ENV=development` (defaults to development if unset).
5. Start API: `python run_api.py` (or `uvicorn services.api.server:app --reload`).

The API listens on `http://localhost:8000`. World boot can take a few seconds on first import.

### Simulation Runners
- Deterministic loop: `python main.py --cycles 10` (`0` = run indefinitely).
- Interactive CLI: `python navigator.py` for guided exploration commands.
- Governor-driven background loop is started by the API via `services/api/deps.py`.

### Frontend (optional)
- `npm install --prefix ui`
- `npm run dev --prefix ui` (Vite on `http://localhost:5173`)
- `npm run build --prefix ui` and `npm run preview --prefix ui`
- Root `package.json` proxies: `npm run typecheck`, `npm test`, `npm run cypress:run`, `npm run e2e`.

### Docker & Compose
- Build: `docker build -t eternia:local .`
- Backend only: `docker compose up backend`
- Full stack (backend + Postgres + monitoring): `docker compose up`
- Default ports: 8000 (API), 5173/80 (UI), 5432 (Postgres), 9090/3000/9100/8081 (Prometheus/Grafana/Node Exporter/cAdvisor).

## Configuration & Secrets
- `config/settings/{default,development,staging,production}.yaml` feed `ConfigManager`; override with env vars like `ETERNIA_FEATURES_QUANTUM_ENABLED`.
- Environment selectors: `ETERNIA_ENV` or `APP_ENV` (`development`, `production`, etc.).
- Auth secrets: set `JWT_SECRET`/`JWT_SECRET_KEY`; otherwise development secrets live under `artifacts/` (encrypted when `SECRET_KEY_ENCRYPTION_PASSWORD` is supplied).
- The API dev token (`DEV_TOKEN`) is generated at `artifacts/auth_token.txt` unless `ETERNA_TOKEN`/`VITE_ETERNA_TOKEN` is provided.
- Gitignored stores (`artifacts/`, `logs/`, `data/`) keep runtime state, backups, and checkpoints; rotate secrets by removing files and restarting.

## Observability & Integrations
- Prometheus metrics via `PrometheusMiddleware` and custom collectors in `modules/monitoring.py`; scrape `/metrics` when enabled.
- HTTP/WebSocket authentication supports dev token, test token, and JWT flows (`services/api/server.py`).
- Quantum-inspired APIs live under `/api/quantum/*`, backed by `modules/quantum_service.QuantumService` with graceful Qiskit fallbacks and tracing hooks.
- Event streaming uses `/ws` with rate limiting and governor-driven broadcast; legacy adapters bridge module events into the API queue.
- Monitoring manifests reside in `monitoring/`; Terraform infrastructure scaffolding lives in `terraform/`.

## Testing
- Python suite: `pytest -q` (see `pytest.ini` markers for `unit`, `integration`, `performance`).
- UI tooling: `npm test --prefix ui`, `npm run typecheck --prefix ui`, `npm run cypress:run --prefix ui` for E2E.
- Protobuf/OpenTelemetry instrumentation ships disabled by default; add env toggles before running telemetry-heavy tests.

## Documentation
- Start with `docs/README.md` for a categorized index spanning onboarding, system design, security, and runbooks.
- Getting started: `docs/developer_onboarding.md`, `docs/environment_setup.md`, `docs/running_the_server.md`, and `docs/docker_setup.md`.
- Architecture & systems: `docs/architecture_v3.md` (plus v1/v2 history), `docs/module_map.md`, `docs/state_management_and_data_flow.md`, `docs/event_system.md`.
- Simulation & world mechanics: `docs/runtime_cycle.md`, `docs/companion_ecology.md`, `docs/evolution_logic.md`, `docs/genesis_valley_pcg.md`.
- Platform & ops: `docs/api_documentation.md`, `docs/monitoring_and_alerting.md`, `docs/release_management.md`, and `docs/runbooks/`.
- Security & governance: `docs/governor.md`, `docs/secure_coding_guidelines.md`, `docs/security_scanning.md`, `docs/backup_and_recovery.md`.
- Agentic automation: `AGENTS.md` and `docs/agentic_orchestration_plan.md` detail the multi-role workflow.
- Planning & tracking: `docs/tasks.md`, `docs/implementation_stories.md`, and `docs/issue_story_map.json`.

## Maintenance Notes
- Align Docker base image with the preferred Python 3.12 toolchain.
- Clarify production database strategy (SQLite artifacts vs. Postgres in compose) and document migration flow.
- Audit remaining scripts in `scripts/` (backups, migrations) and surface usage examples.
- Capture additional required environment variables (e.g., tracing/OTEL) once stabilized.

## Outstanding Work
- Consolidated design for pending features lives in `docs/pending_implementation_design.md`; MCP agents should read it before tackling unchecked tasks in `docs/tasks.md`.
- Frontend roadmap now also spans the immersive world-builder UI, spatial rendering, and movement visualizations alongside i18n, Redux Toolkit, accessibility upgrades, theming, and offline cache safety.
- Security backlog covers TOTP-based 2FA, HMAC request signing, structured audit logging, file-scanning uploads, and privacy-aware exports.
- Data and analytics initiatives span export APIs, validation schemas, observability dashboards, anomaly detection, predictive companions, and conversation-derived training datasets aligned with the personal-universe goals.
- Multi-agent orchestration scripts need to operationalize Planner/Test/Implementer/Reviewer/Security/Docs roles and plug into the shared communication hub so the development loop can self-close as described in the orchestration and feasibility plans.

## License
CC0 1.0 (see `LICENSE`).
