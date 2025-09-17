#!/usr/bin/env bash
# Wrapper to run the S3 MCP server via Docker.
# Requires AWS credentials and region in your environment.
# Override image with S3_MCP_IMAGE if needed.
#
# Usage:
#   export AWS_REGION=... AWS_ACCESS_KEY_ID_RO=... AWS_SECRET_ACCESS_KEY_RO=...
#   scripts/mcp/s3-mcp-server-docker.sh

set -euo pipefail

IMAGE="${S3_MCP_IMAGE:-ghcr.io/modelcontextprotocol/s3-mcp-server:latest}"

missing=()
[[ -z "${AWS_REGION:-}" ]] && missing+=(AWS_REGION)
[[ -z "${AWS_ACCESS_KEY_ID_RO:-}" ]] && missing+=(AWS_ACCESS_KEY_ID_RO)
[[ -z "${AWS_SECRET_ACCESS_KEY_RO:-}" ]] && missing+=(AWS_SECRET_ACCESS_KEY_RO)
if (( ${#missing[@]} > 0 )); then
  echo "[s3-mcp-server-docker] ERROR: Missing env vars: ${missing[*]}" >&2
  exit 1
fi

exec docker run \
  --rm -i \
  -e AWS_REGION \
  -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID_RO}" \
  -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY_RO}" \
  "${IMAGE}"