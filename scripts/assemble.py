#!/usr/bin/env python3
"""Build Firehose entry JSON for a date range from public metadata. No AI involved.

Lists public GitHub repos and public, ungated Hugging Face models and datasets, groups them by
creation day in --tz, and writes YYYY/MM/YYYY-MM-DD.json with everything except `intro`
(scripts/write_intros.py fills that). Days already holding a .json or .md are skipped unless
--force, so hand-written entries survive. Format: FORMAT.md. Standard library only.

Usage: assemble.py --from YYYY-MM-DD --to YYYY-MM-DD [--tz Asia/Jerusalem] [--force] [--dry-run]
"""
import argparse, base64, datetime as dt, json, os, re, subprocess, sys
import urllib.error, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OWNER = "danielrosehill"
EXCLUDE = {"danielrosehill/Firehose"}
MAX_DESC = 200
NO_DESC = "No description published."
CASING = {w.lower(): w for w in """AI API ASR CLI GGUF GPT GPU HF IoT IP LLM LLMs LoRA MCP NLP OCR OS PDF RAG RTL STT TTS UI URL VPS
    ChatGPT GitHub OpenAI OpenRouter HuggingFace YouTube""".split()}


def token():
    if os.environ.get("GH_TOKEN"):
        return os.environ["GH_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "firehose-assemble", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def normalise(machine_name):
    words = []
    for w in re.split(r"[-_\s]+", machine_name):
        if not w:
            continue
        if w.lower() in CASING:
            words.append(CASING[w.lower()])
        elif re.fullmatch(r"\d+(\.\d+)?[bm]", w, re.I):
            words.append(w.upper())
        elif w != w.lower():
            words.append(w)  # already has capitals: keep them
        else:
            words.append(w[0].upper() + w[1:])
    return " ".join(words)


def shorten(text):
    """Whole sentences up to MAX_DESC characters, else cut at a word."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= MAX_DESC:
        return text
    kept = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if len(kept) + len(sentence) + 1 > MAX_DESC:
            break
        kept = f"{kept} {sentence}".strip()
    return kept or text[:MAX_DESC].rsplit(" ", 1)[0] + "..."


def first_paragraph(markdown):
    """First prose paragraph of a README or model card, with Markdown stripped."""
    text = re.sub(r"\A---\n.*?\n---\n", "", markdown, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para or para[0] in "#|>!<-*[" and not para.startswith("**"):
            continue
        if re.match(r"\*\*[^*]{1,40}:?\*\*:?", para) and len(para) < 200 and "http" in para:
            continue  # a "**Write-up:** [link]" line
        para = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", para)
        para = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
        para = re.sub(r"[`*]", "", para).strip()
        if len(para) >= 30:
            return para
    return ""


def repo_type(r):
    name = r["name"].lower()
    text = f"{name} {(r.get('description') or '').lower()}"
    if re.search(r"\bplugin|skills?\b", text):
        return "Agent plugin"
    if "mcp" in name:
        return "MCP server"
    if re.search(r"prompts?\b", name):
        return "Prompt collection"
    if re.search(r"eval|benchmark", name):
        return "Evaluation"
    if re.search(r"(^|-)(site|website|blog|portal)(-|$)", name):
        return "Website"
    if re.search(r"(^|-)app(-|$)", name):
        return "Application"
    return "Tool" if r.get("language") and r["language"] != "HTML" else "Documentation"


def dataset_type(m, desc):
    text = " ".join(m.get("tags", [])).lower() + " " + m["id"].lower() + " " + desc.lower()
    if re.search(r"modality:audio|audio|speech-dataset", text):
        return "Audio dataset"
    if re.search(r"eval|benchmark", text):
        return "Evaluation dataset"
    return "Training dataset" if re.search(r"task_categories:|train|fine-tun", text) else "Reference dataset"


def model_type(m):
    # Judge quantisation from the repo name: tags like gguf or onnx also appear on full-weight repos.
    if re.search(r"gguf|gptq|awq|quant|mlx|ct2|int8|[48]bit", m["id"].lower()):
        return "Quantised model"
    return "Fine-tuned model" if any(t.startswith("base_model:") for t in m.get("tags", [])) else "Other"


def github_projects(day_of, wanted, tok, problems):
    h = {"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {tok}"} if tok else {})}
    out, page = {}, 1
    while True:
        repos = json.loads(fetch(f"https://api.github.com/users/{OWNER}/repos?type=owner&per_page=100&page={page}", h))
        if not repos:
            return out
        for r in repos:
            day = day_of(r["created_at"])
            if day not in wanted or r["private"] or r["fork"] or r["full_name"] in EXCLUDE:
                continue
            desc = r.get("description") or ""
            if not desc:
                try:
                    raw = json.loads(fetch(f"https://api.github.com/repos/{r['full_name']}/readme", h))
                    desc = first_paragraph(base64.b64decode(raw["content"]).decode("utf-8", "replace"))
                except urllib.error.HTTPError as e:
                    if e.code != 404:
                        problems.append(f"readme {r['full_name']}: HTTP {e.code}")
            out.setdefault(day, []).append({
                "name": normalise(r["name"]), "url": r["html_url"], "network": "GitHub", "section": "repos",
                "type": repo_type(r), "description": shorten(desc) or NO_DESC})
        page += 1


def hf_projects(kind, day_of, wanted, out, problems):
    prefix = "datasets/" if kind == "datasets" else ""
    for m in json.loads(fetch(f"https://huggingface.co/api/{kind}?author={OWNER}&limit=1000&full=true")):
        if m.get("private") or m.get("gated") not in (False, None) or not m.get("createdAt"):
            continue
        day = day_of(m["createdAt"])
        if day not in wanted:
            continue
        try:
            desc = first_paragraph(fetch(f"https://huggingface.co/{prefix}{m['id']}/raw/main/README.md").decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            desc = ""
            if e.code != 404:
                problems.append(f"card {m['id']}: HTTP {e.code}")
        out.setdefault(day, []).append({
            "name": normalise(m["id"].split("/", 1)[1]), "url": f"https://huggingface.co/{prefix}{m['id']}",
            "network": "Hugging Face", "section": kind,
            "type": dataset_type(m, desc) if kind == "datasets" else model_type(m),
            "description": shorten(desc) or NO_DESC})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end", required=True)
    ap.add_argument("--tz", default="Asia/Jerusalem")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tz = ZoneInfo(a.tz)
    start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    wanted = {(start + dt.timedelta(days=i)).isoformat() for i in range((end - start).days + 1)}

    def day_of(ts):
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz).date().isoformat()

    problems = []
    days = github_projects(day_of, wanted, token(), problems)
    hf_projects("datasets", day_of, wanted, days, problems)
    hf_projects("models", day_of, wanted, days, problems)
    if problems:  # a failed source must never read as a quiet day
        sys.exit("aborting, nothing written:\n" + "\n".join(problems))

    written = skipped = 0
    for day, projects in sorted(days.items()):
        path = ROOT / day[:4] / day[5:7] / f"{day}.json"
        entry = {"date": day, "scope": "created", "projects": projects}
        if a.dry_run:
            print(json.dumps(entry, indent=1, ensure_ascii=False))
            continue
        if not a.force and (path.exists() or path.with_suffix(".md").exists()):
            skipped += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
    missing = sum(p["description"] == NO_DESC for ps in days.values() for p in ps)
    print(f"{len(days)} days, {sum(map(len, days.values()))} projects, {written} written, {skipped} skipped, "
          f"{missing} without a description", file=sys.stderr)


if __name__ == "__main__":
    main()
