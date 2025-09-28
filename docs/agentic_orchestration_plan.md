# Agentic Orchestration Plan for Eternia

Date: 2025-09-16
Owner: Engineering Automation
Scope: Introduce a lightweight, deterministic agentic workflow to autonomously plan, implement, test, and propose changes via Draft PRs, with guardrails and observability.

---

## High-level Milestones
- Sprint A (2–3 days): Monorepo agent loop — scaffold, supervisor + flow, tools, role prompts, CI workflows, preview env, red-mode, nightly repo atlas.
- Sprint B (1–2 days): Hardening — retries, guardrails, observability, branch protection requirements.
- Sprint C (2–3 days, optional): Extraction path — separate repo + GitHub App + worker, webhook queue → PRs back to Eternia.

---

## Guiding Principles
- Use strongest model for Planner/Reviewer/Security; cheaper model for Implementers; keep Tests on strong model until quality is good.
- Determinism: pin tool versions (CI and agent container) so tests match agent runs.
- Diff discipline: Implementers produce unified diffs (or explicit file blocks). `git_ops` validates patches apply cleanly and returns actionable conflicts.
- Human override: `needs-human-review` label freezes bot pushes; Supervisor must honor it.

---

## Sprint A — Monorepo Agent Loop (2–3 days)

### A1. Scaffold the agent package
- Create directories: `/agents/{orchestrator,roles,tools,prompts}` with `__init__.py`.
- Add `/agents/README.md` describing architecture and responsibilities.
- Config: `.env` keys (read via `os.getenv`)
  - GITHUB_TOKEN, OPENAI_API_KEY (or provider keys), VERCEL_TOKEN (if used), FLY_API_TOKEN, CI_BASE_URL (optional), RED_MODE_LABEL (default: `red-mode`), HUMAN_FREEZE_LABEL (default: `needs-human-review`).
- Wire to existing MCP config under `config/mcp/.env.example` by documenting required variables and adding placeholders.

### A2. Supervisor
- File: `/agents/orchestrator/supervisor.py`.
- Responsibilities:
  - Poll GitHub Issues with label `agent:ready`.
  - Respect repo-wide `red-mode` and `needs-human-review` labels to gate actions.
  - For each eligible Issue:
    - Create a feature branch `agent/{issue-number}-{slug}`.
    - Open a Draft PR targeting default branch.
    - Seed the PR with Planner output (markdown plan + acceptance criteria) as the first comment.
  - Idempotency: do nothing if a Draft PR already exists for the Issue.

### A3. Flow Orchestrator (sequential v1)
- File: `/agents/orchestrator/flow.py`.
- Responsibilities:
  - For a given PR:
    1) Planner role → plan.md + acceptance criteria comment.
    2) Test Author → generate stubs first (PyTest/Vitest as applicable) → commit.
    3) Implementers → limited to whitelisted dirs → produce unified diffs → patch, commit.
    4) Run tools: tests, UI smoke (or trigger workflow), CI poll.
    5) Reviewer → rubric score and actionable nits → comment.
    6) Security → scan (semgrep/CodeQL if available) → patch or issue comments.
    7) Doc Scribe → README/API/ADR updates as markdown patch.
  - Retries: simple backoff for flaky steps, with clear failure notes on PR.

### A4. Tools (minimal v1)
- File: `/agents/tools/git_ops.py`
  - checkout branch, apply patch (validate unified diff), commit, push, open PR via API.
- File: `/agents/tools/ci.py`
  - poll PR checks; fetch failing logs (GitHub Checks API or artifacts).
- File: `/agents/tools/run_tests.py`
  - run `pytest` locally (containerized or pinned venv), parse failures (JUnit or stdout patterns).
- File: `/agents/tools/run_ui.py`
  - trigger Playwright smoke (via CLI or a CI workflow dispatch); read result from checks.
- File: `/agents/tools/openapi_diff.py`
  - run openapi-diff (CLI or library) between base and head.
- File: `/agents/tools/sbom.py`
  - generate SBOM (e.g., `cyclonedx`, `syft`) and stash artifact.
- File: `/agents/tools/k6.py`
  - trigger k6 API perf run locally or via CI; parse thresholds.

### A5. Role prompts & rubrics (MVP)
- Directory: `/agents/prompts/`
  - `planner.md`: outputs markdown plan + acceptance criteria (AC) blocks.
  - `test_author.md`: generates PyTest/Vitest test stubs first.
  - `implementer.md`: instructions to output unified diff or explicit file content blocks; limit changes to whitelisted dirs.
  - `reviewer.md`: rubric scoring (correctness, tests, style, perf, security, docs) + actionable nits.
  - `security.md`: consume semgrep/CodeQL findings; propose concrete patch or issue comments.
  - `scribe.md`: produce README/API/ADR markdown patches.

### A6. GitHub Actions
- `.github/workflows/agent_supervisor.yml`
  - Triggers: `schedule: "*/15 * * * *"` and `on: issues: [labeled]`.
  - Job: run Supervisor to open/refresh Draft PRs.
- `.github/workflows/preview_comment.yml`
  - On PR open/sync: post preview URLs (Vercel UI / Fly API) as a comment.
- `.github/workflows/ui_smoke.yml`
  - Runs Playwright smoke (or cypress) with pinned versions.
- `.github/workflows/api_perf.yml` (k6), `.github/workflows/sbom.yml`, `.github/workflows/openapi_diff.yml`.
- Branch protection: mark `ui_smoke`, `tests`, `openapi_diff`, `sbom`, `api_perf` as required for merge.

### A7. Preview environments
- UI: Vercel auto previews on PR (or configured alternative). Add `vercel.json` if needed.
- API: Fly.io app (e.g., `eternia-api`) with health endpoint `/healthz`.
- Document env/provisioning steps; store non-secret config in repo, secrets in GitHub.

### A8. Red-mode
- Tiny Action: checks preview health periodically; adds/removes `red-mode` label on the repo.
- Supervisor respects red-mode: only allows fix tasks when red-mode active.

### A9. Nightly Repo Atlas
- Script: `repo_atlas.py` (planned under `scripts/`) → JSON map of symbols/deps/owners to
  `artifacts/repo_atlas.json` for agent retrieval (TODO: script not yet committed; interim runs rely on manual topology
  reviews).
- Scheduled workflow nightly to refresh.

---

## Sprint B — Hardening (1–2 days)

### B1. Error handling & retries
- Add typed exceptions, backoff, and circuit breakers in `flow.py`.
- On failure, leave concise escalation comments on PR with next steps.

### B2. Guardrails
- Max patch size; deny mass deletions; enforce tests-first (PR must show tests changed/added).
- Secrets allow-list for tool env; deny outbound calls except approved hosts.

### B3. Observability hooks
- On deploy, fetch `/metrics` + logs; open Issue if 500s spike or p95 regresses; label `agent:ready` for triage.

---

## Sprint C — Optional Extraction (2–3 days)
- New repo `eternia-agents` with the same `/agents` code.
- GitHub App + Fly worker deployment.
- Webhooks: Issues/PR events → queue; worker processes tasks; opens PRs back on Eternia.
- Repository dispatch or REST for preview URLs if using direct pings.

---

## Acceptance Criteria (per milestone)
- Sprint A
  - Supervisor opens Draft PRs from `agent:ready` issues with seeded plan comment.
  - Flow runs sequential roles; commits tests-first; patches apply cleanly; CI checks visible on PR.
  - Preview URLs posted on PR; red-mode respected; nightly repo atlas artifact produced.
- Sprint B
  - Retries/backoff implemented; guardrails enforced; observability creates Issues on regressions.
- Sprint C
  - Externalized worker processes webhook events and opens PRs back to Eternia.

---

## Determinism & Pinning
- Pin Python, Node, and CLI tool versions in CI.
- Use lockfiles and container images for agent runs.
- Store versions in a single `agents/versions.py` or `tools/versions.json` for reuse.

---

## Directory and File Map (to be created)
- agents/
  - orchestrator/
    - supervisor.py
    - flow.py
  - roles/
    - __init__.py (role adapters)
  - tools/
    - git_ops.py
    - ci.py
    - run_tests.py
    - run_ui.py
    - openapi_diff.py
    - sbom.py
    - k6.py
  - prompts/
    - planner.md
    - test_author.md
    - implementer.md
    - reviewer.md
    - security.md
    - scribe.md
  - README.md
- .github/workflows/
  - agent_supervisor.yml
  - preview_comment.yml
  - ui_smoke.yml
  - api_perf.yml
  - sbom.yml
  - openapi_diff.yml
- scripts/
  - repo_atlas.py (planned; ensure this lands before enabling atlas-dependent workflows)
- artifacts/
  - repo_atlas.json (generated)

---

## Task Breakdown & Effort
- Day 1: A1–A3 scaffolding, Supervisor + sequential flow skeleton; prompts.
- Day 2: A4 tools MVP, A6 workflows, A7 previews; red-mode; smoke test.
- Day 3 (buffer): A9 repo atlas and polishing; pinning; docs.
- Day 4–5: Sprint B hardening.
- Day 6–8 (optional): Sprint C extraction.

---

## Risks & Mitigations
- Secrets management: define allow-list and use GitHub Encrypted Secrets; document required scopes.
- CI flakiness: add retries; prefer workflow-dispatch to run heavy checks.
- Patch conflicts: enforce diff validation and bounce back to Implementer with precise conflict hunks.

---

## Next Action
- Confirm this plan. Upon approval, proceed with A1–A3 scaffolding in a feature branch `agent/scaffold` and open a Draft PR with this plan attached.
