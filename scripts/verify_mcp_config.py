#!/usr/bin/env python3
"""
verify_mcp_config.py

Quick verification script to help test if the GitHub MCP setup is ready.
It checks:
- .junie/mcp/mcp.json exists and is valid JSON
- github server is defined under mcpServers
- the configured command for github (default: github-mcp) is resolvable on PATH
- .junie/mcp/.env exists or GITHUB_TOKEN/GITHUB_TOKEN_RO present in the environment

This script does not perform a full MCP JSON-RPC handshake, but it's enough to catch
common configuration issues before launching Junie.

Exit codes:
- 0: All checks passed
- 1: Missing files or invalid JSON
- 2: Missing github server config
- 3: Command not found on PATH
- 4: Missing required token variables
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
            "- Install the GitHub MCP server so 'github-mcp' is available, OR\n"
            "- Create a symlink to scripts/mcp/github-mcp-docker.sh (see docs/mcp.md).\n"
            "  Example: ln -s \"$(pwd)/scripts/mcp/github-mcp-docker.sh\" /usr/local/bin/github-mcp"
        ).format(command)
        fail(3, hint)

    # 4) env readiness: either .junie/mcp/.env has token, or process env has it
    env_has_token = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_RO"))
    file_has_token = False
    if ENV_FILE.exists():
        try:
            for line in ENV_FILE.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.split("=", 1)[0] in {"GITHUB_TOKEN", "GITHUB_TOKEN_RO"}:
                    if line.split("=", 1)[1]:
                        file_has_token = True
                        break
        except Exception:
            # Non-fatal; just ignore parsing issues and rely on env
            pass

    if not (env_has_token or file_has_token):
        fail(4, "No GitHub token found. Set GITHUB_TOKEN or GITHUB_TOKEN_RO in the environment or .junie/mcp/.env")

    print("[verify-mcp] OK: mcp.json valid, github server configured, command found, token present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
