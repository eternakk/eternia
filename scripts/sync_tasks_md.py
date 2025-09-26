#!/usr/bin/env python3
"""
Sync docs/tasks.md with GitHub Issues

Purpose
- Parse docs/tasks.md for checkbox tasks and sync them to GitHub issues in a target repo.
- Dry-run by default; apply changes with --apply.
- Helps when MCP is unavailable or you prefer a direct CLI.

Conventions
- We derive an issue title in the form: [Task {id}] {title}
- Labels used by default:
  - For unchecked tasks: Todos + tasks-md
  - For checked tasks: Done + tasks-md (issue will be closed)

Token resolution order (same as scripts/list_issues.py):
1) GITHUB_TOKEN
2) GITHUB_TOKEN_RO
3) .junie/mcp/.env (keys: GITHUB_TOKEN or GITHUB_TOKEN_RO)

Examples
- Dry-run (plan only):
  python3 scripts/sync_tasks_md.py --repo eternakk/eternia

- Apply changes:
  python3 scripts/sync_tasks_md.py --repo eternakk/eternia --apply

- Limit scanning to specific IDs:
  python3 scripts/sync_tasks_md.py --repo eternakk/eternia --only-ids 405,407,409

Exit codes
- 0 success
- 1 invalid args
- 2 auth/token missing
- 3 GitHub API error
- 4 tasks.md missing or parse failure

Note
- This script will inspect existing issues (state=all) and match by title prefix "[Task {id}]".
- If an unchecked task has a closed issue, it will reopen it when --apply is passed.
- If a checked task has an open issue, it will close it when --apply is passed.
- Label updates are applied to reflect /Todos/Done state.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_MD = PROJECT_ROOT / "docs" / "tasks.md"
MCP_ENV_PATH = PROJECT_ROOT / ".junie" / "mcp" / ".env"
GITHUB_API = "https://api.github.com"

TASK_RE = re.compile(r"^\[(?P<mark>[ xX])\]\s*(?P<id>\d+)\.\s*(?P<title>.+?)\s*$")


@dataclass
class Task:
    id: int
    title: str
    checked: bool
    line_no: int

    @property
    def issue_title(self) -> str:
        return f"[Task {self.id}] {self.title}"


def load_token() -> Optional[str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_RO")
    if token:
        return token.strip()
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


def gh_request(
        method: str, url: str, token: str, body: Optional[dict] = None
) -> Tuple[int, dict, Dict[str, str]]:
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "eternia-sync-tasks/1.0")
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            status = resp.getcode()
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            headers = {k.lower(): v for k, v in resp.getheaders()}
            return status, parsed, headers
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
        msg = f"HTTP {e.code} {method} {url}: {detail}"
        print(f"[sync_tasks] {msg}", file=sys.stderr)
        return e.code, {"error": detail}, {}
    except urllib.error.URLError as e:
        print(f"[sync_tasks] Network error for {method} {url}: {e}", file=sys.stderr)
        return 0, {"error": str(e)}, {}


def gh_get(url: str, token: str) -> Tuple[int, dict, Dict[str, str]]:
    return gh_request("GET", url, token)


def gh_post(url: str, token: str, body: dict) -> Tuple[int, dict, Dict[str, str]]:
    return gh_request("POST", url, token, body)


def gh_patch(url: str, token: str, body: dict) -> Tuple[int, dict, Dict[str, str]]:
    return gh_request("PATCH", url, token, body)


def parse_tasks_md(path: Path) -> List[Task]:
    if not path.exists():
        print(f"[sync_tasks] Missing tasks file: {path}", file=sys.stderr)
        sys.exit(4)
    tasks: List[Task] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = TASK_RE.match(line.strip())
        if not m:
            continue
        checked = m.group("mark").lower() == "x"
        try:
            task_id = int(m.group("id"))
        except ValueError:
            continue
        title = m.group("title").strip()
        tasks.append(Task(id=task_id, title=title, checked=checked, line_no=i))
    return tasks


def list_repo_issues_all(
        owner: str, repo: str, token: str, limit_scan: int = 300
) -> List[dict]:
    results: List[dict] = []
    page = 1
    per_page = 100
    while len(results) < limit_scan:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues?{urlencode({'state': 'all', 'per_page': per_page, 'page': page, 'direction': 'desc', 'sort': 'created'})}"
        status, data, _ = gh_get(url, token)
        if status != 200:
            raise RuntimeError(
                f"GitHub API error listing issues: status={status} data={data}"
            )
        batch = data if isinstance(data, list) else []
        if not batch:
            break
        results.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return results[:limit_scan]


def ensure_labels(current: List[str], required: Iterable[str]) -> List[str]:
    s = {x for x in (current or [])}
    for r in required:
        if r:
            s.add(r)
    return sorted(s)


def remove_labels(current: List[str], to_remove: Iterable[str]) -> List[str]:
    s = {x for x in (current or [])}
    for r in to_remove:
        s.discard(r)
    return sorted(s)


@dataclass
class Action:
    kind: str  # 'create' | 'reopen' | 'close' | 'update-labels' | 'noop'
    task: Task
    issue_number: Optional[int] = None
    details: str = ""
    new_labels: Optional[List[str]] = None


def plan_actions(
        tasks: List[Task],
        issues: List[dict],
        label_todo: str,
        label_done: str,
        label_extra: Optional[str],
        only_ids: Optional[set[int]],
) -> List[Action]:
    # Build index by task id from issues by matching title prefix
    by_id: Dict[int, dict] = {}
    for it in issues:
        title = it.get("title") or ""
        m = re.match(r"\[Task\s+(\d+)\]\s+", title)
        if not m:
            continue
        try:
            tid = int(m.group(1))
        except ValueError:
            continue
        # Keep the most recent open issue preferentially
        prev = by_id.get(tid)
        if prev is None:
            by_id[tid] = it
        else:
            # Prefer open over closed; if both open, smaller number
            open_prev = prev.get("state") == "open"
            open_new = it.get("state") == "open"
            if open_new and not open_prev:
                by_id[tid] = it
            elif open_new == open_prev and (
                    it.get("number", 0) < prev.get("number", 0)
            ):
                by_id[tid] = it

    actions: List[Action] = []
    for t in tasks:
        if only_ids and t.id not in only_ids:
            continue
        issue = by_id.get(t.id)
        if not t.checked:
            # Desired: open issue with Todos (+ extra) labels
            desired_labels = [label_todo]
            if label_extra:
                desired_labels.append(label_extra)
            if issue is None:
                actions.append(
                    Action(
                        "create",
                        t,
                        details="create new open issue with Todo label",
                        new_labels=desired_labels,
                    )
                )
                continue
            # Issue exists
            is_open = issue.get("state") == "open"
            current_labels = sorted(
                [
                    lbl.get("name")
                    for lbl in issue.get("labels", [])
                    if isinstance(lbl, dict)
                ]
            )
            target_labels = ensure_labels(
                remove_labels(current_labels, [label_done]), desired_labels
            )
            if not is_open:
                actions.append(
                    Action(
                        "reopen",
                        t,
                        issue_number=issue.get("number"),
                        details="reopen and set Todo label",
                        new_labels=target_labels,
                    )
                )
            elif current_labels != target_labels:
                actions.append(
                    Action(
                        "update-labels",
                        t,
                        issue_number=issue.get("number"),
                        details="set Todo (+extra) labels",
                        new_labels=target_labels,
                    )
                )
            else:
                actions.append(
                    Action(
                        "noop",
                        t,
                        issue_number=issue.get("number"),
                        details="already open with desired labels",
                    )
                )
        else:
            # Checked: desired closed with Done (+ extra) labels
            desired_labels = [label_done]
            if label_extra:
                desired_labels.append(label_extra)
            if issue is None:
                actions.append(
                    Action("noop", t, details="no issue found; nothing to close")
                )
                continue
            is_open = issue.get("state") == "open"
            current_labels = sorted(
                [
                    lbl.get("name")
                    for lbl in issue.get("labels", [])
                    if isinstance(lbl, dict)
                ]
            )
            target_labels = ensure_labels(
                remove_labels(current_labels, [label_todo]), desired_labels
            )
            if is_open:
                actions.append(
                    Action(
                        "close",
                        t,
                        issue_number=issue.get("number"),
                        details="close and set Done label",
                        new_labels=target_labels,
                    )
                )
            elif current_labels != target_labels:
                actions.append(
                    Action(
                        "update-labels",
                        t,
                        issue_number=issue.get("number"),
                        details="adjust labels on closed issue",
                        new_labels=target_labels,
                    )
                )
            else:
                actions.append(
                    Action(
                        "noop",
                        t,
                        issue_number=issue.get("number"),
                        details="already closed with desired labels",
                    )
                )
    return actions


def execute_actions(owner: str, repo: str, token: str, actions: List[Action]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for a in actions:
        if a.kind == "noop":
            print(f"- NOOP Task {a.task.id}: {a.details}")
            continue
        if a.kind == "create":
            body = {
                "title": a.task.issue_title,
                "body": f"Source: docs/tasks.md (line {a.task.line_no})\n\nState: TODO\n\nThis issue is tracked from the project task list.",
                "labels": a.new_labels or [],
            }
            url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
            status, data, _ = gh_post(url, token, body)
            if status in (200, 201):
                print(f"- CREATE Task {a.task.id}: issue #{data.get('number')} created")
            else:
                print(f"! CREATE Task {a.task.id} FAILED: status={status} body={data}")
            continue
        if a.kind in ("reopen", "close", "update-labels"):
            patch: Dict[str, object] = {}
            if a.kind == "reopen":
                patch["state"] = "open"
            if a.kind == "close":
                patch["state"] = "closed"
            if a.new_labels is not None:
                patch["labels"] = a.new_labels
            url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{a.issue_number}"
            status, data, _ = gh_patch(url, token, patch)
            if status == 200:
                print(
                    f"- {a.kind.upper()} Task {a.task.id}: issue #{a.issue_number} {a.details}"
                )
                # If closing, add a comment noting completion time
                if a.kind == "close":
                    comment = {
                        "body": f"Closed via tasks.md (line {a.task.line_no}) at {now}."
                    }
                    c_url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{a.issue_number}/comments"
                    c_status, c_data, _ = gh_post(c_url, token, comment)
                    if c_status not in (200, 201):
                        print(
                            f"! COMMENT Task {a.task.id} on issue #{a.issue_number} FAILED: status={c_status} body={c_data}"
                        )
            else:
                print(
                    f"! {a.kind.upper()} Task {a.task.id} FAILED on issue #{a.issue_number}: status={status} body={data}"
                )
            continue
        print(f"! Unknown action kind {a.kind} for Task {a.task.id}")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Sync docs/tasks.md checkboxes to GitHub issues (dry-run by default)"
    )
    p.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/name format, e.g., eternakk/eternia",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply the planned changes (create/reopen/close/update labels)",
    )
    p.add_argument(
        "--limit-scan",
        type=int,
        default=300,
        help="Max number of issues to scan from GitHub (state=all)",
    )
    p.add_argument(
        "--label-todo", default="Todo", help="Label to apply for unchecked tasks"
    )
    p.add_argument(
        "--label-done", default="Done", help="Label to apply for checked tasks"
    )
    p.add_argument(
        "--label-extra",
        default="tasks-md",
        help="Extra label to tag tasks synced from tasks.md (blank to disable)",
    )
    p.add_argument(
        "--only-ids",
        default="",
        help="Comma-separated list of task IDs to restrict sync to",
    )

    args = p.parse_args(argv)

    if "/" not in args.repo:
        print("[sync_tasks] --repo must be in owner/name format", file=sys.stderr)
        return 1
    owner, repo = args.repo.split("/", 1)

    token = load_token()
    if not token:
        print(
            "[sync_tasks] Missing GitHub token. Set GITHUB_TOKEN or GITHUB_TOKEN_RO, or add it to .junie/mcp/.env",
            file=sys.stderr,
        )
        return 2
    if len(token) < 20:
        print(
            "[sync_tasks] Warning: token looks short; you may get 401 Unauthorized.",
            file=sys.stderr,
        )

    tasks = parse_tasks_md(TASKS_MD)
    if not tasks:
        print(
            "[sync_tasks] No tasks parsed from docs/tasks.md. Ensure lines follow the pattern: [ ] 405. Title here",
            file=sys.stderr,
        )
        return 4

    only_ids: Optional[set[int]] = None
    if args.only_ids.strip():
        try:
            only_ids = {int(x.strip()) for x in args.only_ids.split(",") if x.strip()}
        except ValueError:
            print(
                "[sync_tasks] --only-ids must be a comma-separated list of integers",
                file=sys.stderr,
            )
            return 1

    try:
        issues = list_repo_issues_all(
            owner, repo, token, limit_scan=max(1, args.limit_scan)
        )
    except Exception as e:
        print(f"[sync_tasks] Failed to list issues: {e}", file=sys.stderr)
        return 3

    label_extra = args.label_extra.strip() or None
    actions = plan_actions(
        tasks, issues, args.label_todo, args.label_done, label_extra, only_ids
    )

    # Print plan summary
    create_n = sum(1 for a in actions if a.kind == "create")
    reopen_n = sum(1 for a in actions if a.kind == "reopen")
    close_n = sum(1 for a in actions if a.kind == "close")
    update_n = sum(1 for a in actions if a.kind == "update-labels")
    noop_n = sum(1 for a in actions if a.kind == "noop")
    print(
        f"[sync_tasks] Plan: create={create_n}, reopen={reopen_n}, close={close_n}, update-labels={update_n}, noop={noop_n}"
    )

    for a in actions:
        id_s = f"Task {a.task.id}"
        issue_s = f"issue #{a.issue_number}" if a.issue_number else "(no issue)"
        labels_s = f" labels={a.new_labels}" if a.new_labels is not None else ""
        print(f"  - {a.kind:13s} {id_s:>8s} -> {issue_s}: {a.details}{labels_s}")

    if not args.apply:
        print("[sync_tasks] Dry-run only. Re-run with --apply to execute.")
        return 0

    # Execute
    execute_actions(owner, repo, token, actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
