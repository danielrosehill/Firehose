#!/usr/bin/env python3
"""Fill the `intro` of every entry JSON that lacks one. This is the only AI step in Firehose.

One short call per day through OpenRouter, reasoning off. Needs OPENROUTER_API_KEY (run under
`with-secrets`). Prints measured cost. Standard library only.

Usage: write_intros.py [--model deepseek/deepseek-v4.1-flash] [--limit N] [--max-cost 0.25]
"""
import argparse, concurrent.futures as cf, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = """You write the lead paragraph for a dated log of public software projects.
Write two or three plain sentences, 60 words at most, saying what was created and across which areas.
Group the projects by subject; do not list every name. Use only what the project list says.
No hype, no emojis, no dashes as punctuation. Do not mention the date or a person. Output only the paragraph.

Example of the style:
New repositories covered agent tooling and home network security, with three agent plugins and a playbook for keeping cheap IP cameras local-only. On Hugging Face, the new work was speech-recognition training material: a small model that writes read-aloud sentences, its training data, and a mixed English-Hebrew sentence dataset."""


def intro(entry, model, key):
    lines = "\n".join(f"- [{p['section']}] {p['name']} ({p['type']}): {p['description']}" for p in entry["projects"])
    body = {"model": model, "temperature": 0.3, "max_tokens": 200, "reasoning": {"enabled": False},
            "usage": {"include": True}, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": lines}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.load(r)
    text = re.sub(r"\s+", " ", res["choices"][0]["message"]["content"]).strip()
    return text, res.get("usage", {}).get("cost", 0) or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek/deepseek-v4.1-flash")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-cost", type=float, default=0.25)
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY not set: run under with-secrets")
    todo = []
    for f in sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/*-*-*.json"), reverse=True):
        e = json.loads(f.read_text(encoding="utf-8"))
        if not e.get("intro"):
            todo.append((f, e))
    todo = todo[: a.limit] if a.limit else todo
    spent = failed = done = 0
    with cf.ThreadPoolExecutor(6) as pool:
        jobs = {pool.submit(intro, e, a.model, key): (f, e) for f, e in todo}
        for job in cf.as_completed(jobs):
            f, e = jobs[job]
            try:
                text, cost = job.result()
            except Exception as err:
                failed += 1
                print(f"{f.name}: {err}", file=sys.stderr)
                continue
            spent += cost
            if not text:
                failed += 1
                print(f"{f.name}: empty reply", file=sys.stderr)
                continue
            e["intro"] = text
            f.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            done += 1
            if spent > a.max_cost:
                for j in jobs:
                    j.cancel()
                print(f"stopped at cost cap ${a.max_cost}", file=sys.stderr)
                break
    print(json.dumps({"written": done, "failed": failed, "cost_usd": round(spent, 5), "model": a.model}))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
