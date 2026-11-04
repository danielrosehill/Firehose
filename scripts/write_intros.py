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
If there is one project, write a single sentence saying what it is. If there are several, write two or three plain sentences, 60 words at most, grouping them by subject.
Use only what the project list says. Do not list every name. With more than ten projects, name the main themes only, with no long lists: the 60-word limit is strict.
Open with the subject matter in your own words, never a stock phrase or the word "led", and say "repositories" only when there are several.
Never add a closing remark about what area the work sits in or what it centred on: stop when the projects are described.
No hype, no emojis, no dashes as punctuation. Do not mention the date or a person. Output only the paragraph.

Example with several projects:
Three agent plugins and a playbook for keeping cheap IP cameras local-only covered agent tooling and home network security. On Hugging Face, the new work was speech-recognition training material: a small model that writes read-aloud sentences, its training data, and a mixed English-Hebrew sentence dataset.

Example with one project:
A plot of how the maximum output token length of major language models has grown, as of February 2025."""


def intro(entry, model, key):
    lines = "\n".join(f"- [{p['section']}] {p['name']} ({p['type']}): {p['description']}" for p in entry["projects"])
    body = {"model": model, "temperature": 0.3, "max_tokens": 200, "reasoning": {"enabled": False},
            "usage": {"include": True}, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": lines}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.load(r)
    text = re.sub(r"\s+", " ", res["choices"][0]["message"]["content"] or "").strip()
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
