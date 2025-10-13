#!/usr/bin/env bash
# Lightweight wrapper to run the GitHub MCP server via Docker.
# Usage:
#   1) Ensure you have Docker installed and running.
#   2) Ensure GITHUB_TOKEN is available in the environment (exported) or passed inline.
#   3) Optionally set IMAGE tag via GITHUB_MCP_IMAGE (defaults to latest).
#   4) Run this script directly, or point Junie MCP config's `command` to this file.
#
# Example manual run:
#   export GITHUB_TOKEN=ghp_xxx
#   scripts/mcp/github-mcp-docker.sh
#
# Example using a different image tag:
#   GITHUB_MCP_IMAGE=ghcr.io/modelcontextprotocol/github-mcp:0.1.2 scripts/mcp/github-mcp-docker.sh
#
# Notes:
# - The script runs Docker in interactive mode and forwards STDIN/STDOUT, as Junie connects via stdio.
# - No repo path mount is strictly required by the server, but we mount the current project directory
#   at /workspace (read-only) in case the server or tools reference local files in the future.
# - If you don't want the mount, remove the -v line below.
# - This wrapper auto-loads .junie/mcp/.env and ~/.codex/mcp/{github,.}.env if present, and uses GITHUB_TOKEN_RO as a fallback for GITHUB_TOKEN.

set -euo pipefail

# Resolve project root early
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Auto-load env from local Junie or Codex config if present
ENV_FILES=(
  "${PROJECT_ROOT}/.junie/mcp/.env"
  "${HOME}/.codex/mcp/github.env"
  "${HOME}/.codex/mcp/.env"
)

for env_file in "${ENV_FILES[@]}"; do
  if [[ -f "${env_file}" ]]; then
    # shellcheck disable=SC1090
    set -a
    . "${env_file}"
    set +a
  fi
done

IMAGE="${GITHUB_MCP_IMAGE:-ghcr.io/modelcontextprotocol/github-mcp:latest}"

# Fallback: if only GITHUB_TOKEN_RO is set, use it as GITHUB_TOKEN
if [[ -z "${GITHUB_TOKEN:-}" && -n "${GITHUB_TOKEN_RO:-}" ]]; then
  export GITHUB_TOKEN="${GITHUB_TOKEN_RO}"
fi

# Validate token availability
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "[github-mcp-docker] ERROR: GITHUB_TOKEN is not set." >&2
  echo "Provide it by either: (1) exporting GITHUB_TOKEN in your shell; or (2) setting it in .junie/mcp/.env or ~/.codex/mcp/github.env (both auto-loaded)." >&2
  echo "Ensure the token has appropriate scopes (read, write:issues, write:pull_requests if needed)." >&2
  exit 1
fi

# Ensure the image is available locally; if access is denied, attempt GHCR auth using env vars
ensure_image_pulled() {
  # If image already present locally, skip pull
  if docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    return
  fi
  # Try to pull and capture output
  if out=$(docker pull "${IMAGE}" 2>&1); then
    return
  fi
  # If pull failed, check if it looks like an auth issue and attempt ghcr login
  if echo "${out}" | grep -qiE "denied|unauthorized|authentication required|requested access to the resource is denied"; then
    local user pass
    user="${GHCR_USERNAME:-${GITHUB_USERNAME:-}}"
    pass="${GHCR_TOKEN:-${GHCR_PAT:-${GITHUB_TOKEN:-}}}"
    if [[ -n "${user}" && -n "${pass}" ]]; then
      echo "[github-mcp-docker] Attempting ghcr.io login for ${user} to pull ${IMAGE}..." >&2
      if echo "${pass}" | docker login ghcr.io -u "${user}" --password-stdin >/dev/null 2>&1; then
        if ! docker pull "${IMAGE}"; then
          echo "[github-mcp-docker] ERROR: Pull failed even after ghcr.io login. Ensure the token has read:packages and the image exists: ${IMAGE}" >&2
          exit 1
        fi
      else
        echo "[github-mcp-docker] ERROR: ghcr.io login failed. Set GHCR_USERNAME and GHCR_TOKEN (or GHCR_PAT/GITHUB_TOKEN with read:packages) and try again." >&2
        exit 1
      fi
    else
      echo "[github-mcp-docker] ERROR: GHCR denied access to ${IMAGE}. Provide GHCR_USERNAME and GHCR_TOKEN (or GHCR_PAT, or a GITHUB_TOKEN with read:packages) in .junie/mcp/.env, or run 'docker login ghcr.io' manually." >&2
      exit 1
    fi
  else
    echo "[github-mcp-docker] ERROR: Failed to pull ${IMAGE}: ${out}" >&2
    exit 1
  fi
}

ensure_image_pulled

# Docker run with stdio and env passthrough
exec docker run \
  --rm -i \
  -e GITHUB_TOKEN \
  -v "${PROJECT_ROOT}:/workspace:ro" \
  "${IMAGE}"
