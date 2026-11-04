#!/usr/bin/env python3
"""Rebuild the entry lists from YYYY/MM/YYYY-MM-DD.md files. Run from anywhere.

Writes YYYY/MM/README.md for every month and the block between the markers in README.md.
Each entry's list line comes from the `summary:` field in its front matter.
Also writes entries.json, every YYYY-MM-DD.json newest first, which the blog reads at build time.
"""
import json, re
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
    lines = [f"# {month.parent.name}-{month.name}\n"]
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
structured = [json.loads(f.read_text(encoding="utf-8"))
              for f in sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/*-*-*.json"), reverse=True)]
(ROOT / "entries.json").write_text(json.dumps(structured, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{len(entries)} entries, {len(months)} months")
