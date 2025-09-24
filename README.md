# Eternia

A sandboxed AI simulation and control platform with a FastAPI backend and a TypeScript/React UI. The project models zones, physics profiles, companions, emotional circuits, and governance policies; it exposes control and observability via an API and optional web UI.

This README provides an overview, setup instructions, commands, environment variables, testing guidance, and pointers to relevant docs. Where details are unclear in the repository, TODO notes are included for maintainers to fill in.

## Overview

- Backend: Python (FastAPI + Uvicorn), event-driven modules, optional world simulation loop.
- UI: Vite + React + TypeScript (under ui/), optional Storybook and Cypress E2E.
- Data: SQLite (artifacts/data) for development; yoyo-migrations present.
- Auth: OAuth2/JWT with development fallbacks. Rate limiting and metrics enabled.
- Deployment: Dockerfile and docker-compose.yml; monitoring stack (Prometheus + Grafana) included.

## Tech stack

- Language: Python 3.12 recommended by project docs; FastAPI app (services.api.server:app)
- ASGI server: Uvicorn
- Key Python deps (requirements.txt): fastapi, uvicorn, httpx, pydantic v2, PyJWT, bcrypt, slowapi, starlette-exporter, yoyo-migrations, torch (optional ML), pytest stack
- Node/UI: Vite, React 19, TypeScript, Vitest, Cypress, Storybook (see ui/package.json)
- Containerization: Docker, docker-compose; Prometheus, Grafana, cAdvisor, Node Exporter

Note: Dockerfile currently pins python:3.10-slim while guidelines prefer Python 3.12. See TODO below.

## Requirements

- Python: 3.12.x recommended (guidelines); 3.11+ semantics used by dependencies. 3.10 may work in the Docker image but is not the preferred local version.
- OS: macOS/Linux recommended; Windows supported via WSL2.
- Node.js: Required only for UI and UI tests (Vite/Storybook/Cypress). Version aligned with ui/ devDependencies (Node 18+ recommended).

## Getting started (backend)

1) Create a virtual environment and install dependencies
- python -m venv .venv && source .venv/bin/activate
- pip install --upgrade pip
- pip install -r requirements.txt

2) Set environment (development is default)
- export ETERNIA_ENV=development  # or APP_ENV
- Optionally set JWT_SECRET for deterministic dev tokens, otherwise the app will manage a local dev secret (see Secrets & Environments).

3) Run the API server (FastAPI)
- python run_api.py
- Or with explicit Uvicorn: uvicorn services.api.server:app --host 0.0.0.0 --port 8000 --reload

4) Run the simulation CLI (world loop)
- python main.py --cycles 10  # 0 = infinite

API will be on http://localhost:8000. UI expects this default backend during dev.

## Getting started (UI)

The UI is under ui/ and is optional for backend-only development.

- npm install --prefix ui
- npm run dev --prefix ui  # Vite dev server on http://localhost:5173
- npm run build --prefix ui
- npm run preview --prefix ui

Repo root also proxies some UI commands via package.json scripts:
- npm run typecheck
- npm test
- npm run cypress:run
- npm run e2e

See ui/package.json for Storybook and granular Cypress specs.

## Entry points

- CLI runner: python main.py
- API runner: python run_api.py (starts FastAPI app services.api.server:app)
- Uvicorn alt: uvicorn services.api.server:app --host 0.0.0.0 --port 8000

Note: World initialization can take seconds on first import/run.

## Environment variables

Environment selection
- ETERNIA_ENV or APP_ENV ∈ {development, production}. Values prod/production imply production. Defaults to development.

JWT secret handling (policy)
- Development priority:
  1) JWT_SECRET or JWT_SECRET_KEY in environment
  2) If SECRET_KEY_ENCRYPTION_PASSWORD is set, an encrypted secret is stored at artifacts/jwt_secret.txt
  3) Otherwise a plaintext dev secret at artifacts/dev.jwt_secret.txt (gitignored) is created/used
- Production priority:
  1) JWT_SECRET (or JWT_SECRET_KEY) required, or
  2) SECRET_KEY_ENCRYPTION_PASSWORD to create/use encrypted artifacts/jwt_secret.txt. If neither is present, startup fails.

Other variables seen in compose or modules
- DB_PASSWORD (used by postgres service in docker-compose)
- GRAFANA_ADMIN_PASSWORD, GRAFANA_SECRET_KEY (Grafana in docker-compose)
- Prometheus/Grafana configs under monitoring/ (mounted by compose)

Directories are gitignored: artifacts/, data/, logs/.

## Running tests

- All tests (quiet): pytest -q
- Only unit tests: pytest -q -m unit
- Exclude integration: pytest -q -m "not integration"
- By path: pytest -q tests/unit
- Benchmarks run by default (pytest-benchmark). To skip by keyword or path:
  - pytest -q -k "not performance"

Notes
- See tests/conftest.py for rich fixtures (event bus, physics profiles, etc.).
- For async handlers, prefer publish_async() to ensure completion before assertions.
- World setup is slow; isolate integration tests when possible.

## Scripts

- scripts/sync_tasks_to_github_project.py — Sync docs/*tasks.md checkboxes to GitHub Projects (see section below)
- scripts/verify_mcp_config.py — Validates local MCP tooling setup (see docs/mcp.md)
- scripts/mcp/*.sh — Convenience wrappers for running MCP-related Docker images
- docs mention scripts for migrations and backups (manage_migrations.py, restore_backup.py). TODO: Verify presence and document exact usage here.

Run examples
- python scripts/sync_tasks_to_github_project.py
- python scripts/verify_mcp_config.py

## Docker

- Build: docker build -t eternia:local .
- Run backend only: docker compose up backend
- Full stack (backend + db + optional monitoring): docker compose up

Compose uses ETERNIA_ENV. Ensure JWT_SECRET (or SECRET_KEY_ENCRYPTION_PASSWORD) is set appropriately in production-like runs.

Ports
- 8000 → FastAPI backend
- 80 → UI (when ui/Dockerfile exists and frontend service is enabled)
- 5432 → Postgres
- 9090 → Prometheus, 3000 → Grafana, 9100 → Node Exporter, 8081 → cAdvisor

## Project structure (selected)

- agents/ — Agent definitions and behaviors
- artifacts/ — Secrets and artifacts (gitignored)
- assets/ — Static assets
- config/ — App configuration
- data/ — Databases and persistent data (gitignored)
- docs/ — Markdown documentation (see below)
- logs/ — Application logs (gitignored)
- migrations/ — yoyo migration files
- modules/ — Core backend modules (event bus, monitoring, backup manager, etc.)
- services/api/ — FastAPI app and routers
- scripts/ — Utility scripts (sync, MCP, etc.)
- tests/ — Unit, integration, and performance tests
- ui/ — Frontend (Vite + React + TS)
- main.py — CLI world runner
- run_api.py — API server bootstrap (Uvicorn)
- Dockerfile, docker-compose.yml — Containerization
- requirements.txt — Python dependencies
- package.json — Root proxy to ui scripts

## Logs, data, and docs hygiene

Do not store data files under docs/. Use artifacts/, data/, logs/ as intended. A helper script can clean accidental data dirs under docs/:

- ./cleanup_docs.sh

## Secrets & Environments (detailed)

JWT signing secrets are handled differently in development and production. Summary:

- Development:
  1) JWT_SECRET/JWT_SECRET_KEY env
  2) Or encrypted artifacts/jwt_secret.txt if SECRET_KEY_ENCRYPTION_PASSWORD provided
  3) Else plaintext artifacts/dev.jwt_secret.txt is used (gitignored)

- Production:
  1) JWT_SECRET/JWT_SECRET_KEY required, or
  2) SECRET_KEY_ENCRYPTION_PASSWORD to use encrypted artifacts/jwt_secret.txt
  3) If neither is present, startup fails by design

Artifacts directory is gitignored. To rotate, delete secret files and restart with desired env.

## Syncing tasks to GitHub Projects

See scripts/sync_tasks_to_github_project.py and .github/workflows/sync_tasks.yml.

Quick start
- Add GH_TOKEN secret to repo Actions
- Add GH_OWNER and GH_OWNER_TYPE variables (and optionally GH_PROJECT_TITLE, GH_STATUS_TODO, GH_STATUS_DONE)
- Run locally: python scripts/sync_tasks_to_github_project.py
- Or trigger the workflow after editing docs/tasks.md

## License

This project is licensed under CC0 1.0 (see LICENSE).

## TODOs for maintainers

- Align Dockerfile base image with Python 3.12 per project guidelines (currently python:3.10-slim).
- Document exact DB configuration for production (compose uses Postgres; app code also references SQLite artifacts). Clarify default DB and migration flow.
- Audit and document all scripts under scripts/ (migrations, backups) in this README with exact commands.
- Confirm any additional required env vars (e.g., OTEL settings) and add them here if enabled in deployment.