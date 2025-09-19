#!/usr/bin/env bash
# Wrapper to run the SQLite MCP server via Docker.
# Usage:
#   1) Ensure Docker is running.
#   2) Optionally set SQLITE_MCP_IMAGE to override the image tag.
#   3) Optionally set SQLITE_DB and SQLITE_MODE (defaults below) or pass args.
#   4) Run this script directly, or point Junie MCP config's `command` to this file.
#
# Defaults align with .junie/mcp/mcp.json:
#   --db ./artifacts/dev.sqlite3 --mode ro
#
# Examples:
#   SQLITE_DB=./artifacts/dev.sqlite3 SQLITE_MODE=ro scripts/mcp/mcp-sqlite-docker.sh
#   SQLITE_MCP_IMAGE=ghcr.io/modelcontextprotocol/sqlite-mcp:latest scripts/mcp/mcp-sqlite-docker.sh --db ./artifacts/other.sqlite3 --mode ro

set -euo pipefail

IMAGE="${SQLITE_MCP_IMAGE:-ghcr.io/modelcontextprotocol/sqlite-mcp:latest}"

# Resolve project root and default DB path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEFAULT_DB="${PROJECT_ROOT}/artifacts/dev.sqlite3"
DB_PATH="${SQLITE_DB:-${DEFAULT_DB}}"
MODE="${SQLITE_MODE:-ro}"

if [[ ! -f "${DB_PATH}" ]]; then
  echo "[mcp-sqlite-docker] WARNING: DB file not found at ${DB_PATH}. The server may fail if run in ro mode." >&2
fi

# Build args: allow user to override by passing explicit args
ARGS=("--db" "/workspace/$(realpath --relative-to="${PROJECT_ROOT}" "${DB_PATH}")" "--mode" "${MODE}")
if [[ $# -gt 0 ]]; then
  ARGS=("$@")
fi

exec docker run \
  --rm -i \
  -v "${PROJECT_ROOT}:/workspace:rw" \
  "${IMAGE}" \
  "${ARGS[@]}"