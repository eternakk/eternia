# Eternia

A simulation and control platform with a FastAPI backend and a modern React + Vite + TypeScript UI. The system exposes HTTP and WebSocket APIs for controlling/observing the world state, includes observability (Prometheus/Grafana), and ships with end‑to‑end and unit tests.

This README provides an overview, requirements, setup instructions, how to run locally or with Docker, useful scripts, environment variables, tests, project structure, and licensing notes.

## Tech stack

- Backend: Python 3.10+, FastAPI, Uvicorn
- Data and migrations: custom migration helpers and yoyo-migrations (see scripts/manage_migrations.py and migrations/)
- ML: PyTorch (torch) for selected components
- Observability: Prometheus metrics via starlette-exporter; Grafana dashboards via docker-compose
- Auth: HTTP Bearer; development/test tokens; optional JWT (PyJWT)
- Frontend: React 19, Vite 6, TypeScript 5, TailwindCSS, Storybook
- Package managers: pip (requirements.txt) and npm (ui/package.json)
- Tests: pytest (Python), Vitest/Testing Library (UI), Cypress (E2E)

## Requirements

- Python: 3.10 or newer (Dockerfile is based on python:3.10-slim)
- Node.js: 18.x (ui Dockerfile uses node:18-alpine)
- npm: 9+ (npm ci supported), or use the version bundled with Node 18
- Docker and Docker Compose (optional, for containerized development/ops)

## Quick start (local dev)

1) Backend
- Create and activate a virtual environment and install dependencies:
  - python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt
- Run the API server (auto‑reload):
  - python run_api.py
- API docs (once running):
  - Open http://localhost:8000/docs (Swagger UI)
  - Metrics: http://localhost:8000/metrics

2) Frontend (UI)
- Install UI dependencies:
  - cd ui
  - npm ci   # or: npm install
- Start the dev server:
  - npm run dev
- Open http://localhost:5173

3) End‑to‑end (UI + API)
- Ensure backend is running on :8000
- In ui/: npm run e2e to start Vite and then run Cypress in headless mode

## Running with Docker

- Build and run full stack (backend, frontend, Postgres, monitoring):
  - docker-compose up --build
- Services exposed by default:
  - Backend API: http://localhost:8000
  - Frontend (nginx): http://localhost/
  - Postgres: localhost:5432 (credentials via docker-compose env)
  - Prometheus: http://localhost:9090
  - Grafana: http://localhost:3000 (default admin password comes from env)
  - Optional Adminer (dev profile): http://localhost:8080

Note: docker-compose specifies persistent named volumes for Postgres and Prometheus/Grafana data.

## Entry points and scripts

Backend entry points
- API server (development): python run_api.py → uvicorn services.api.server:app --reload
- Simulation CLI: python main.py --cycles 100 (0 = infinite)

Root npm scripts (proxy to UI)
- npm run typecheck → npm --prefix ui run typecheck
- npm test → npm --prefix ui run test --
- npm run cypress:run → npm --prefix ui run cypress:run
- npm run e2e → npm --prefix ui run e2e

UI scripts (from ui/package.json; run inside ui/)
- npm run dev — start Vite on port 5173
- npm run build — type-check + build
- npm run preview — preview built app
- npm run typecheck — TypeScript type check
- npm run lint — ESLint
- npm test — Vitest runner (script: node ./scripts/vitest-runner.mjs)
- npm run storybook / build-storybook
- Cypress:
  - npm run cypress:open / cypress:run
  - npm run e2e (dev server + cypress:run)
  - Selective: e2e:ritual, e2e:dashboard, e2e:zone

Python utility scripts (scripts/)
- scripts/manage_migrations.py — create/apply/rollback/status for DB migrations
  - Examples:
    - python scripts/manage_migrations.py create add_users_table
    - python scripts/manage_migrations.py apply
    - python scripts/manage_migrations.py rollback --steps 1
    - python scripts/manage_migrations.py status
- scripts/run_benchmarks.py — run performance benchmarks
- scripts/profile_simulation.py — profile core simulation loops
- scripts/restore_backup.py — restore from artifacts/ backups

## Configuration and environment variables

Common variables (see docker-compose.yml and services/api/server.py)
- ETERNIA_ENV: environment name (default: development)
- JWT_SECRET: secret for JWT auth (development default provided in compose)
- DB_PASSWORD: database password for Postgres service in docker-compose

Auth tokens (development/testing)
- The API includes an endpoint GET /api/token that returns a development TEST_TOKEN for local use.
- The backend also recognizes a DEV_TOKEN in development contexts (see services/api/deps.py).
- For production, configure JWT via JWT_SECRET and related user management. TODO: document full JWT setup.

CORS and UI/API hostnames
- CORS allows http://localhost:5173 by default (Vite dev server) and the API origin.
- Adjust allowed origins in services/api/server.py if your dev ports differ.

Database
- docker-compose runs Postgres 14 with database eternia_<env> and user eternia_app.
- The Python codebase also references a local SQLite file at data/eternia.db in migration tooling.
- TODO: Confirm the authoritative runtime database (Postgres vs SQLite) and update this README and configuration accordingly.

Paths and data directories
- artifacts/: tokens, JWT secrets, user data, governor state, checkpoints, profiling data
- config/: configuration files
- data/: database files and persistent data (e.g., data/eternia.db when using SQLite)
- logs/: application logs (api_security.log, eternia.log, debug.log, etc.)
- migrations/: database migration scripts (managed by yoyo/custom helpers)

## Tests

Python tests (pytest)
- Install dev deps: pip install -r requirements.txt
- Run: pytest (uses pytest.ini to enable coverage; default threshold: 38%)
- Examples:
  - pytest -q
  - pytest -k backup_manager -vv
  - Property-based tests are included via Hypothesis (see tests/README.md)

UI tests (Vitest)
- In ui/: npm test (headless) or npm run test:watch

End‑to‑end tests (Cypress)
- In ui/: npm run e2e (starts Vite then runs Cypress)
- For GUI: npm run e2e:open
- Some e2e scripts validate ui/cypress.env.json; if missing, the validator will create an empty JSON. Provide any required keys for your environment. See ui/scripts/validate-cypress-env.mjs.

## Project structure

- modules/ — core backend domain modules
- services/ — API service (FastAPI app at services/api/server.py)
- scripts/ — maintenance and tooling scripts
- ui/ — React + Vite frontend
- tests/ — Python unit/integration/performance tests; see tests/README.md
- migrations/ — database migration files
- monitoring/ — Prometheus, Grafana, and alertmanager configs
- terraform/ — infrastructure as code (IaC)
- Dockerfile — backend container image
- ui/Dockerfile — frontend container image
- docker-compose.yml — multi-service dev/ops stack

## Important note on data storage

Do not store data files in the docs/ directory. The docs/ directory is reserved exclusively for documentation files.

Store data in their appropriate directories:
- artifacts/ — artifact files
- config/ — configuration files
- data/ — database and other data files
- logs/ — log files

The .gitignore is configured to ignore these data directories to prevent large or sensitive files from being committed.

## Cleanup script

A cleanup script (cleanup_docs.sh) is provided to remove any data directories that might have been mistakenly created under docs/. Run it with:

```bash
./cleanup_docs.sh
```

## License

No license file is present in the repository.
- TODO: Add a LICENSE file (e.g., MIT/Apache-2.0) and update this section accordingly.
