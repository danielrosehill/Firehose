#!/usr/bin/env python3
"""Validate a YYYY-MM-DD.json entry and write its .md beside it. Format: FORMAT.md.

Usage: render_entry.py YYYY/MM/YYYY-MM-DD.json [...]
"""
import datetime as dt, json, sys
from pathlib import Path

SECTIONS = {"repos": "GitHub Repositories", "datasets": "Datasets", "models": "AI Models"}
NETWORKS = {"GitHub", "Hugging Face"}
TYPES = {
    "repos": {"Agent plugin", "MCP server", "Application", "Tool", "Website", "Documentation",
              "Prompt collection", "Evaluation", "Other"},
    "datasets": {"Training dataset", "Evaluation dataset", "Audio dataset", "Reference dataset", "Other"},
    "models": {"Fine-tuned model", "Quantised model", "Other"},
}


def check(e, path):
    day = dt.date.fromisoformat(e["date"])
    problems = [] if path.stem == e["date"] else [f"file name does not match date {e['date']}"]
    if not e.get("summary"):
        problems.append("missing summary")
    if not e.get("projects"):
        problems.append("no projects: a day with none gets no entry")
    for p in e.get("projects", []):
        label = p.get("name", "?")
        if p.get("section") not in SECTIONS:
            problems.append(f"{label}: bad section {p.get('section')!r}")
        elif p.get("type") not in TYPES[p["section"]]:
            problems.append(f"{label}: bad type {p.get('type')!r}")
        if p.get("network") not in NETWORKS:
            problems.append(f"{label}: bad network {p.get('network')!r}")
        if not str(p.get("url", "")).startswith("https://"):
            problems.append(f"{label}: bad url")
        if not p.get("description"):
            problems.append(f"{label}: missing description")
    return day, problems


def render(e, day):
    counts = {s: sum(p["section"] == s for p in e["projects"]) for s in SECTIONS}
    lines = ["---", f"date: {e['date']}", f"summary: {e['summary']}", f"scope: {e.get('scope', 'created')}",
             "counts: { " + ", ".join(f"{k}: {v}" for k, v in counts.items()) + " }", "---", "",
             f"# {day.day} {day:%B %Y}", "", e["summary"]]
    for section, title in SECTIONS.items():
        items = [p for p in e["projects"] if p["section"] == section]
        if items:
            lines += ["", f"## {title}", ""]
            lines += [f"- **[{p['name']}]({p['url']})** ({p['network']}, {p['type']}): {p['description']}" for p in items]
    return "\n".join(lines) + "\n"


failed = False
for arg in sys.argv[1:]:
    path = Path(arg)
    entry = json.loads(path.read_text(encoding="utf-8"))
    day, problems = check(entry, path)
    if problems:
        failed = True
        print(f"{path}: " + "; ".join(problems), file=sys.stderr)
        continue
    path.with_suffix(".md").write_text(render(entry, day), encoding="utf-8")
    print(f"rendered {path.with_suffix('.md')}")
sys.exit(1 if failed else 0)
