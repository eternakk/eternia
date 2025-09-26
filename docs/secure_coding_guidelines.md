# Eternia Secure Coding Guidelines

Audience: All Eternia contributors (backend, frontend, infra). These practices are tailored to our current stack: Python 3.12, FastAPI, httpx/anyio, React UI, and our JWT-based auth.

Status: Adopted 2025-09-19

---

## 1) Environment, secrets, and configuration

- Environment flag: ETERNIA_ENV (or APP_ENV) in {development, production}. Treat prod/production as production.
- JWT secrets (see README Secrets & Environments):
  - Development priority: JWT_SECRET/JWT_SECRET_KEY from env; or if SECRET_KEY_ENCRYPTION_PASSWORD is set, use encrypted artifacts/jwt_secret.txt; otherwise artifacts/dev.jwt_secret.txt.
  - Production: JWT_SECRET (or JWT_SECRET_KEY) required, or encrypted artifacts/jwt_secret.txt via SECRET_KEY_ENCRYPTION_PASSWORD. If neither present, startup must fail.
- Never commit secrets. artifacts/, data/, and logs/ are gitignored. Do not store data under docs/.
- Use typed config objects; validate env at startup (required keys, allowed values). Fail fast.

## 2) Authentication, authorization, and session safety

- JWT contents: keep minimal (sub, iat, exp, roles/permissions). Avoid PII.
- Set exp/nbf/iat; enforce clock skew tolerance in validation.
- Implement token rotation support at the service layer (task 603). For now, keep access tokens short-lived and refresh with server verification.
- Scope permissions via explicit allow lists per endpoint. Prefer dependency-injected guards in FastAPI routers.
- Reject tokens signed with none/weak algs. Pin to HS256/RS256 as configured. Validate kid only from our allow list.

## 3) Input validation and data handling

- Validate all external inputs (body, query, headers, path, forms) using Pydantic models with strict types; set extra=forbid.
- Apply length and range bounds for strings/numbers; whitelist enums where applicable.
- Sanitize and normalize: trim strings; normalize unicode where relevant; reject control chars for identifiers.
- Output encoding: rely on frameworks’ escaping (Jinja/React). Never build HTML by string concatenation from user input.

## 4) Transport and endpoint hardening

- Enforce HTTPS in production; behind proxies set and validate X-Forwarded-* headers via trusted proxy list.
- Rate limiting is in place; keep reasonable defaults; add per-endpoint overrides for sensitive routes.
- Content Security Policy (CSP) headers are enabled (task 601). When adding new front-end resources, update CSP.
- CORS: default deny; explicitly allow origins/methods/headers needed by the UI.

## 5) Logging, monitoring, and secrets redaction

- Use structured logging (modules/logging_config.py). Include request IDs and user IDs where safe.
- Never log secrets, JWTs, passwords, tokens, or full request bodies. Redact fields: password, token, authorization, secret, key.
- Error traces may include data; prefer logging IDs and context, not payloads.
- Expose metrics for auth failures, rate limits, and unusual patterns.

## 6) Dependency, supply-chain, and build pipeline

- Pin direct dependencies; update regularly and address deprecations.
- Security scanning is enabled in CI for dependencies and container images (task 408). Add findings to the backlog with CVE links.
- Verify integrity of third-party assets. Prefer npm/pip registries over raw URLs.
- Build containers as non-root; minimize layers; set USER to a dedicated UID.

## 7) Code execution, SSRF, deserialization

- Never eval/exec arbitrary strings. Avoid pickle on untrusted inputs.
- For HTTP clients (httpx), disable auto-redirects/cookies where not needed. Validate target hosts; avoid user-controlled URLs for internal networks (SSRF).
- For file parsing (images, archives), use libraries with safe defaults; set size/time limits.

## 8) Database and storage

- Use parameterized queries or ORM query builders; never concatenate SQL.
- Apply data retention policies (task 701) and clearly mark PII fields. Encrypt at rest where supported.
- Backups must be access-controlled and encrypted. Test restore procedures.

## 9) Frontend security (React/UI)

- Rely on React’s escaping. Avoid dangerouslySetInnerHTML; if unavoidable, sanitize with a vetted library.
- Keep CSP alignments with any new script/style sources.
- Prefer same-site cookies for sensitive flows if adopted; otherwise keep tokens in memory and never localStorage for high-risk endpoints.
- Implement robust keyboard accessibility, ARIA roles, and focus management; avoid onClick-only interactions.

## 10) Secrets handling in code reviews

- Run local secret scanners before commits when touching config.
- Review diffs for accidental token leaks. If leaked, rotate immediately and purge history if feasible.

## 11) Developer training checklist

- Read these guidelines and the README Secrets & Environments section.
- Complete a secure coding module (OWASP Top 10) annually.
- Run through an incident response tabletop (see runbooks) twice per year.
- Add unit tests for validation and authorization branches when adding endpoints.

## References

- OWASP ASVS, OWASP Top 10
- FastAPI Security Best Practices
- Python Security (Bandit), dependency scanning

