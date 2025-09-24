#!/usr/bin/env python3
"""
list_issues.py — Minimal GitHub issues lister for Eternia

Purpose
- Provide a simple, dependency-light CLI to list GitHub issues for a repository.
- Designed to work regardless of MCP server availability; uses the GitHub REST API directly.

Auth
- Reads token from (in order):
  1) GITHUB_TOKEN
  2) GITHUB_TOKEN_RO
  3) .junie/mcp/.env (keys: GITHUB_TOKEN or GITHUB_TOKEN_RO)

Usage examples
- python3 scripts/list_issues.py --repo eternakk/eternia
- python3 scripts/list_issues.py --repo eternakk/eternia --state open --limit 20
- python3 scripts/list_issues.py --repo eternakk/eternia --labels

Exit codes
- 0 success
- 1 invalid args
- 2 auth/token missing
- 3 GitHub API error

Notes
- The GitHub "issues" API endpoint also returns pull requests when not filtered out by parameter; we filter out PRs by default unless --include-prs is set.

"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_ENV_PATH = PROJECT_ROOT / ".junie" / "mcp" / ".env"
GITHUB_API = "https://api.github.com"


def load_token() -> Optional[str]:
    # 1) Process env
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_RO")
    if token:
        return token.strip()
    # 2) .junie/mcp/.env
    try:
        if MCP_ENV_PATH.exists():
            for line in MCP_ENV_PATH.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, _, value = line.partition("=")
                if key in {"GITHUB_TOKEN", "GITHUB_TOKEN_RO"} and value:
                    return value.strip()
    except Exception:
        pass
    return None


def build_request(url: str, token: str) -> urllib.request.Request:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "eternia-list-issues/1.0")
    return req


def fetch_json(url: str, token: str) -> List[Dict]:
    req = build_request(url, token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, list) else [data]
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
        print(f"[list_issues] HTTP {e.code} error for {url}: {detail}", file=sys.stderr)
        sys.exit(3)
    except urllib.error.URLError as e:
        print(f"[list_issues] Network error: {e}", file=sys.stderr)
        sys.exit(3)


def paginate_issues(
        owner: str, repo: str, token: str, query: Dict[str, str], limit: int
) -> List[Dict]:
    # GitHub paginates with page/per_page; default 30, max 100
    results: List[Dict] = []
    page = 1
    per_page = min(100, max(1, limit))
    while len(results) < limit:
        q = query.copy()
        q.update({"page": str(page), "per_page": str(per_page)})
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues?{urlencode(q)}"
        batch = fetch_json(url, token)
        if not batch:
            break
        results.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return results[:limit]


def format_row(item: Dict) -> str:
    number = item.get("number")
    title = (item.get("title") or "").replace("\n", " ").strip()
    state = item.get("state")
    labels = ",".join(
        [lbl.get("name") for lbl in item.get("labels", []) if isinstance(lbl, dict)]
    )
    assignee = (
        (item.get("assignee") or {}).get("login")
        if isinstance(item.get("assignee"), dict)
        else None
    )
    created = item.get("created_at")
    return f"#{number} [{state}] {title} | labels={labels} | assignee={assignee or '-'} | created={created}"


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="List GitHub issues for a repository")
    p.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/name format, e.g., eternakk/eternia",
    )
    p.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="open",
        help="Filter by state",
    )
    p.add_argument(
        "--labels", default="", help="Comma-separated label names to filter by"
    )
    p.add_argument(
        "--assignee", default=None, help='Filter by assignee login (or "none")'
    )
    p.add_argument("--creator", default=None, help="Filter by creator login")
    p.add_argument(
        "--include-prs",
        action="store_true",
        help="Include pull requests in output (off by default)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Maximum number of items to return (default 30)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-friendly lines",
    )
    p.add_argument(
        "--url", action="store_true", help="Include HTML URL in human output"
    )

    args = p.parse_args(argv)

    if "/" not in args.repo:
        print("[list_issues] --repo must be in owner/name format", file=sys.stderr)
        return 1
    owner, repo = args.repo.split("/", 1)

    token = load_token()
    if not token:
        print(
            "[list_issues] Missing GitHub token. Set GITHUB_TOKEN or GITHUB_TOKEN_RO, or add it to .junie/mcp/.env",
            file=sys.stderr,
        )
        return 2
    if len(token) < 20:
        print(
            "[list_issues] Warning: token looks short; you may get 401 Unauthorized.",
            file=sys.stderr,
        )

    query: Dict[str, str] = {
        "state": args.state,
        "direction": "desc",
        "sort": "created",
    }
    if args.labels:
        query["labels"] = args.labels
    if args.assignee is not None:
        query["assignee"] = args.assignee
    if args.creator is not None:
        query["creator"] = args.creator

    items = paginate_issues(owner, repo, token, query, limit=max(1, args.limit))

    # Filter out PRs unless requested
    if not args.include_prs:
        items = [it for it in items if "pull_request" not in it]

    if args.json:
        print(json.dumps(items, indent=2))
    else:
        for it in items:
            line = format_row(it)
            if args.url and "html_url" in it:
                line += f"\n    {it['html_url']}"
            print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
