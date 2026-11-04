#!/usr/bin/env python3
"""Validate a YYYY-MM-DD.json entry, sort its projects in place and write its .md beside it.
Format: FORMAT.md.

Usage: render_entry.py YYYY/MM/YYYY-MM-DD.json [...]
"""
import datetime as dt, json, sys
from pathlib import Path

SECTIONS = {"repos": "GitHub Repositories", "datasets": "Datasets", "models": "AI Models"}
NOUNS = {"repos": "repo", "datasets": "dataset", "models": "model"}
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
    if not e.get("intro"):
        problems.append("missing intro")
    if not e.get("projects"):
        problems.append("no projects: a day with none gets no entry")
    for p in e.get("projects", []):
        label = p.get("name", "?")
        if "-" in label or "_" in label:
            problems.append(f"{label}: name is not normalised")
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


def templated_summary(e, day):
    parts = []
    for section, noun in NOUNS.items():
        n = sum(p["section"] == section for p in e["projects"])
        if n:
            parts.append(f"{n} {noun}{'' if n == 1 else 's'}")
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"Public projects created on {day.day} {day:%B %Y}: {listed}."


def render(e, day):
    counts = {s: sum(p["section"] == s for p in e["projects"]) for s in SECTIONS}
    lines = ["---", f"date: {e['date']}", f"summary: {e['summary']}", f"scope: {e.get('scope', 'created')}",
             "counts: { " + ", ".join(f"{k}: {v}" for k, v in counts.items()) + " }", "---", "",
             f"# {day.day} {day:%B %Y}", "", e["intro"]]
    for section, title in SECTIONS.items():
        items = [p for p in e["projects"] if p["section"] == section]
        if items:
            noun = NOUNS[section] + ("" if len(items) == 1 else "s")
            lines += ["", f"## {title}", "", f"{len(items)} {noun} created", ""]
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
    entry["projects"].sort(key=lambda p: (list(SECTIONS).index(p["section"]), p["name"].casefold()))
    ordered = {"date": entry["date"], "summary": templated_summary(entry, day), "intro": entry["intro"],
               "scope": entry.get("scope", "created"), "projects": entry["projects"]}
    entry = ordered
    path.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    path.with_suffix(".md").write_text(render(entry, day), encoding="utf-8")
    print(f"rendered {path.with_suffix('.md')}")
sys.exit(1 if failed else 0)
