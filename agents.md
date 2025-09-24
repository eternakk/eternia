# Eternia Agent Operations Guide

This guide documents how autonomous and human-in-the-loop agents collaborate on Eternia. It distills industry best
practices for multi-agent delivery and adapts them to Eternia's alignment-first simulation stack, security posture, and
narrative goals.

## Objectives

- Preserve Alignment Governor authority: agents must honor pause, rollback, and red-mode signals before acting.
- Deliver traceable value: every action should link back to an issue, story, or task in `docs/tasks.md` or
  `docs/implementation_stories.md`.
- Stay test-first and reversible: agents stage tests before implementation work and maintain undo paths with checkpoints
  and Git hygiene.
- Minimize blast radius: apply gated changes, lean on preview environments, and surface risk to human overseers early.

## Core Roles and Handoffs

| Role                | Primary Outputs                                                                 | Guardrails                                                                       | Notes                                                                      |
|---------------------|---------------------------------------------------------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| **Supervisor**      | Draft PR seeded from `agent:ready` issues, branch `agent/{issue-number}-{slug}` | Blocks on repo `red-mode` or `needs-human-review` labels; idempotent PR creation | Runs on schedule or issue label events; leaves audit trail in PR timeline  |
| **Planner**         | `plan.md` with acceptance criteria, dependency callouts, risk log               | References canonical docs; forbids implementation changes                        | Uses strongest model; ensures alignment checks and runtime impact analysis |
| **Test Author**     | New or expanded automated tests committed before code                           | Restricted to `tests/`, `test/`, `ui/tests`, fixtures                            | Must justify skipped tests; promotes contract-first delivery               |
| **Implementer(s)**  | Minimal diff implementing planned change set                                    | Whitelisted directories; diff validation via `git_ops`                           | Fails closed on governor overrides or missing tests                        |
| **Reviewer**        | Rubric score + actionable feedback comment                                      | Checks correctness, perf, alignment, documentation                               | Can request human escalation when uncertainty > threshold                  |
| **Security Sentry** | Findings + patches or blocking comments                                         | Runs Semgrep/CodeQL/HMAC checklists; respects secret allow-list                  | Coordinates with governor for sensitive flows                              |
| **Doc Scribe**      | README/API/ADR updates, demo scripts                                            | Ensures human and agent onboarding stay current                                  | Syncs with `docs/pending_implementation_design.md`                         |

## End-to-End Workflow

1. **Issue Intake**: Product or Mission Control labels an issue with `agent:ready` and optional `epic:*` tag. Include
   story context, acceptance criteria, and links to design docs.
2. **Safety Gate**: Supervisor verifies `red-mode` and `needs-human-review` labels; logs decision. Governor overrides
   pause all automation.
3. **Branch & Draft PR**: Supervisor creates branch + Draft PR; posts Planner output as first comment.
4. **Sequential Roles**: Flow orchestrator triggers roles in order (Planner → Test Author → Implementer → Reviewer →
   Security → Doc Scribe). Each step leaves structured comments and commits.
5. **Validation**: `agents/tools/run_tests.py` executes PyTest/unit suites; optional UI smoke (`run_ui.py`) and perf (
   `k6.py`) workflows run in CI. Failures block progression.
6. **Observability Checks**: After implementation, agents fetch `/metrics`, review logs, and update risk status.
   Persistent anomalies open follow-up issues labeled `alignment:review`.
7. **Human Handoff**: On success, mark PR `ready for review`. On uncertainty or escalations, add `needs-human-review`,
   summarize blockers, and halt automation.

## Operational Guardrails

- **Diff Discipline**: Implementers must submit unified diffs validated by `git_ops`. Reject patches touching
  non-whitelisted roots or exceeding size thresholds.
- **Test Coverage**: PR merges require updated or new tests unless explicitly waived by human reviewer. Test Author
  advocates for coverage parity in Python and TypeScript.
- **Secrets & ENV Hygiene**: Only expose environment variables enumerated in `config/mcp/.env.example`. Never echo
  secret values in logs or comments.
- **Governor Compliance**: Call Alignment Governor APIs (`/api/governor/*`) through approved clients. Respect veto
  responses and log attempts.
- **Privacy Constraints**: When handling conversation data, defer to consent toggles and sanitization utilities in
  `modules/data_privacy.py`.

## Tooling Expectations

- Pin runtime versions via `agents/versions.py` (planned) or container images to avoid non-deterministic diffs.
- Prefer repo-local CLIs (poetry, npm scripts) over global binaries; run inside dedicated venv or Node environment.
- Capture artifacts (test results, SBOM, preview URLs) under `artifacts/` or GitHub Action summaries; avoid committing
  generated binaries.
- Use `scripts/repo_atlas.py` output for repository topology before large edits.

## Issue & Label Conventions

- `agent:ready`: Eligible for automation once requirements and links exist.
- `red-mode`: Automation freeze (only hotfix/security tasks allowed).
- `alignment:review`: Signals potential immersion or safety regression; requires governor & human audit.
- `needs-human-review`: Forces human intervention; Supervisor must respect and stand down.
- `epic:{A-F}`: Maps to implementation stories epics for reporting.
- Keep `docs/issue_story_map.json` current so automation can resolve stories from GitHub issues.

## Best Practices for Humans Partnering with Agents

- Provide crisp problem statements, explicit acceptance criteria, and validation hints in issues.
- Respond quickly to agent escalation comments to reduce idle branches.
- Label follow-up tasks with `handoff` and supply context (logs, metric IDs, reproduction scripts).
- Periodically audit agent comments and commits to refine prompts in `agents/prompts/`.
- Review and rotate access tokens; revoke unused credentials from GitHub secrets and `.env` templates.

## Onboarding & Local Dry Runs

1. Copy `.env.example` from `config/mcp/` and populate tokens locally.
2. Install agent dependencies (`pip install -r requirements.txt`, `npm install --prefix ui`, additional CLIs listed in
   `installed_packages.txt`).
3. Run `python -m agents.orchestrator.flow --dry-run <ISSUE_ID>` to simulate the pipeline and review required steps.
4. Verify governor connection with `python navigator.py --status` and ensure no `red-mode` label is active before real
   runs.

## Keeping This Guide Current

- Update this file whenever agent prompts, workflows, or guardrails change.
- Mirror changes in `docs/agentic_orchestration_plan.md` and mention major updates in release notes or internal
  briefings.
- Add TODOs to `docs/tasks.md` when gaps are discovered (new tools, missing scripts, updated governance rules).

Following this guide keeps Eternia's automation aligned with its narrative safety goals while enabling rapid, auditable
delivery.
