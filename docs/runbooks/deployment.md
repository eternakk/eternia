# Deployment Runbook

Last updated: 2025-09-17

Purpose: Provide a concise, actionable guide to deploy Eternia safely across environments (dev, staging, prod).

Prerequisites:
- Docker and docker-compose installed locally
- Access to container registry and infrastructure credentials (KMS/Secrets Manager)
- ENV files populated (see config/settings and .env examples)

Environments:
- Development: local docker-compose, ephemeral data
- Staging: managed environment for pre-prod validation
- Production: HA setup with monitoring, backups, and branch protection

Steps:
1) Pre-deploy checks
- [ ] All CI checks passing (tests, lint, type, security scan)
- [ ] Changelog updated and version bump if required
- [ ] Database migrations prepared (yoyo/alembic) and reviewed
- [ ] Feature flags reviewed (config/config_manager)

2) Build & Scan
- [ ] Build images: docker-compose build or CI pipeline
- [ ] Dependency scan: scripts/security_scan.sh deps
- [ ] Image scan: scripts/security_scan.sh images (if Trivy/Grype available)

3) Release
- [ ] Push images to registry
- [ ] Apply infra changes (terraform apply) if needed
- [ ] Deploy to target environment (helm/kustomize/docker-compose)
- [ ] Run migrations (scripts/migrate.sh if present)

4) Verify
- [ ] Health endpoints respond (GET /api/health if present)
- [ ] Metrics available (/metrics via exporter)
- [ ] Logs clean (no new errors)
- [ ] Smoke tests pass (core API and UI)

5) Rollback
- [ ] Keep previous image tag available
- [ ] Revert deployment manifests or use helm rollback
- [ ] Restore backup if data migration failed (scripts/restore_backup.py)

Operational Notes:
- CSP and security headers are enforced at API layer (services/api/server.py)
- Rate limiting via slowapi; adjust limits per environment
- Observability: Prometheus + tracing (if enabled)

Contacts:
- On-call: #eternia-ops
- Owners: Engineering Automation
