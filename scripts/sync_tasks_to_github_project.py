#!/usr/bin/env python3
"""
Sync markdown checkbox tasks from docs/tasks.md and docs/quantum_tasks.md to a GitHub Project (Projects v2).

Features:
- Parses markdown checkboxes from the specified files.
- Finds a user/org project by title (default: "eterniakk").
- Upserts Draft Issues in the project with the task title.
- Sets the Status single-select field to "To do" or "Done" based on [ ] vs [x].
- Idempotent by matching existing Draft Issue titles.

Configuration via environment variables:
- GH_TOKEN: GitHub token with access to Projects v2 (read/write) [required]
- GH_OWNER: The user/org login that owns the Project [required]
- GH_OWNER_TYPE: "user" or "org" (how to search the project) [required]
- GH_PROJECT_TITLE: Project title to match (default: eterniakk)
- GH_STATUS_TODO: Status option name for todo (default: To do)
- GH_STATUS_DONE: Status option name for done (default: Done)
- FILES: Comma-separated list of markdown files to parse (default: docs/tasks.md,docs/quantum_tasks.md)
- DRY_RUN: If "1" or "true", do not perform write operations (default: 0)

Usage:
  python scripts/sync_tasks_to_github_project.py

Note:
- The default GitHub Actions GITHUB_TOKEN typically lacks permission to modify user-level Projects v2.
  Use a Personal Access Token (classic) with project:write or the fine-grained equivalent and store it as GH_TOKEN secret.
"""
from __future__ import annotations

import os
import re
import sys
import json
from typing import Dict, List, Tuple, Optional

import httpx

GQL_ENDPOINT = "https://api.github.com/graphql"

TASK_LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?\[( |x|X)\]\s*(.+)$")
SKIP_TITLES = {"pending", "done", "in progress"}


def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_markdown_tasks(paths: List[str]) -> List[Tuple[str, bool]]:
    """Return list of (title, done) from given markdown files."""
    results: List[Tuple[str, bool]] = []
    for path in paths:
        if not os.path.exists(path):
            print(f"[warn] File not found: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = TASK_LINE_RE.match(line)
                if not m:
                    continue
                done = m.group(1).lower() == "x"
                title = m.group(2).strip()
                # Normalize title: remove trailing periods/spaces
                title = re.sub(r"\s+", " ", title).strip()
                # Skip legend/examples
                if title.lower() in SKIP_TITLES:
                    continue
                # Some lines may include markdown numbering like "51. Do X"
                # Keep as-is to preserve user intent.
                results.append((title, done))
    return results


def gql(client: httpx.Client, query: str, variables: Dict) -> Dict:
    r = client.post(GQL_ENDPOINT, json={"query": query, "variables": variables})
    r.raise_for_status()
    data = r.json()
    if "errors" in data and data["errors"]:
        # Surface GraphQL errors
        raise RuntimeError(f"GraphQL error: {json.dumps(data['errors'], indent=2)}")
    return data["data"]


def get_project_and_fields(client: httpx.Client, owner: str, owner_type: str, project_title: str) -> Tuple[str, Dict, Dict[str, str]]:
    """
    Return (projectId, status_field, status_options_map)
    - status_field: dict with id and name
    - status_options_map: name(lower)->optionId
    """
    if owner_type.lower() == "user":
        query = """
        query($login: String!) {
          user(login: $login) {
            projectsV2(first: 50) {
              nodes { id title number
                fields(first: 50) {
                  nodes {
                    ... on ProjectV2FieldCommon { id name dataType }
                    ... on ProjectV2SingleSelectField { id name dataType options { id name } }
                  }
                }
              }
            }
          }
        }
        """
        data = gql(client, query, {"login": owner})
        nodes = data["user"]["projectsV2"]["nodes"]
    elif owner_type.lower() in {"org", "organization"}:
        query = """
        query($login: String!) {
          organization(login: $login) {
            projectsV2(first: 50) {
              nodes { id title number
                fields(first: 50) {
                  nodes {
                    ... on ProjectV2FieldCommon { id name dataType }
                    ... on ProjectV2SingleSelectField { id name dataType options { id name } }
                  }
                }
              }
            }
          }
        }
        """
        data = gql(client, query, {"login": owner})
        nodes = data["organization"]["projectsV2"]["nodes"]
    else:
        raise SystemExit("GH_OWNER_TYPE must be 'user' or 'org'")

    # Choose project by title if provided and found; otherwise fall back to the first available project
    project = None
    title_norm = (project_title or "").strip().lower()
    if title_norm:
        for n in nodes:
            if n.get("title", "").strip().lower() == title_norm:
                project = n
                break
    if not project:
        if nodes:
            project = nodes[0]
            print(f"[info] Project titled '{project_title}' not found or not provided; defaulting to first project: '{project.get('title')}' (# {project.get('number')}).")
        else:
            raise SystemExit(f"No Projects v2 found under {owner_type} '{owner}'.")

    # Find Status field and option map
    status_field = None
    status_options: Dict[str, str] = {}
    for f in project["fields"]["nodes"]:
        if f.get("dataType") == "SINGLE_SELECT" and f.get("name", "").lower() in {"status", "state"}:
            status_field = f
            for opt in f.get("options", []) or []:
                status_options[opt["name"].strip().lower()] = opt["id"]
            break

    if not status_field:
        raise SystemExit("Could not find a 'Status' single-select field in the project.")

    return project["id"], status_field, status_options


def get_project_items_by_title(client: httpx.Client, project_id: str) -> Dict[str, str]:
    """Return mapping of existing draft item titles (lower) -> itemId.
    Note: We only match Draft Issues by title to avoid clashing with repo issues/PRs.
    """
    query = """
    query($projectId: ID!, $first: Int!, $after: String) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: $first, after: $after) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              content {
                __typename
                ... on DraftIssue { id title }
                ... on Issue { id title }
                ... on PullRequest { id title }
              }
            }
          }
        }
      }
    }
    """
    result: Dict[str, str] = {}
    after: Optional[str] = None
    while True:
        data = gql(client, query, {"projectId": project_id, "first": 100, "after": after})
        items = data["node"]["items"]
        for node in items["nodes"]:
            content = node.get("content")
            if content and content.get("__typename") == "DraftIssue":
                title = content.get("title", "").strip().lower()
                if title:
                    result[title] = node["id"]
        if not items["pageInfo"]["hasNextPage"]:
            break
        after = items["pageInfo"]["endCursor"]
    return result


def add_draft_item(client: httpx.Client, project_id: str, title: str, body: str = "") -> str:
    mutation = """
    mutation($projectId: ID!, $title: String!, $body: String) {
      addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
        projectItem { id }
      }
    }
    """
    data = gql(client, mutation, {"projectId": project_id, "title": title, "body": body})
    return data["addProjectV2DraftIssue"]["projectItem"]["id"]


def set_status(client: httpx.Client, project_id: str, item_id: str, field_id: str, option_id: str) -> None:
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) { projectV2Item { id } }
    }
    """
    gql(client, mutation, {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "optionId": option_id,
    })


def main() -> int:
    token = os.getenv("GH_TOKEN")
    owner = os.getenv("GH_OWNER")
    owner_type = os.getenv("GH_OWNER_TYPE")
    project_title = os.getenv("GH_PROJECT_TITLE", "eterniakk")
    status_todo = os.getenv("GH_STATUS_TODO", "To do").strip().lower()
    status_done = os.getenv("GH_STATUS_DONE", "Done").strip().lower()
    files = os.getenv("FILES", "docs/tasks.md,docs/quantum_tasks.md").split(",")
    files = [p.strip() for p in files if p.strip()]
    dry_run = env_bool("DRY_RUN", False)

    if not token or not owner or not owner_type:
        if env_bool("DRY_RUN", False):
            print("[dry-run] GH_TOKEN/GH_OWNER/GH_OWNER_TYPE not set; proceeding without network calls.")
        else:
            print("error: GH_TOKEN, GH_OWNER, GH_OWNER_TYPE are required in env.")
            return 2

    tasks = parse_markdown_tasks(files)
    # De-duplicate by title (keep last occurrence)
    task_map: Dict[str, bool] = {}
    for title, done in tasks:
        task_map[title] = done

    if not task_map:
        print("No tasks found to sync.")
        return 0

    # If DRY_RUN, avoid any network calls and only print the plan
    if dry_run:
        todos = [t for t, d in task_map.items() if not d]
        dones = [t for t, d in task_map.items() if d]
        print("[dry-run] Parsed tasks from:")
        for p in files:
            print(f"  - {p}")
        print(f"[dry-run] Would set {len(dones)} tasks to Done and {len(todos)} to To do")
        if dones:
            print("[dry-run] Done tasks:")
            for t in dones:
                print(f"  - {t}")
        if todos:
            print("[dry-run] To do tasks:")
            for t in todos:
                print(f"  - {t}")
        return 0

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    with httpx.Client(headers=headers, timeout=30) as client:
        project_id, status_field, status_options = get_project_and_fields(client, owner, owner_type, project_title)
        status_field_id = status_field["id"]

        # Find option ids
        todo_option = status_options.get(status_todo)
        done_option = status_options.get(status_done)
        if not todo_option or not done_option:
            print("error: Could not resolve Status options. Available:")
            for name, oid in status_options.items():
                print(f"  - {name}: {oid}")
            print(f"Expected names (lower): '{status_todo}' and '{status_done}'")
            return 3

        existing = get_project_items_by_title(client, project_id)

        created = 0
        updated = 0
        for title, done in task_map.items():
            desired_option = done_option if done else todo_option
            key = title.strip().lower()
            if key in existing:
                item_id = existing[key]
                print(f"[update] {title} -> {'Done' if done else 'To do'}")
                set_status(client, project_id, item_id, status_field_id, desired_option)
                updated += 1
            else:
                print(f"[create] {title} -> {'Done' if done else 'To do'}")
                item_id = add_draft_item(client, project_id, title)
                set_status(client, project_id, item_id, status_field_id, desired_option)
                created += 1

        print(f"Sync complete. Created: {created}, Updated: {updated}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
