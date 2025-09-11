# Dependency Audit — 2025-09-11

This report summarizes dependency vulnerabilities and available updates across Python (pip) and UI (npm) package managers. Majors are batched/skipped with notes about potential breaking changes.

## Python (requirements.txt)

No known vulnerabilities found by pip-audit.

### Available updates (Python)

- Patch/minor updates:

| Package | Current | Latest | Update Type |
|---|---:|---:|---|
| hypothesis | 6.98.8 | 6.138.15 | minor |
| tomli | 2.0.1 | 2.2.1 | minor |

- Majors or unbounded (batched/skipped):

| Package | Current | Latest | Note |
|---|---:|---:|---|
| pytest | 7.4.4 | 8.4.2 | Potential breaking changes; review release notes before upgrading. |
| pytest-asyncio | 0.23.5 | 1.1.0 | Potential breaking changes; review release notes before upgrading. |
| pytest-benchmark | 4.0.0 | 5.1.0 | Potential breaking changes; review release notes before upgrading. |
| pytest-cov | 4.1.0 | 7.0.0 | Potential breaking changes; review release notes before upgrading. |
| sse-starlette | 2.0.0 | 3.0.2 | Potential breaking changes; review release notes before upgrading. |
| yoyo-migrations | 8.2.0 | 9.0.0 | Potential breaking changes; review release notes before upgrading. |

## UI (ui/package.json)

No known vulnerabilities found by npm audit.

### Available updates (UI)

No update information available.

## Next steps

- Would you like me to apply the listed patch/minor updates and run the test suites (pytest, Vitest, Cypress) to verify? If all tests pass, I can open a PR with the changes. Majors will be left for a separate migration plan.
