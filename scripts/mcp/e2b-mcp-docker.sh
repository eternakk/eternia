#!/usr/bin/env bash
# Wrapper to run the E2B MCP server via Docker.
# Requires E2B_API_KEY in your environment.
# Override image with E2B_MCP_IMAGE if needed.
#
# Usage:
#   export E2B_API_KEY=... 
#   scripts/mcp/e2b-mcp-docker.sh

set -euo pipefail

IMAGE="${E2B_MCP_IMAGE:-ghcr.io/e2b-dev/e2b-mcp:latest}"

if [[ -z "${E2B_API_KEY:-}" ]]; then
  echo "[e2b-mcp-docker] ERROR: E2B_API_KEY is not set." >&2
  exit 1
fi

exec docker run \
  --rm -i \
  -e E2B_API_KEY \
  "${IMAGE}"