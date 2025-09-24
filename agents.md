# Repository Guidelines

## Project Structure & Module Organization
Core simulation code lives under `modules/` and `world_builder_modules/`, with orchestration entry points in `main.py`, `navigator.py`, and `run_api.py`. API routers and dependencies reside in `services/api/`, while the React/Vite interface sits in `ui/`. Tests mirror this layout in `tests/` for Python and `ui/src/__tests__/` + Cypress specs under `ui/cypress/`. Automation artifacts, backups, and logs stay in the gitignored `artifacts/`, `backups/`, and `logs/` directories.

## Build, Test, and Development Commands
Create or refresh a virtual environment, then install dependencies with `pip install -r requirements.txt`. Run the FastAPI control plane locally via `python run_api.py`, and start the simulation loop with `python main.py --cycles 10`. Frontend workflows use `npm install --prefix ui`, `npm run dev --prefix ui`, `npm test --prefix ui`, and `npm run cypress:run --prefix ui`. Docker-based environments rely on `docker compose up` at the repository root.

## Coding Style & Naming Conventions
Python code follows PEP 8 with black-style 4-space indentation and type hints enforced by `mypy` (strict). React components use PascalCase filenames, while hooks remain camelCase. Configuration constants and environment variables should use upper snake case (e.g., `ETERNIA_ENV`). Run `ruff` and `black` before committing to keep formatting consistent.

## Testing Guidelines
Unit and integration tests run with `pytest`; mark long-running suites using the markers in `pytest.ini`. Write test modules as `test_<module>.py` and place fixtures in `tests/conftest.py`. UI unit tests leverage Vitest, and end-to-end coverage comes from Cypress; ensure new features include both layers when relevant. Aim for >80% coverage on new modules and document any shortfalls in the pull request.

## Commit & Pull Request Guidelines
Structure commits around logical, reversible changes; prefer imperative present-tense messages such as "Add governor veto checks". Reference GitHub issues (`Fixes #13`) in either the commit body or PR description. Pull requests should summarize intent, link relevant stories from `docs/implementation_stories.md`, list test commands executed, and attach screenshots or screencasts for UI changes. Request reviews from domain owners when touching security, analytics, or governor modules.

## Agent-Specific Instructions
Tag automation-ready issues with `agent:ready` and ensure `docs/issue_story_map.json` stays updated. Run `python -m agents.orchestrator.flow --dry-run <ISSUE>` to preview the multi-role pipeline before handing tasks to MCP agents. Respect `red-mode` and `needs-human-review` labels—agents must pause until a human supervisor clears them.
