#!/usr/bin/env bash
# Wrapper to run the Postgres MCP server via Docker.
# Passes standard PG* env vars from your environment.
#
# Required env vars (read-only per mcp.json):
#   PGHOST, PGPORT, PGDATABASE, PGUSER_RO -> mapped to PGUSER inside container, PGPASSWORD_RO -> PGPASSWORD
# Optional: PGSSLMODE (defaults to require if not set)
#
# Usage:
#   export PGHOST=... PGPORT=5432 PGDATABASE=... PGUSER_RO=... PGPASSWORD_RO=...
#   scripts/mcp/server-postgres-docker.sh
#
# Override image with POSTGRES_MCP_IMAGE if needed.

set -euo pipefail

IMAGE="${POSTGRES_MCP_IMAGE:-ghcr.io/modelcontextprotocol/postgres-mcp:latest}"

# Validate required vars
missing=()
[[ -z "${PGHOST:-}" ]] && missing+=(PGHOST)
[[ -z "${PGPORT:-}" ]] && missing+=(PGPORT)
[[ -z "${PGDATABASE:-}" ]] && missing+=(PGDATABASE)
[[ -z "${PGUSER_RO:-}" ]] && missing+=(PGUSER_RO)
[[ -z "${PGPASSWORD_RO:-}" ]] && missing+=(PGPASSWORD_RO)
if (( ${#missing[@]} > 0 )); then
  echo "[server-postgres-docker] ERROR: Missing env vars: ${missing[*]}" >&2
  exit 1
fi

SSL_MODE="${PGSSLMODE:-require}"

exec docker run \
  --rm -i \
  -e PGHOST -e PGPORT -e PGDATABASE \
  -e PGUSER="${PGUSER_RO}" \
  -e PGPASSWORD="${PGPASSWORD_RO}" \
  -e PGSSLMODE="${SSL_MODE}" \
  "${IMAGE}"