#!/usr/bin/env python3
"""
verify_mcp_config.py

Quick verification script to help test if the GitHub MCP setup is ready.
It checks:
- .junie/mcp/mcp.json exists and is valid JSON
- github server is defined under mcpServers
- the configured command for github (docker or native) is resolvable on PATH
- .junie/mcp/.env exists or GITHUB_TOKEN/GITHUB_TOKEN_RO present in the environment
- If using Docker, that env forwarding (-e GITHUB_TOKEN / -e GITHUB_PERSONAL_ACCESS_TOKEN) is configured

This script does not perform a full MCP JSON-RPC handshake, but it's enough to catch
common configuration issues before launching Junie.

Exit codes:
- 0: All checks passed
- 1: Missing files or invalid JSON
- 2: Missing github server config
- 3: Command not found on PATH
- 4: Missing required token variables
- 5: Docker config likely missing env forwarding

"""
from __future__ import annotations
import json
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_JSON = PROJECT_ROOT / ".junie/mcp/mcp.json"
ENV_FILE = PROJECT_ROOT / ".junie/mcp/.env"


def fail(code: int, msg: str) -> None:
    print(f"[verify-mcp] {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> int:
    # 1) mcp.json exists and is valid
    if not MCP_JSON.exists():
        fail(1, f"Missing MCP config: {MCP_JSON}")
    try:
        data = json.loads(MCP_JSON.read_text())
    except Exception as e:
        fail(1, f"Invalid JSON in {MCP_JSON}: {e}")

    # 2) github server present
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        fail(2, "mcpServers is missing or not an object in mcp.json")
    github = servers.get("github")
    if not isinstance(github, dict):
        fail(2, "'github' server not found under mcpServers in mcp.json")

    # 3) command resolvable
    command = github.get("command")
    if not command or not isinstance(command, str):
        fail(2, "github server 'command' is missing or not a string")
    resolved = shutil.which(command)
    if not resolved:
        # If not on PATH, provide a helpful hint about the Docker wrapper
        hint = (
            "Command not found on PATH: '{}'.\n"
            "- If you intend to run natively, install 'github-mcp' so it is available on PATH.\n"
            "- If you intend to run via Docker, create a symlink to scripts/mcp/github-mcp-docker.sh (see docs/mcp.md).\n"

            "  Example: ln -s \"$(pwd)/scripts/mcp/github-mcp-docker.sh\" /usr/local/bin/github-mcp"
        ).format(command)
        fail(3, hint)

    # 4) env readiness: either .junie/mcp/.env has token, or process env has it
    env_has_token = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_RO"))
    file_has_token = False
    file_token_value = None

    if ENV_FILE.exists():
        try:
            for line in ENV_FILE.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, _, value = line.partition("=")
                if key in {"GITHUB_TOKEN", "GITHUB_TOKEN_RO"}:
                    if value:
                        file_has_token = True
                        file_token_value = value

                        break
        except Exception:
            # Non-fatal; just ignore parsing issues and rely on env
            pass

    if not (env_has_token or file_has_token):
        fail(4, "No GitHub token found. Set GITHUB_TOKEN or GITHUB_TOKEN_RO in the environment or .junie/mcp/.env")

    # 4b) Light sanity check of token format (non-fatal)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_RO") or file_token_value or ""
    if token and len(token) < 20:
        print("[verify-mcp] Warning: GitHub token looks unusually short — ensure it's a real PAT/fine-grained token with required scopes.")

    # 5) If using Docker for github, ensure env forwarding is present
    args = github.get("args") or []
    env_cfg = github.get("env") or {}
    uses_docker = command == "docker" or (resolved and "docker" in resolved)
    if uses_docker:
        args_set = set(arg.strip() for arg in args if isinstance(arg, str))
        missing_env_flags = []
        for var in ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN"):
            if "-e" in args_set and var in args_set:
                continue
            # Look for pattern: ["-e", "VAR"]; simple check
            if not ("-e" in args_set and any(a == var for a in args)):
                missing_env_flags.append(var)
        missing_env_map = []
        for var in ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN"):
            if var not in env_cfg:
                missing_env_map.append(var)
        if missing_env_flags or missing_env_map:
            example = (
                "Docker run is missing env forwarding for: {}.\n"
                "Ensure github.args includes: -e GITHUB_TOKEN -e GITHUB_PERSONAL_ACCESS_TOKEN\n"
                "And github.env maps them, e.g.:\n"
                "  \"env\": {\n"
                "    \"GITHUB_PERSONAL_ACCESS_TOKEN\": \"env://GITHUB_TOKEN_RO\",\n"
                "    \"GITHUB_TOKEN\": \"env://GITHUB_TOKEN_RO\"\n"
                "  }\n"
            ).format(", ".join(missing_env_flags or missing_env_map))
            fail(5, example)
        # Provide a ready-to-run diagnostic command
        print("[verify-mcp] Info: To verify env propagation inside the container, run:\n"
              "  docker run --rm -i -e GITHUB_TOKEN -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server env | grep GITHUB_")

    print("[verify-mcp] OK: mcp.json valid, github server configured, command found, token present.")
    print("[verify-mcp] Note: If you still get 401 Unauthorized, ensure the token has scopes: repo (read), issues:write, pull_requests:write as needed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
