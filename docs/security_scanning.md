# Security Scanning

Last updated: 2025-09-17

This document describes how to run dependency and container image security scans for Eternia.

Quick start
- Run dependency scans:
  - bash scripts/security_scan.sh deps
- Run container image scans (if Trivy is installed):
  - bash scripts/security_scan.sh images
- Run everything (best-effort, non-fatal on missing tools):
  - bash scripts/security_scan.sh all

Tools
- pip-audit: audits Python dependencies against known vulnerabilities
- safety: alternative Python dependency vulnerability checker
- npm audit: scans frontend dependencies (requires Node/npm)
- trivy: scans container images for vulnerabilities (requires Docker and Trivy)

Notes
- The script exits non-zero for targeted modes (deps, images) if vulnerabilities are found.
- For CI integration, call the script with deps and images as separate steps; consider allowing low/medium findings while failing on high/critical.
- Container image scanning requires images to be built locally or pulled from a registry before scanning.
