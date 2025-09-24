#!/usr/bin/env python3
"""
list_org_repos.py — List repositories under a GitHub organization

Purpose
- Provide a simple, dependency-light CLI to list repositories for a GitHub org.
- Mirrors the auth/structure of scripts/list_issues.py so it works with your existing setup.

Auth
- Reads token from (in order):
  1) GITHUB_TOKEN
  2) GITHUB_TOKEN_RO
  3) .junie/mcp/.env (keys: GITHUB_TOKEN or GITHUB_TOKEN_RO)

Usage examples
- python3 scripts/list_org_repos.py --org eternakk
- python3 scripts/list_org_repos.py --org eternakk --type all --limit 200
- python3 scripts/list_org_repos.py --org eternakk --json
- python3 scripts/list_org_repos.py --org eternakk --only-names

Exit codes
- 0 success
- 1 invalid args
- 2 auth/token missing
- 3 GitHub API error

Notes
- For private/org-internal repos, your token must have access to the organization and repositories.
- If you see 401/403/404, check token identity, scopes, and org SSO/authorization.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlencode
import urllib.request
import urllib.error

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_ENV_PATH = PROJECT_ROOT / '.junie' / 'mcp' / '.env'
GITHUB_API = 'https://api.github.com'


def load_token() -> Optional[str]:
    # 1) Process env
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_TOKEN_RO')
    if token:
        return token.strip()
    # 2) .junie/mcp/.env
    try:
        if MCP_ENV_PATH.exists():
            for line in MCP_ENV_PATH.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, _, value = line.partition('=')
                if key in {'GITHUB_TOKEN', 'GITHUB_TOKEN_RO'} and value:
                    return value.strip()
    except Exception:
        pass
    return None


def build_request(url: str, token: str) -> urllib.request.Request:
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    req.add_header('User-Agent', 'eternia-list-org-repos/1.0')
    return req


def fetch_json(url: str, token: str):
    req = build_request(url, token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        print(f"[list_org_repos] HTTP {e.code} error for {url}: {detail}", file=sys.stderr)
        sys.exit(3)
    except urllib.error.URLError as e:
        print(f"[list_org_repos] Network error: {e}", file=sys.stderr)
        sys.exit(3)


def paginate_org_repos(org: str, token: str, query: Dict[str, str], limit: int) -> List[Dict]:
    results: List[Dict] = []
    page = 1
    per_page = min(100, max(1, limit))
    while len(results) < limit:
        q = query.copy()
        q.update({'page': str(page), 'per_page': str(per_page)})
        url = f"{GITHUB_API}/orgs/{org}/repos?{urlencode(q)}"
        batch = fetch_json(url, token)
        if not isinstance(batch, list) or not batch:
            break
        results.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return results[:limit]


def format_row(repo: Dict, include_url: bool = False) -> str:
    name = repo.get('name') or ''
    private = bool(repo.get('private'))
    archived = bool(repo.get('archived'))
    fork = bool(repo.get('fork'))
    language = repo.get('language') or '-'
    updated = repo.get('updated_at') or '-'
    visibility = repo.get('visibility') or ('private' if private else 'public')
    line = f"{name} | visibility={visibility} | archived={archived} | fork={fork} | lang={language} | updated={updated}"
    if include_url and 'html_url' in repo:
        line += f"\n    {repo['html_url']}"
    return line


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description='List GitHub repositories under an organization')
    p.add_argument('--org', required=True, help='Organization login, e.g., eternakk')
    p.add_argument('--type', choices=['all', 'public', 'private', 'forks', 'sources', 'member'], default='all', help='Repository type filter (GitHub API)')
    p.add_argument('--sort', choices=['created', 'updated', 'pushed', 'full_name'], default='full_name', help='Sort field')
    p.add_argument('--direction', choices=['asc', 'desc'], default='asc', help='Sort direction')
    p.add_argument('--limit', type=int, default=100, help='Maximum number of repos to return (default 100)')
    p.add_argument('--json', action='store_true', help='Output JSON instead of human-friendly lines')
    p.add_argument('--url', action='store_true', help='Include HTML URL in human output')
    p.add_argument('--only-names', action='store_true', help='Print only repository names (overrides other human fields)')

    args = p.parse_args(argv)

    token = load_token()
    if not token:
        print('[list_org_repos] Missing GitHub token. Set GITHUB_TOKEN or GITHUB_TOKEN_RO, or add it to .junie/mcp/.env', file=sys.stderr)
        return 2
    if len(token) < 20:
        print('[list_org_repos] Warning: token looks short; you may get 401 Unauthorized.', file=sys.stderr)

    query: Dict[str, str] = {
        'type': args.type,
        'sort': args.sort,
        'direction': args.direction,
    }

    items = paginate_org_repos(args.org, token, query, limit=max(1, args.limit))

    if args.json:
        print(json.dumps(items, indent=2))
    else:
        only_names = args.only_names
        for repo in items:
            if only_names:
                print(repo.get('name', ''))
            else:
                print(format_row(repo, include_url=args.url))

    return 0


if __name__ == '__main__':
    sys.exit(main())
