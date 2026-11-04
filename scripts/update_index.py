#!/usr/bin/env python3
"""Rebuild the entry lists from YYYY/MM/YYYY-MM-DD.md files. Run from anywhere.

Writes YYYY/MM/README.md for every month and the block between the markers in README.md.
Each entry's list line comes from the `summary:` field in its front matter.
Also writes data.json (metrics by day and month, plus every YYYY-MM-DD.json newest first), which the blog
reads at build time, and a programmatic YYYY/MM/wrap-up.md per month: the days concatenated section by section.
"""
import datetime as dt, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN, END = "<!-- entries:begin -->", "<!-- entries:end -->"
LATEST = 14


def summary(path):
    m = re.search(r"^summary:\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip('"') if m else ""


entries = sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/*-*-*.md"), reverse=True)
months = {}
for e in entries:
    months.setdefault(e.parent, []).append(e)

for month, days in months.items():
    lines = [f"# {month.parent.name}-{month.name}\n", "[Wrap-up](wrap-up.md)\n"]
    lines += [f"- [{d.stem}]({d.name}): {summary(d)}" for d in days]
    (month / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

block = ["### Latest\n"]
block += [f"- [{e.stem}]({e.relative_to(ROOT).as_posix()}): {summary(e)}" for e in entries[:LATEST]]
block += ["\n### By month\n"]
block += [f"- [{m.parent.name}-{m.name}]({m.relative_to(ROOT).as_posix()}/README.md) ({len(d)} days)" for m, d in months.items()]
readme = ROOT / "README.md"
text = readme.read_text(encoding="utf-8")
new = text[: text.index(BEGIN) + len(BEGIN)] + "\n" + "\n".join(block) + "\n" + text[text.index(END):]
readme.write_text(new, encoding="utf-8")
SECTIONS = {"repos": ("GitHub Repositories", "repo"), "datasets": ("Datasets", "dataset"), "models": ("AI Models", "model")}
structured = [json.loads(f.read_text(encoding="utf-8"))
              for f in sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/*-*-*.json"), reverse=True)]


def tally(days):
    counts = {s: sum(p["section"] == s for e in days for p in e["projects"]) for s in SECTIONS}
    return {**counts, "total": sum(counts.values())}


by_month = {}
for e in structured:
    by_month.setdefault(e["date"][:7], []).append(e)
data = {
    "metrics": {
        "totals": {**tally(structured), "days": len(structured)},
        "by_month": [{"month": m, "days": len(d), **tally(d)} for m, d in sorted(by_month.items())],
        "by_day": [{"date": e["date"], **tally([e])} for e in reversed(structured)],
    },
    "entries": structured,
}
(ROOT / "data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

for month, days in by_month.items():
    label = dt.date.fromisoformat(month + "-01").strftime("%B %Y")
    t = tally(days)
    counts = ", ".join(f"{t[s]} {n}{'' if t[s] == 1 else 's'}" for s, (_, n) in SECTIONS.items() if t[s])
    lines = [f"# Firehose wrap-up for {label}", "", f"{counts} created across {len(days)} day{'' if len(days) == 1 else 's'}."]
    for section, (title, noun) in SECTIONS.items():
        if t[section]:
            lines += ["", f"## {title}", "", f"{t[section]} {noun}{'' if t[section] == 1 else 's'} created", ""]
            lines += [f"- {e['date']}: **[{p['name']}]({p['url']})** ({p['network']}, {p['type']}): {p['description']}"
                      for e in reversed(days) for p in e["projects"] if p["section"] == section]
    (ROOT / month[:4] / month[5:] / "wrap-up.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"{len(entries)} entries, {len(months)} months")
