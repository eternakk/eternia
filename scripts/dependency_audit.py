#!/usr/bin/env python3
"""
Dependency audit script for Eternia.
- Audits Python dependencies (requirements.txt) with pip-audit.
- Audits UI (ui/package.json) with npm audit and npm outdated.
- Queries PyPI for latest versions of pinned Python requirements and classifies update types.
- Generates dependency-audit-<YYYY-MM-DD>.md in repo root.

This script tries to avoid installing project dependencies; it only queries registries/APIs.
Requires: pip-audit, Node/npm in PATH, internet access for PyPI and npm registry.
"""
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = REPO_ROOT / "requirements.txt"
UI_DIR = REPO_ROOT / "ui"
DATE_STR = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = REPO_ROOT / f"dependency-audit-{DATE_STR}.md"


def run(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDERR:\n{proc.stderr}")
    return proc.returncode, proc.stdout, proc.stderr


def read_requirements(path: Path) -> List[Tuple[str, Optional[str]]]:
    reqs: List[Tuple[str, Optional[str]]] = []
    pattern = re.compile(r"^([A-Za-z0-9_.\-]+)\s*(==\s*([A-Za-z0-9_.\-]+))?\s*(#.*)?$")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = pattern.match(line)
        if not m:
            # Unparseable; store raw name
            name = re.split(r"[<>=! ]", line)[0]
            reqs.append((name, None))
            continue
        name = m.group(1)
        ver = m.group(3)
        reqs.append((name, ver))
    return reqs


def py_latest_version(package: str) -> Optional[str]:
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
            return data.get("info", {}).get("version")
    except Exception:
        return None


def version_tuple(v: str) -> Tuple[int, ...]:
    # Strip post/dev/rc tags and convert to ints best-effort
    v = re.sub(r"[+\-].*$", "", v)  # remove build metadata/suffixes
    v = re.sub(r"(rc|a|b|post|dev)\d*$", "", v)
    parts = []
    for p in v.split('.'):
        m = re.match(r"(\d+)", p)
        parts.append(int(m.group(1)) if m else 0)
    # Normalize length to 3
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def classify_update(current: str, latest: str) -> str:
    c = version_tuple(current)
    l = version_tuple(latest)
    if l <= c:
        return "none"
    if l[0] != c[0]:
        return "major"
    if l[1] != c[1]:
        return "minor"
    return "patch"


def audit_python() -> Dict:
    result: Dict = {"vulns": [], "updates": []}
    # Vulnerabilities via pip-audit
    try:
        _, out_json, _ = run(["pip-audit", "-r", str(REQ_FILE), "-f", "json"])
        # pip-audit may print a non-JSON preface; extract the JSON payload robustly
        json_start = out_json.find("{")
        json_end = out_json.rfind("}")
        payload = out_json[json_start:json_end+1] if json_start != -1 and json_end != -1 else out_json
        data = json.loads(payload)
        for dep in data.get("dependencies", []):
            vulns = dep.get("vulns", [])
            for v in vulns:
                result["vulns"].append({
                    "package": dep.get("name"),
                    "version": dep.get("version"),
                    "id": v.get("id"),
                    "aliases": v.get("aliases", []),
                    "fix_versions": v.get("fix_versions", []),
                    "severity": None,  # pip-audit JSON doesn't include severity consistently
                })
    except Exception as e:
        result["vulns_error"] = str(e)

    # Available updates: compare pinned versions to latest
    for name, ver in read_requirements(REQ_FILE):
        latest = py_latest_version(name)
        if ver and latest:
            update_type = classify_update(ver, latest)
            if update_type != "none":
                result["updates"].append({
                    "package": name,
                    "current": ver,
                    "latest": latest,
                    "update_type": update_type,
                })
        elif not ver:
            result["updates"].append({
                "package": name,
                "current": "unconstrained",
                "latest": latest or "unknown",
                "update_type": "unbounded",
            })
    return result


def audit_ui() -> Dict:
    result: Dict = {"vulns": [], "updates": []}
    if not UI_DIR.exists():
        result["error"] = "ui/ directory not found"
        return result
    # npm audit
    try:
        _, out, _ = run(["npm", "audit", "--json"], cwd=UI_DIR)
        if not out.strip():
            # Fallback to text output if JSON is empty (older npm)
            _, out, _ = run(["npm", "audit"], cwd=UI_DIR)
        audit = json.loads(out) if out.strip().startswith('{') else {"vulnerabilities": {}}
        vulns = audit.get("vulnerabilities", {})
        for name, v in vulns.items():
            via = v.get("via", [])
            ids = []
            ranges = set()
            for item in via:
                if isinstance(item, dict):
                    ids.append({
                        "id": item.get("url", "").split("/")[-1],  # GHSA id from URL
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "range": item.get("range"),
                    })
                    if item.get("range"):
                        ranges.add(item["range"]) 
            result["vulns"].append({
                "package": name,
                "severity": v.get("severity"),
                "isDirect": v.get("isDirect"),
                "fixAvailable": v.get("fixAvailable"),
                "nodes": v.get("nodes", []),
                "ids": ids,
                "range": v.get("range") or ", ".join(sorted(ranges)),
            })
        result["ui_audit_metadata"] = audit.get("metadata", {})
    except Exception as e:
        result["vulns_error"] = str(e)

    # npm outdated
    try:
        _, out, _ = run(["npm", "outdated", "--json"], cwd=UI_DIR)
        if out.strip():
            outdated = json.loads(out)
        else:
            # Fallback to table output
            _, out, _ = run(["npm", "outdated"], cwd=UI_DIR)
            outdated = {}
            for line in out.splitlines():
                # Package  Current  Wanted  Latest ...
                if not line or line.lower().startswith("package"):
                    continue
                cols = [c for c in line.split(" ") if c]
                if len(cols) >= 4:
                    pkg, current, wanted, latest = cols[0], cols[1], cols[2], cols[3]
                    outdated[pkg] = {"current": current, "wanted": wanted, "latest": latest}
        for pkg, info in outdated.items():
            current = info.get("current")
            wanted = info.get("wanted")
            latest = info.get("latest")
            # Classify update to wanted (within range) vs latest (may be major)
            wanted_type = classify_update(current, wanted) if current and wanted else "none"
            latest_type = classify_update(current, latest) if current and latest else "none"
            result["updates"].append({
                "package": pkg,
                "current": current,
                "wanted": wanted,
                "latest": latest,
                "wanted_type": wanted_type,
                "latest_type": latest_type,
            })
    except Exception as e:
        result["updates_error"] = str(e)

    return result


def generate_report(py: Dict, ui: Dict) -> str:
    lines: List[str] = []
    lines.append(f"# Dependency Audit — {DATE_STR}")
    lines.append("")
    lines.append("This report summarizes dependency vulnerabilities and available updates across Python (pip) and UI (npm) package managers. Majors are batched/skipped with notes about potential breaking changes.")
    lines.append("")

    # Python vulnerabilities
    lines.append("## Python (requirements.txt)")
    if py.get("vulns"):
        lines.append("")
        lines.append("### Vulnerabilities")
        lines.append("")
        lines.append("- Source: pip-audit")
        lines.append("")
        lines.append("| Package | Current | Vulnerability ID | Aliases | Severity | Fixed Versions |")
        lines.append("|---|---:|---|---|---:|---|")
        for v in py["vulns"]:
            aliases = ", ".join(v.get("aliases") or [])
            fixes = ", ".join(v.get("fix_versions") or [])
            lines.append(f"| {v['package']} | {v['version']} | {v['id']} | {aliases} | {v.get('severity') or 'N/A'} | {fixes} |")
    else:
        lines.append("")
        lines.append("No known vulnerabilities found by pip-audit.")

    # Python updates
    lines.append("")
    lines.append("### Available updates (Python)")
    py_updates = py.get("updates", [])
    if py_updates:
        lines.append("")
        lines.append("- Patch/minor updates:")
        lines.append("")
        lines.append("| Package | Current | Latest | Update Type |")
        lines.append("|---|---:|---:|---|")
        for u in sorted(py_updates, key=lambda x: (x["package"].lower())):
            if u["update_type"] in {"patch", "minor"}:
                lines.append(f"| {u['package']} | {u['current']} | {u['latest']} | {u['update_type']} |")
        lines.append("")
        lines.append("- Majors or unbounded (batched/skipped):")
        lines.append("")
        lines.append("| Package | Current | Latest | Note |")
        lines.append("|---|---:|---:|---|")
        for u in sorted(py_updates, key=lambda x: (x["package"].lower())):
            if u["update_type"] in {"major", "unbounded"}:
                note = "Potential breaking changes; review release notes before upgrading."
                if u["update_type"] == "unbounded":
                    note = "Unpinned requirement; consider pinning to a stable version."
                lines.append(f"| {u['package']} | {u['current']} | {u['latest']} | {note} |")
    else:
        lines.append("")
        lines.append("No update information available.")

    # UI vulnerabilities
    lines.append("")
    lines.append("## UI (ui/package.json)")
    if ui.get("vulns"):
        lines.append("")
        lines.append("### Vulnerabilities")
        lines.append("")
        lines.append("- Source: npm audit")
        lines.append("")
        lines.append("| Package | Severity | Direct | Vulnerability IDs | Affected Range | Fix Available |")
        lines.append("|---|---:|:---:|---|---|:---:|")
        for v in ui["vulns"]:
            ids = ", ".join([i.get("id", "") for i in v.get("ids", []) if i.get("id")]) or "(see advisory)"
            lines.append(f"| {v['package']} | {v.get('severity') or ''} | {'yes' if v.get('isDirect') else 'no'} | {ids} | {v.get('range') or ''} | {'yes' if v.get('fixAvailable') else 'no'} |")
    else:
        lines.append("")
        lines.append("No known vulnerabilities found by npm audit.")

    # UI updates
    lines.append("")
    lines.append("### Available updates (UI)")
    ui_updates = ui.get("updates", [])
    if ui_updates:
        lines.append("")
        lines.append("- Patch/minor updates (safe to apply where tests pass):")
        lines.append("")
        lines.append("| Package | Current | Wanted | Update Type |")
        lines.append("|---|---:|---:|---|")
        for u in sorted(ui_updates, key=lambda x: x["package"].lower()):
            if u["wanted_type"] in {"patch", "minor"}:
                lines.append(f"| {u['package']} | {u['current']} | {u['wanted']} | {u['wanted_type']} |")
        lines.append("")
        lines.append("- Majors (batched/skipped):")
        lines.append("")
        lines.append("| Package | Current | Latest | Note |")
        lines.append("|---|---:|---:|---|")
        for u in sorted(ui_updates, key=lambda x: x["package"].lower()):
            if u["latest_type"] == "major":
                note = "Major upgrade may introduce breaking changes; consult migration guides."
                lines.append(f"| {u['package']} | {u['current']} | {u['latest']} | {note} |")
    else:
        lines.append("")
        lines.append("No update information available.")

    # Next steps prompt
    lines.append("")
    lines.append("## Next steps")
    lines.append("")
    lines.append("- Would you like me to apply the listed patch/minor updates and run the test suites (pytest, Vitest, Cypress) to verify? If all tests pass, I can open a PR with the changes. Majors will be left for a separate migration plan.")

    return "\n".join(lines) + "\n"


def main() -> int:
    py = audit_python()
    ui = audit_ui()
    report = generate_report(py, ui)
    OUT_FILE.write_text(report)
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
