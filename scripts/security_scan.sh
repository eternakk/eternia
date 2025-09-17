#!/usr/bin/env bash
set -euo pipefail

CMD=${1:-all}

echo "[security-scan] Starting security scan: $CMD"

run_pip_audit() {
  if command -v pip-audit >/dev/null 2>&1; then
    echo "[security-scan] Running pip-audit..."
    pip-audit || {
      echo "[security-scan] pip-audit found vulnerabilities." >&2
      return 1
    }
  else
    echo "[security-scan] pip-audit not installed. Install with: pip install pip-audit"
  fi
}

run_safety() {
  if command -v safety >/dev/null 2>&1; then
    echo "[security-scan] Running safety..."
    safety check || {
      echo "[security-scan] safety found vulnerabilities." >&2
      return 1
    }
  else
    echo "[security-scan] safety not installed. Install with: pip install safety"
  fi
}

run_npm_audit() {
  if command -v npm >/dev/null 2>&1; then
    if [ -f package.json ]; then
      echo "[security-scan] Running npm audit (high+ only)..."
      npm audit --audit-level=high || {
        echo "[security-scan] npm audit reported issues (>= high)." >&2
        return 1
      }
    else
      echo "[security-scan] No package.json found; skipping npm audit."
    fi
  else
    echo "[security-scan] npm not installed; skipping frontend audit."
  fi
}

run_trivy() {
  if command -v trivy >/dev/null 2>&1; then
    echo "[security-scan] Running trivy on local Docker images..."
    images=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' || true)
    if [ -z "$images" ]; then
      echo "[security-scan] No local images found to scan."
      return 0
    fi
    for img in $images; do
      echo "[security-scan] Scanning $img"
      trivy image --severity HIGH,CRITICAL "$img" || {
        echo "[security-scan] trivy found vulnerabilities in $img." >&2
        return 1
      }
    done
  else
    echo "[security-scan] trivy not installed; skipping image scan. Install: https://aquasecurity.github.io/trivy/"
  fi
}

case "$CMD" in
  deps)
    run_pip_audit || exit 1
    run_safety || exit 1
    run_npm_audit || exit 1
    ;;
  images)
    run_trivy || exit 1
    ;;
  all)
    run_pip_audit || true
    run_safety || true
    run_npm_audit || true
    run_trivy || true
    ;;
  *)
    echo "Usage: $0 [deps|images|all]";
    exit 2
    ;;
esac