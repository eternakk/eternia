"""Command-line utilities for orchestrating Eternia agent flows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

STORY_DOC_PATH = Path("docs/implementation_stories.md")
ISSUE_MAP_PATH = Path("docs/issue_story_map.json")


@dataclass
class Story:
    """Represents a single implementation story and its metadata."""

    code: str
    title: str
    epic: str
    tasks: List[str]


@dataclass
class DryRunReport:
    """Structured view of the dry-run output."""

    issue: str
    story: Optional[Story]
    pipeline_steps: List[str]
    guardrails: List[str]
    validation_steps: List[str]
    references: List[str]
    warnings: List[str]

    def to_lines(self) -> List[str]:
        lines: List[str] = []
        lines.append("=== Eternia Agent Flow Dry Run ===")
        lines.append(f"Issue: {self.issue}")
        if self.story:
            lines.append(f"Story: {self.story.title} ({self.story.code})")
            lines.append(f"Epic: {self.story.epic}")
            if self.story.tasks:
                lines.append("Tasks:")
                for item in self.story.tasks:
                    lines.append(f"  - {item}")
        else:
            lines.append("Story: <unknown>")

        if self.pipeline_steps:
            lines.append("Pipeline Sequence:")
            for idx, step in enumerate(self.pipeline_steps, start=1):
                lines.append(f"  {idx}. {step}")

        if self.guardrails:
            lines.append("Operational Guardrails:")
            for item in self.guardrails:
                lines.append(f"  - {item}")

        if self.validation_steps:
            lines.append("Validation Hooks:")
            for item in self.validation_steps:
                lines.append(f"  - {item}")

        if self.references:
            lines.append("Reference Material:")
            for item in self.references:
                lines.append(f"  - {item}")

        if self.warnings:
            lines.append("Warnings:")
            for item in self.warnings:
                lines.append(f"  - {item}")

        return lines


DEFAULT_PIPELINE = [
    "Planner drafts plan.md with acceptance criteria and risk notes",
    "Test Author stages or updates automated tests before code changes",
    "Implementer applies planned diffs within whitelisted directories",
    "Automated test suite executes via agents/tools/run_tests.py",
    "UI smoke and optional perf checks run via CI dispatch",
    "Reviewer posts rubric score and actionable feedback",
    "Security Sentry reviews findings and patches or blocks as needed",
    "Doc Scribe updates documentation and demo scripts",
]

DEFAULT_GUARDRAILS = [
    "Respect repo-level red-mode and needs-human-review labels",
    "Validate diffs with git_ops and reject oversized or unsafe patches",
    "Keep secrets limited to config/mcp/.env.example allow-list",
    "Call Alignment Governor APIs through approved clients and honor vetoes",
    "Apply privacy scrubbing when handling transcripts or analytics",
]

DEFAULT_VALIDATIONS = [
    "PyTest / unit suites via agents/tools/run_tests.py",
    "Optional UI smoke suite via agents/tools/run_ui.py",
    "Metrics and log spot-check after implementation",
    "Escalate anomalies with alignment:review issue if needed",
]

REFERENCE_DOCS = [
    "agents.md",
    "docs/agentic_orchestration_plan.md",
    "docs/pending_implementation_design.md",
    "docs/implementation_stories.md",
]


def parse_arguments(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orchestrate Eternia agent flows. Only dry-run mode is currently supported."
    )
    parser.add_argument("issue", help="Issue identifier (number or slug)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the agent pipeline without making network or git calls.",
    )
    parser.add_argument(
        "--story",
        help="Override story code or title if the automatic lookup cannot resolve it.",
    )
    parser.add_argument(
        "--issue-map",
        default=str(ISSUE_MAP_PATH),
        help="Path to the issue-to-story mapping JSON file.",
    )
    parser.add_argument(
        "--stories-doc",
        default=str(STORY_DOC_PATH),
        help="Path to the implementation stories markdown document.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def load_issue_story_map(map_path: Path) -> dict[str, dict[str, str]]:
    if not map_path.exists():
        return {}
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
        return {
            str(key): {
                "code": str(value.get("code", "")),
                "title": str(value.get("title", "")),
            }
            for key, value in data.items()
        }
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse issue map at {map_path}: {exc}") from exc


def parse_stories(doc_path: Path) -> dict[str, Story]:
    if not doc_path.exists():
        raise FileNotFoundError(f"Story document not found: {doc_path}")

    stories: dict[str, Story] = {}
    current_epic = ""
    current_story: Optional[Story] = None

    story_heading_pattern = re.compile(r"^### Story\s+(?P<code>[A-Z]\d+)\s+–\s+(?P<title>.+)$")

    for raw_line in doc_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("## Epic"):
            current_epic = line.replace("##", "").strip()
            current_story = None
            continue

        match = story_heading_pattern.match(line)
        if match:
            code = match.group("code")
            title = match.group("title").strip()
            current_story = Story(code=code, title=f"Story {code} – {title}", epic=current_epic, tasks=[])
            stories[code] = current_story
            continue

        if current_story and line.startswith("- "):
            current_story.tasks.append(line[2:].strip())
            continue

        if line.startswith("### "):
            current_story = None

    return stories


def match_story(candidates: dict[str, Story], query: str) -> Optional[Story]:
    lowered = query.lower()
    # Exact code match
    if query.upper() in candidates:
        return candidates[query.upper()]

    for story in candidates.values():
        if story.title.lower() == lowered:
            return story
    for story in candidates.values():
        if lowered in story.title.lower():
            return story
    return None


def resolve_story(
    issue: str,
    story_override: Optional[str],
    issue_map: dict[str, dict[str, str]],
    stories: dict[str, Story],
    warnings: List[str],
) -> Optional[Story]:
    if story_override:
        story = match_story(stories, story_override)
        if story:
            return story
        warnings.append(f"Story override '{story_override}' did not match any known stories.")

    normalized_issue = issue.lstrip("#")
    mapping = issue_map.get(normalized_issue)
    if not mapping:
        warnings.append(
            "Issue not found in docs/issue_story_map.json; specify --story to override lookup."
        )
        return None

    if mapping.get("code"):
        story = match_story(stories, mapping["code"])
        if story:
            return story

    if mapping.get("title"):
        story = match_story(stories, mapping["title"])
        if story:
            return story

    warnings.append(
        f"Issue {issue} is mapped but story '{mapping}' could not be located in implementation stories."
    )
    return None


def build_report(args: argparse.Namespace) -> DryRunReport:
    issue_map_path = Path(args.issue_map)
    stories_doc_path = Path(args.stories_doc)

    issue_map = load_issue_story_map(issue_map_path)
    stories = parse_stories(stories_doc_path)

    warnings: List[str] = []
    story = resolve_story(args.issue, args.story, issue_map, stories, warnings)

    return DryRunReport(
        issue=args.issue,
        story=story,
        pipeline_steps=list(DEFAULT_PIPELINE),
        guardrails=list(DEFAULT_GUARDRAILS),
        validation_steps=list(DEFAULT_VALIDATIONS),
        references=list(REFERENCE_DOCS),
        warnings=warnings,
    )


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_arguments(argv)

    if not args.dry_run:
        print("Only --dry-run mode is currently implemented.", file=sys.stderr)
        return 2

    try:
        report = build_report(args)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for line in report.to_lines():
        print(line)

    if report.story is None:
        return 3

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
