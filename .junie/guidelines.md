Eternia – Development Guidelines (Project‑Specific)

Audience: Senior developers and maintainers of Eternia.
Scope: Concrete, repo‑specific knowledge to speed up local setup, testing, and debugging. This document intentionally avoids generic Python basics.

1) Build and Configuration

Python/OS
- Python: 3.12.x (project CI and local .venv have been exercised on 3.12). Some libs (e.g., httpx/anyio/fastapi stack) and our event loop usage depend on 3.11+ semantics.
- OS: Mac/Linux are primary. Windows works under WSL2.

Environment selection and secrets (critical)
- Env flag: ETERNIA_ENV (or APP_ENV) ∈ {development, production}. Values prod/production imply production. Defaults to development.
- JWT secret handling (see README Secrets & Environments for full policy):
  - Development priority:
    1) JWT_SECRET or JWT_SECRET_KEY in environment.
    2) If SECRET_KEY_ENCRYPTION_PASSWORD is set, an encrypted secret is stored at artifacts/jwt_secret.txt.
    3) Otherwise a plaintext dev secret at artifacts/dev.jwt_secret.txt (gitignored) is created/used.
  - Production priority:
    1) JWT_SECRET (or JWT_SECRET_KEY) required, or
    2) SECRET_KEY_ENCRYPTION_PASSWORD to create/use encrypted artifacts/jwt_secret.txt.
    If neither is present, startup fails (by design).
- Artifacts, data, and logs directories are gitignored by default. Do not store data under docs/.

Local services
- App entry points:
  - CLI runner: python main.py (interactive/looped world setup and runtime)
  - API runner: python run_api.py (FastAPI service, includes world setup)
- World and init side effects: The first import/run performs world initialization (zones, physics profiles, companions, etc.) and can take seconds. This also happens under pytest unless isolated; see Testing section.

Docker
- Dockerfile and docker-compose.yml are provided. Compose uses ETERNIA_ENV; ensure proper secrets are passed.
- Minimal invocation:
  - docker build -t eternia:local .
  - docker compose up api  # if api service defined in compose file

Python environment
- Recommended: create a local venv with Python 3.12 and install requirements.
  - python -m venv .venv && source .venv/bin/activate
  - pip install --upgrade pip
  - pip install -r requirements.txt
- Optional UI/npm stack:
  - Node in package.json; only needed for ui/ development or Cypress runs. Not required for core Python tests.

Configuration files worth knowing
- pytest.ini: currently minimal; runs tests quietly (-q). No custom markers registered yet; see Testing Guidelines for implications.
- mypy.ini: partial/targeted type checking config; run mypy selectively if you extend typed areas.
- yoyo.ini: DB migration config (yoyo-migrations). migrations/ is present though normal tests do not apply migrations dynamically.

2) Testing: How to run and how to add tests

Overview
- Test runner: pytest (see pytest.ini). Our test set includes unit, integration, and performance benches (pytest-benchmark). Integration tests exercise the FastAPI app and world initialization and thus trigger long startup and log noise.
- Baseline: A full pytest run passes locally but emits several warnings:
  - Unknown markers like @pytest.mark.integration or @pytest.mark.unit (not registered).
  - RuntimeWarnings about un-awaited coroutines from async hooks in certain integration tests; these are expected and tolerated under current architecture, but should be reduced over time.

Quick commands
- Run all tests (quiet): pytest -q
- Only a directory: pytest -q tests/unit
- Keyword filter: pytest -q -k event_bus
- Skip integration by convention (since markers aren’t registered yet):
  - Prefer path selection: pytest -q tests/unit tests/performance
  - Or add your own local mark expressions once markers are registered (see below).
- Benchmark opt-in: performance tests use pytest-benchmark; they run by default. To skip:
  - pytest -q -k "not performance"  # relies on file naming; or move benches under a marker once registered

Markers (project state and recommendation)
- Current state: integration and unit markers appear in tests but are not registered in pytest.ini, causing PytestUnknownMarkWarning.
- Recommendation:
  - Register markers in pytest.ini to enable -m filtering without warnings. Example to add:
    [pytest]
    markers =
        unit: fast, isolated unit tests
        integration: exercises multiple modules/IO
        performance: micro/meso benchmarks using pytest-benchmark
  - After registration you can run:
    - pytest -q -m unit
    - pytest -q -m "not integration"

Fixtures and helpers (repo-specific)
- tests/conftest.py exposes rich fixtures:
  - event_bus(): fresh EventBus singleton handle
  - pause_event(), resume_event(), shutdown_event()
  - emotional_state(), emotional_circuit_system()
  - physics_profile(), physics_zone_registry()
  - time_synchronizer(), sensory_profile()
  - social_interaction_module(), user()
  - mock_world(), mock_governor()
- Event system API (modules/utilities/event_bus.py):
  - Event, EventListener base, @event_handler decorator, EventBus.publish(), publish_async(), subscribe()/unsubscribe().
  - Handlers can be sync or async; publish() schedules async handlers (does not await), publish_async() awaits them.

Adding new tests (guidelines)
- Unit tests
  - Prefer tests/unit/ hierarchy.
  - Use provided fixtures to avoid booting the full world unless necessary.
  - For event-driven units, prefer EventListener + @event_handler and validate handler order via EventPriority where relevant.
- Integration tests
  - Place under tests/integration/.
  - If spinning the API, use httpx.AsyncClient or TestClient; be mindful of startup side effects (world setup) and JWT requirements if hitting auth endpoints.
  - Keep external IO mocked unless explicitly validating migrations or long-lived flows.
- Performance/benchmarks
  - Place under tests/performance/ with pytest-benchmark. Guard with a marker once markers are registered to allow easy exclusion in CI.

Creating and running a simple test (validated example)
- We validated the flow locally using a minimal EventBus test:
  - File (temporary): tests/unit/test_demo_guidelines.py
    from modules.utilities.event_bus import EventBus, Event, event_handler, EventListener
    class DemoEvent(Event):
        def __init__(self, value: int):
            self.value = value
    class DemoListener(EventListener):
        def __init__(self):
            self.values = []
            super().__init__()
        @event_handler(DemoEvent)
        def on_demo(self, evt: DemoEvent):
            self.values.append(evt.value)
    def test_demo_event_flow():
        bus = EventBus()
        listener = DemoListener()
        bus.publish(DemoEvent(1))
        bus.publish(DemoEvent(2))
        assert listener.values == [1, 2]
  - Run: pytest -q tests/unit/test_demo_guidelines.py
  - Result: passed (with a PytestUnknownMarkWarning only if you add @pytest.mark.unit before registering markers).
  - Cleanup: the file was removed after validation to keep the repo unchanged; use this as a pattern for onboarding demos.

Advice to keep pytest fast and deterministic
- Avoid importing world_builder or starting run loops in unit tests. Mock Eterna interface pieces (see fixtures) instead.
- Prefer publish_async() in tests that validate async handlers to ensure completion before assertions.
- Use -k and directory selection to avoid slow integration boot unless you specifically target it.
- Suppress expected warnings locally via filterwarnings in pytest.ini if they distract (already excludes DeprecationWarning).

3) Additional Development Information

Code style and typing
- Style: PEP8/black-like conventions are generally followed; no mandatory formatter enforced in CI yet. Keep lines <= 100–120.
- Typing: Gradually typed. mypy.ini exists; run mypy on modules/ you touch:
  - mypy modules/<your_area> --namespace-packages --explicit-package-bases

Logging
- Logging is configured in modules/logging_config.py. Pytest will initialize logging and you will see structured INFO lines during world setup; this is normal.
- For tests, prefer using caplog to assert on log messages rather than mutating global logging config.

Database and migrations
- SQLite artifact at data/eternia.db is used in dev. Migrations managed by yoyo; integration tests should not auto-apply migrations unless explicitly invoked.
- If your test needs a clean DB, create an ephemeral tmp path and point the app to it via env variables (or mock the repository layer) to avoid touching local data/.

FastAPI service notes
- run_api.py boots the API and triggers world setup. For endpoint tests, use FastAPI TestClient/AsyncClient and scope the app to the test to avoid cross-test leakage.
- Auth endpoints require JWT secret presence (see Secrets section). For tests, inject JWT_SECRET to a deterministic value.

Quantum/metrics endpoints
- Some integration tests hit quantum routers and metrics; they may emit RuntimeWarnings due to intentionally non-awaited background coroutines. This is known; do not fail the suite on these warnings.

CI and benches
- pytest-benchmark results are printed; we do not assert specific thresholds in CI yet. Treat numbers as observational. If you add performance gates, isolate in a separate job.

House rules
- Do not store data in docs/. Use artifacts/, data/, logs/ as intended; they are gitignored.
- When adding markers, update pytest.ini to register them to avoid warnings and enable -m filtering.
- Keep integration tests resilient to environment variability (offline operation, missing GPU, etc.).

Appendix – Quick recipes
- Register markers (suggested):
  [pytest]
  addopts = -q
  markers =
      unit: fast, isolated unit tests
      integration: exercises multiple modules/IO
      performance: micro/meso benchmarks using pytest-benchmark
  filterwarnings =
      ignore::DeprecationWarning
      ignore::PendingDeprecationWarning
- Run only unit tests once markers are registered:
  pytest -q -m unit
- Skip performance benches by path:
  pytest -q tests/unit tests/integration
